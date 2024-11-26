#!/bin/bash

set -e

# Настраиваем cron задачу
echo "* * * * * root python manage.py update_expired_auctions" > /etc/cron.d/auction_cron
chmod 0644 /etc/cron.d/auction_cron
service cron start

sleep 2
# Выполняем миграцию базы данных
python manage.py migrate
python manage.py collectstatic --no-input
cp -r /app/collected_static/. /backend_static/static/
cp -r /app/static/. /backend_static/static/

# Запускаем сервер Django
gunicorn --bind 0.0.0.0:8000 website.wsgi