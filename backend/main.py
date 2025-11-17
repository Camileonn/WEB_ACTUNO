import datetime
import time
import logging
from fastapi import FastAPI
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import PlainTextResponse

# -------------------------------
# CONFIGURAR LOGGING → LOKI
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s — %(message)s"
)

logger = logging.getLogger("calculadora")

# -------------------------------
# CONFIGURAR PROMETHEUS
# -------------------------------
REQUEST_COUNT = Counter(
    "operation_total",
    "Número de operaciones realizadas",
    ["operation", "status"]
)

REQUEST_LATENCY = Histogram(
    "operation_duration_ms",
    "Duración en milisegundos",
    ["operation"]
)

# -------------------------------
# FASTAPI
# -------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# MONGO
# -------------------------------
try:
    client = MongoClient("mongodb://admin_user:web3@mongo:27017/")
    database = client.practica1
    collection_historial = database.historial
    logger.info("Mongo conectado correctamente")
except Exception as e:
    logger.error(f"Error al conectar a Mongo: {e}")


# -------------------------------
# MÉTRICAS PROMETHEUS
# -------------------------------
@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type="text/plain")


# -------------------------------
# FUNCIONES DE OPERACIONES
# -------------------------------

def operate(a, b, op_name, operation_func):
    start = time.time()

    try:
        # Validación ejemplo
        if op_name == "division" and b == 0:
            raise ValueError("No se puede dividir entre cero.")

        result = operation_func(a, b)

        # Guardar en Mongo
        document = {
            "a": a,
            "b": b,
            "operation": op_name,
            "result": result,
            "date": datetime.datetime.now(tz=datetime.timezone.utc)
        }
        collection_historial.insert_one(document)

        # Log success
        logger.info(f"Operación {op_name} exitosa: {a} y {b}")

        # Métricas Prometheus
        REQUEST_COUNT.labels(operation=op_name, status="success").inc()
        REQUEST_LATENCY.labels(operation=op_name).observe((time.time() - start) * 1000)

        return {"a": a, "b": b, "resultado": result}

    except Exception as e:
        logger.error(f"Error en operación {op_name}: {e}")
        REQUEST_COUNT.labels(operation=op_name, status="error").inc()
        raise e


@app.get("/calculator/sum")
def sum_numbers(a: float, b: float):
    return operate(a, b, "suma", lambda x, y: x + y)


@app.get("/calculator/rest")
def rest_numbers(a: float, b: float):
    return operate(a, b, "resta", lambda x, y: x - y)


@app.get("/calculator/multiply")
def multiply_numbers(a: float, b: float):
    return operate(a, b, "multiplicacion", lambda x, y: x * y)


@app.get("/calculator/divide")
def divide_numbers(a: float, b: float):
    return operate(a, b, "division", lambda x, y: x / y)


# -------------------------------
# HISTORIAL
# -------------------------------
@app.get("/calculator/history")
def obtain_history():
    try:
        records = collection_historial.find().sort("date", -1).limit(10)

        history = []
        for record in records:
            history.append({
                "a": record.get("a"),
                "b": record.get("b"),
                "operation": record.get("operation"),
                "result": record.get("result"),
                "date": record["date"].isoformat()
            })

        logger.info("Historial consultado correctamente")
        REQUEST_COUNT.labels(operation="historial", status="success").inc()
        return {"history": history}

    except Exception as e:
        logger.error("Error al consultar historial: " + str(e))
        REQUEST_COUNT.labels(operation="historial", status="error").inc()
        raise e

