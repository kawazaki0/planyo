#!/bin/sh


postgres_ready() {
python << END
import sys

import psycopg2

try:
    psycopg2.connect(
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${POSTGRES_HOST}",
        port="${POSTGRES_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
}
until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'


python manage.py migrate
python manage.py collectstatic --noinput

/usr/local/bin/gunicorn --timeout 1800 planyo.wsgi --bind 0.0.0.0:8001 --chdir=/app # --certfile=/certs/fullchain.pem --keyfile=/certs/privkey.pem
