#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "=========================================================="
echo "  FIUBA - Sistema de Planificaciones & Bibliografía"
echo "=========================================================="

# 1. Asegurar contenedor PostgreSQL
if ! docker ps --format '{{.Names}}' | grep -q "^pg-material-estudio$"; then
    if docker ps -a --format '{{.Names}}' | grep -q "^pg-material-estudio$"; then
        echo "--> Iniciando contenedor PostgreSQL (pg-material-estudio)..."
        docker start pg-material-estudio
    else
        echo "--> Creando contenedor PostgreSQL..."
        docker run -d --name pg-material-estudio \
            -e POSTGRES_USER=postgres \
            -e POSTGRES_PASSWORD=postgres \
            -e POSTGRES_DB=material_estudio \
            -p 5432:5432 \
            -v pgdata_material_estudio:/var/lib/postgresql/data \
            --restart unless-stopped \
            postgres:16-alpine
        sleep 2
        docker exec -i pg-material-estudio psql -U postgres -d material_estudio < "$DIR/schema.sql"
        docker exec -i pg-material-estudio psql -U postgres -d material_estudio < "$DIR/seed_data.sql"
    fi
else
    echo "✓ Contenedor PostgreSQL activo en puerto 5432"
fi

# 2. Iniciar servidor frontend Astro
echo "--> Iniciando frontend Astro en http://localhost:4321..."
cd "$DIR/frontend"
npm run dev -- --host 127.0.0.1 --port 4321
