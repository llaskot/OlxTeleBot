# Используйте базовый образ с поддержкой Python
FROM python

# Установите рабочую директорию в контейнере
WORKDIR /app

# Создайте и активируйте виртуальное окружение
RUN python3 -m venv venv

# Скопируйте файл requirements.txt и установите зависимости
COPY requirements.txt .
RUN . venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Запустите ваше приложение
CMD ["venv/bin/python3", "code/main.py"]
