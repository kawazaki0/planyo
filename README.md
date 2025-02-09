# Planyo integration

## Prerequisites

The application requires:
- Docker
- docker-compose

## Setup

### Docker

To run all on production:

    docker compose up -d 

It will create two containers. First with postgres database and second
with django server on gunicorn. Database data is stored on a docker volume,
therefore it is persistent.

### Local

If you want to run django server without docker and with sqlite database,
you need to setup environment like this:

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd planyo
    ./manage.py migrate
    ./manage.py runserver

    DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --username admin --email 'admin@admin.pl' --noinput

### Deployment on VPS

    rsync --progress -az --exclude='.git' --exclude='.venv' --exclude='__pycache__' . vps:/home/debian/planyo
    docker compose up -d --build
    docker exec -e DJANGO_SETTINGS_MODULE=settings.prod -it planyo-django-1 python manage.py createsuperuser
