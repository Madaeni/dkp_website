#!/bin/bash

set -e

sleep 2

# Миграция баз данных
python manage.py migrate

# Сбор статики
python manage.py collectstatic --no-input

# Копирование статических файлов
cp -r /app/collected_static/. /backend_static/static/
cp -r /app/static/. /backend_static/static/

# Запуск gunicorn
gunicorn --bind 0.0.0.0:8000 website.wsgi