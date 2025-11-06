import os
import sys
import re
import json
import time
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
import psycopg2

# --- Fuerza a usar UTF-8 en todo Python ---
if sys.getdefaultencoding().lower() != 'utf-8':
    try:
        os.system('chcp 65001 >NUL')  # cambia la página de códigos a UTF-8 (solo Windows)
    except Exception:
        pass
    os.environ["PYTHONIOENCODING"] = "utf-8"

# === Configuración de la DB ===
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "clinc150")
DB_USER = os.getenv("DB_USER", "user")
DB_PASS = os.getenv("DB_PASS", "password")

# === Configuración de KAGGLE (NUEVO) ===
KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
KAGGLE_KEY = os.getenv("KAGGLE_KEY")

# === Función para limpiar texto ===
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# === Descargar dataset CLINC150 ===
download_dir = "datasets/clinc150"
os.makedirs(download_dir, exist_ok=True)

api = KaggleApi()

# --- MODIFICACIÓN CLAVE PARA AUTENTICACIÓN DOCKER ---
if KAGGLE_USERNAME and KAGGLE_KEY:
    # Si las variables de entorno están presentes, usarlas para autenticar
    os.environ['KAGGLE_USERNAME'] = KAGGLE_USERNAME
    os.environ['KAGGLE_KEY'] = KAGGLE_KEY
    print("Autenticando Kaggle usando KAGGLE_USERNAME y KAGGLE_KEY del entorno...")
    api.authenticate()
else:
    # Intentar la autenticación automática (útil para desarrollo local, fallará en Docker sin volumen)
    print("Autenticando Kaggle automáticamente (¡Asegúrese de configurar KAGGLE_USERNAME/KEY en Docker!)")
    api.authenticate() 
# ----------------------------------------------------

print("Descargando dataset CLINC150 desde Kaggle...")
try:
    api.dataset_download_files("hongtrung/clinc150-dataset", path=download_dir, unzip=True)
    print("Dataset descargado correctamente.")
except Exception as e:
    print(f"❌ Error al descargar el dataset. Revise sus credenciales de Kaggle. Error: {e}")
    sys.exit(1)


# === Leer SOLO data_small.json ===
data_path = os.path.join(download_dir, "data", "data_small.json")
print(f"Cargando {data_path} ...")

with open(data_path, "r", encoding="utf-8") as f:
    CLINC150 = json.load(f)

train_data = pd.DataFrame(CLINC150["train"], columns=["text", "intent"])
val_data = pd.DataFrame(CLINC150["val"], columns=["text", "intent"])
test_data = pd.DataFrame(CLINC150["test"], columns=["text", "intent"])

df = pd.concat([train_data, val_data, test_data], ignore_index=True)
print(f"✅ Total muestras cargadas: {len(df)}")

# === Limpieza ===
df["clean_text"] = df["text"].apply(clean_text)

# === Esperar que DB esté lista ===
print("Esperando conexión a la base de datos...")
time.sleep(15) 

# === Conexión a PostgreSQL ===
try:
    print(f"Conectando a PostgreSQL en {DB_HOST}:{DB_PORT}...")
    conn = psycopg2.connect(
        f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASS}"
    )
    cur = conn.cursor()
    print("✅ Conexión exitosa a la base de datos.")

    # === Ejecutar init.sql si existe ===
    init_path = os.path.join(os.getcwd(), "init.sql")
    if os.path.exists(init_path):
        print(f"Ejecutando {init_path} ...")
        with open(init_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
        cur.execute(sql_script)
        conn.commit()
        print("✅ Tabla creada o verificada correctamente.")
    else:
        print("⚠️ No se encontró init.sql; se asume que la tabla ya existe.")

except Exception as e:
    print("❌ Error al conectar o inicializar la base de datos:")
    print(e)
    sys.exit(1)

# === Insertar registros ===
print("Insertando datos en PostgreSQL...")
for _, row in df.iterrows():
    cur.execute(
        """
        INSERT INTO clinc150 (text, clean_text, intent)
        VALUES (%s, %s, %s)
        """,
        (row["text"], row["clean_text"], row["intent"]),
    )

conn.commit()
cur.close()
conn.close()
print("🎉 Carga completada correctamente (data_small.json).")