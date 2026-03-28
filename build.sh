#!/usr/bin/env bash

echo "Starting build..."

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate

echo "Build completed!"