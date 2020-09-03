#! /usr/bin/env bash
cd /app
python manage.py makemigrations
sleep 2
python manage.py migrate --no-input
sleep 2
python manage.py collectstatic --no-input
sleep 2
