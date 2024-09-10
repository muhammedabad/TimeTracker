#!/bin/bash

DEFAULT_PORT=${POSTGRES_DB_PORT:=5432}

until nc -z ${POSTGRES_DB_HOST} ${POSTGRES_DB_PORT}; do
    echo "$(date) - waiting for postgres ($POSTGRES_DB_HOST: $POSTGRES_DB_PORT)..."
    sleep 1
done

# Migrations
echo "Running Django migrations"
python manage.py migrate

# Static Content
echo "Running Django Static content generation"
python manage.py collectstatic --no-input

# Start app
echo "Start up application"
#uvicorn muhammed_abad.asgi:application --host 0.0.0.0 --port 8200 --reload
python manage.py runserver 0.0.0.0:8200