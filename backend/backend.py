from flask import Flask, jsonify, request
import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

app = Flask(__name__)
from flask_cors import CORS
# 🚨 CORRECCIÓN: Permitir explícitamente peticiones desde cualquier origen ('*')
CORS(app, resources={r"/*": {"origins": "*"}})


# Conexión a PostgreSQL
def get_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )

@app.route('/')
def index():
    return jsonify({"message": "API CLINC150 (data_small.json) funcionando"})


# 🔹 1. Obtener todos los intents
@app.route('/api/intents', methods=['GET'])
def get_intents():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT intent FROM clinc150 ORDER BY intent;")
    intents = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(intents)


# 🔹 2. Obtener ejemplos de un intent específico
@app.route('/api/examples/<intent>', methods=['GET'])
def get_examples(intent):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT text, clean_text FROM clinc150 WHERE intent = %s LIMIT 20;",
        (intent,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"text": r[0], "clean_text": r[1]} for r in rows])


# 🔹 3. Buscar textos que contengan una palabra clave
@app.route('/api/search', methods=['GET'])
def search_text():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT text, intent FROM clinc150 WHERE clean_text ILIKE %s LIMIT 30;",
        (f"%{query}%",)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"text": r[0], "intent": r[1]} for r in rows])


# 🔹 4. Contar cuántas frases hay por intent
@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT intent, COUNT(*) FROM clinc150 GROUP BY intent ORDER BY intent;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"intent": r[0], "count": r[1]} for r in rows])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
