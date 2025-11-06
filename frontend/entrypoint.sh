#!/bin/sh

# La ruta es solo "/api", ya que Nginx se encargará del proxy interno.
# Esto hace que el navegador pida la URL a su propio dominio (p.e., /api/intents)
find /usr/share/nginx/html -name '*.js' | xargs sed -i "s|__API_PLACEHOLDER__|\/api|g"

# Iniciar Nginx
exec nginx -g 'daemon off;'