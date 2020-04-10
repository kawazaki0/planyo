FROM python:3.12

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY planyo /app/planyo
COPY manage.py /app/
WORKDIR /app

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

EXPOSE 8001
ENTRYPOINT ["/entrypoint.sh"]
