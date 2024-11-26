FROM python:3.10-slim-buster

WORKDIR /app

# Установка необходимых пакетов
RUN apt-get update && \
    apt-get install -y cron

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем скрипт запуска
COPY docker-cron.sh /usr/local/bin/docker-cron.sh
RUN chmod +x /usr/local/bin/docker-cron.sh

# Запускаем приложение
CMD ["/usr/local/bin/docker-cron.sh"]