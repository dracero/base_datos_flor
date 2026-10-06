#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Verificar si el contenedor pg-material-estudio está corriendo
if ! docker ps --format '{{.Names}}' | grep -q "^pg-material-estudio$"; then
    if docker ps -a --format '{{.Names}}' | grep -q "^pg-material-estudio$"; then
        echo "--> [Docker] Levantando contenedor PostgreSQL (pg-material-estudio)..."
        docker start pg-material-estudio
    else
        echo "--> [Docker] Creando contenedor PostgreSQL con base de datos..."
        docker run -d --name pg-material-estudio \
            -e POSTGRES_USER=postgres \
            -e POSTGRES_PASSWORD=postgres \
            -e POSTGRES_DB=material_estudio \
            -p 5432:5432 \
            -v pgdata_material_estudio:/var/lib/postgresql/data \
            --restart unless-stopped \
            postgres:16-alpine
        sleep 2
        until docker exec -i pg-material-estudio pg_isready -U postgres -d material_estudio >/dev/null 2>&1; do
            sleep 1
        done
        docker exec -i pg-material-estudio psql -U postgres -d material_estudio < "$DIR/schema.sql"
        docker exec -i pg-material-estudio psql -U postgres -d material_estudio < "$DIR/seed_data.sql"
    fi

    # Esperar hasta que esté listo para aceptar queries
    until docker exec -i pg-material-estudio pg_isready -U postgres -d material_estudio >/dev/null 2>&1; do
        sleep 1
    done
    echo "✓ PostgreSQL listo y escuchando en puerto 5432"
else
    echo "✓ PostgreSQL ya está activo en puerto 5432"
fi
