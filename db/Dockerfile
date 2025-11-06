# db/Dockerfile

FROM python:3.10-slim

WORKDIR /app

COPY requirements_db.txt .

# 🚨 CAMBIO CLAVE: Usar el flag --upgrade --no-cache-dir y, opcionalmente, --force-reinstall
# Esto garantiza que todas las dependencias se instalen de nuevo para la arquitectura actual.
RUN pip install --no-cache-dir --upgrade --force-reinstall -r requirements_db.txt

COPY init.sql .
COPY download_and_load.py .

CMD ["python", "download_and_load.py"]