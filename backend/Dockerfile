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

# Запускаем приложение
RUN chmod +x docker-cron.sh
CMD ["bash", "docker-cron.sh"]