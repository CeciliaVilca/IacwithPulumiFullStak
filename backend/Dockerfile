# backend/Dockerfile

# Usar una imagen base de Python ligera (slim)
FROM python:3.10-slim

# Establecer variables de entorno para la codificación
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP backend.py

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 1. Copiar el archivo de requisitos e instalar dependencias
# Esto ayuda a aprovechar el cache de Docker si solo cambia el código
COPY requirements.txt .
# Instalar las dependencias de Python (flask, psycopg2-binary)
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copiar el resto del código de la aplicación
# Copiar el backend.py y config.py al directorio de trabajo /app
COPY . .

# 3. Exponer el puerto que usa Flask (5000)
# (Esto no publica el puerto, solo documenta el puerto que usa el contenedor)
EXPOSE 5000

# 4. Comando para correr la aplicación Flask
# Usamos '0.0.0.0' en el host para asegurar que sea accesible desde afuera del contenedor
CMD ["python", "backend.py"]