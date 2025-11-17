import { useState, useEffect } from "react";

function App() {
    const [a, setA] = useState("");
    const [b, setB] = useState("");
    const [resultado, setResultado] = useState(null);
    const [historial, setHistorial] = useState([]);

    const API = "http://localhost:8089";

    const llamarOperacion = async (endpoint) => {
        if (a === "" || b === "") {
            alert("Ingresa ambos números");
            return;
        }

        const res = await fetch(`${API}/calculator/${endpoint}?a=${a}&b=${b}`);
        const data = await res.json();
        setResultado(data.resultado);
        obtenerHistorial();
    };

    const obtenerHistorial = async () => {
        const res = await fetch(`${API}/calculator/history`);
        const data = await res.json();
        setHistorial(data.history);
    };

    useEffect(() => {
        obtenerHistorial();
    }, []);

    return (
        <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col items-center p-6">
            <div className="w-full max-w-md bg-gray-800 rounded-xl shadow-lg p-6">
                <h1 className="text-3xl font-bold text-center text-blue-400 mb-6">
                    Calculadora Avanzada
                </h1>

                {/* Inputs */}
                <div className="flex flex-col space-y-4">
                    <input
                        type="number"
                        value={a}
                        onChange={(e) => setA(e.target.value)}
                        placeholder="Número 1"
                        className="px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />

                    <input
                        type="number"
                        value={b}
                        onChange={(e) => setB(e.target.value)}
                        placeholder="Número 2"
                        className="px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />

                    {/* Botones de operaciones */}
                    <div className="grid grid-cols-2 gap-3">
                        <button
                            onClick={() => llamarOperacion("sum")}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg"
                        >
                            Sumar
                        </button>

                        <button
                            onClick={() => llamarOperacion("rest")}
                            className="bg-yellow-600 hover:bg-yellow-700 text-white font-semibold py-2 rounded-lg"
                        >
                            Restar
                        </button>

                        <button
                            onClick={() => llamarOperacion("multiply")}
                            className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-lg"
                        >
                            Multiplicar
                        </button>

                        <button
                            onClick={() => llamarOperacion("divide")}
                            className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 rounded-lg"
                        >
                            Dividir
                        </button>
                    </div>
                </div>

                {/* Resultado */}
                {resultado !== null && (
                    <h2 className="mt-6 text-xl font-semibold text-green-400 text-center">
                        Resultado: {resultado}
                    </h2>
                )}

                {/* Historial */}
                <div className="mt-8">
                    <h3 className="text-lg font-semibold text-gray-300 mb-3">Historial:</h3>
                    <ul className="space-y-2 max-h-48 overflow-y-auto">
                        {historial.map((op, i) => (
                            <li
                                key={i}
                                className="bg-gray-700 px-4 py-2 rounded-lg border border-gray-600 text-sm"
                            >
                                <span className="font-semibold text-blue-300">
                                    {op.operation.toUpperCase()}
                                </span>{" "}
                                → {op.a} y {op.b} ={" "}
                                <span className="text-green-400 font-bold">{op.result}</span>{" "}
                                <span className="text-gray-400 text-xs">( {op.date} )</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default App;

