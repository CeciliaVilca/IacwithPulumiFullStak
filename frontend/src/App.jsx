import { useEffect, useState } from "react";
// Usamos los nombres corregidos: getExamples y searchText
import { getIntents, getExamples, searchText } from "./api"; 
import SearchBar from "./components/SearchBar";
import IntentList from "./components/IntentList";

function App() {
  const [intents, setIntents] = useState([]);
  const [samples, setSamples] = useState([]);
  const [selectedIntent, setSelectedIntent] = useState("");
  const [query, setQuery] = useState("");

  // 1. Definición de la función de manejo
  const handleIntentSelect = (intentName) => {
    setQuery(""); // 👈 ¡CLAVE! Limpiar el estado de búsqueda
    setSelectedIntent(intentName);
    // Nota: El useEffect para selectedIntent se encargará de la llamada a la API
  };

  useEffect(() => {
    getIntents().then(setIntents);
  }, []);

  useEffect(() => {
    // Aquí se llama a la API de ejemplos cuando se selecciona un intent
    if (selectedIntent) getExamples(selectedIntent).then(setSamples);
  }, [selectedIntent]);

  useEffect(() => {
    // Aquí se llama a la API de búsqueda cuando se ingresa un query
    if (query.length > 1) searchText(query).then(setSamples);
  }, [query]);

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-4 text-center">💬 CLINC150 Explorer</h1>
      <SearchBar onSearch={setQuery} />

      {!selectedIntent && !query && (
        <>
          <h2 className="text-lg font-semibold mb-2 text-gray-700 text-center">
            Selecciona una intención
          </h2>
          {/* 2. Pasar la nueva función de manejo al IntentList */}
          <IntentList intents={intents} onSelect={handleIntentSelect} />
        </>
      )}

      {(selectedIntent || query) && (
        <div className="mt-4">
          <button
            className="mb-3 px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300"
            onClick={() => {
              setSelectedIntent("");
              setQuery("");
              setSamples([]);
            }}
          >
            ⬅ Volver
          </button>

          <h3 className="text-xl font-semibold mb-2">
            {/* 3. El título ahora será correcto: si query está vacío, mostrará "Ejemplos de..." */}
            {query ? `Resultados para "${query}"` : `Ejemplos de "${selectedIntent}"`}
          </h3>
          <ul className="bg-white rounded-md shadow p-4">
            {samples.length > 0 ? (
              samples.map((s, i) => (
                <li key={i} className="border-b py-2">{s.text}</li>
              ))
            ) : (
              <li className="text-gray-500 italic">Sin resultados...</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;