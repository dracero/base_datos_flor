#!/usr/bin/env bash
if [ -z "$1" ]; then
    docker exec -it pg-material-estudio psql -U postgres -d material_estudio
else
    docker exec -i pg-material-estudio psql -U postgres -d material_estudio -c "$1"
fi
