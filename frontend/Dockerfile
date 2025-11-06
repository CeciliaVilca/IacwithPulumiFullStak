FROM node:20-alpine as build 

# ...
WORKDIR /app

# 🚨 PASO 1: Copiar solo los archivos de dependencias
COPY package.json package-lock.json ./

# 🚨 PASO 2: Limpieza y reinstalación. Esto es CRÍTICO para los bindings musl/Alpine.
# Forzamos la instalación.
# RUN rm -rf package-lock.json node_modules
RUN npm install --legacy-peer-deps --unsafe-perm

# Copiar el código fuente (para que no interfiera con la instalación)
COPY . .

# Compilar la aplicación React/Vite
RUN npm run build

# ====================================================================
# FASE 2: SERVICIO (SERVE) - No necesita cambios
# ====================================================================
FROM nginx:alpine

# 1. Copiar el entrypoint.sh (Contiene saltos de línea de Windows)
COPY entrypoint.sh /docker-entrypoint.sh

# 2. 🚨 ¡FIX CRÍTICO! Usa sed para eliminar los caracteres \r (saltos de línea de DOS)
# Esto asegura que el script se ejecute correctamente en Alpine Linux.
RUN sed -i 's/\r$//' /docker-entrypoint.sh 

# 3. Dar permisos de ejecución
RUN chmod +x /docker-entrypoint.sh 

# 4. Eliminar la configuración predeterminada de Nginx
RUN rm /etc/nginx/conf.d/default.conf

# 5. Copiar un archivo de configuración de Nginx personalizado
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 6. Copiar los archivos de la aplicación compilados
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

# 7. Usar el script limpio como punto de entrada
ENTRYPOINT ["/docker-entrypoint.sh"]