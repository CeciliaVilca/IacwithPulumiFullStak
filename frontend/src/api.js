import axios from "axios";

// URL base de tu backend Flask
const API_URL = "/api";

// Obtener todos los intents disponibles
export async function getIntents() {
  try {
    // La URL resultante ahora será: http://127.0.0.1:5000/api/intents
    const res = await axios.get(`${API_URL}/intents`);
    return res.data;
  } catch (err) {
    console.error("Error al obtener intents:", err);
    return [];
  }
}

//Obtener ejemplos de un intent específico
 
export async function getExamples(intent) {
  try {
    const res = await axios.get(`${API_URL}/examples/${encodeURIComponent(intent)}`);
    return res.data;
  } catch (err) {
    console.error("Error al obtener ejemplos:", err);
    return [];
  }
}

// Buscar textos que contengan una palabra clave
export async function searchText(query) {
  try {
    const res = await axios.get(`${API_URL}/search`, { params: { q: query } });
    return res.data;
  } catch (err) {
    console.error("Error al buscar texto:", err);
    return [];
  }
}

//Obtener estadísticas de cantidad de frases por intent
export async function getStats() {
  try {
    const res = await axios.get(`${API_URL}/stats`);
    return res.data;
  } catch (err) {
    console.error("Error al obtener estadísticas:", err);
    return [];
  }
}
