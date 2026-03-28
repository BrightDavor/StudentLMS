<<<<<<< HEAD
# Create a proper build.sh file
@'
#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed!"
'@ | Out-File -FilePath build.sh -Encoding UTF8
=======
#!/usr/bin/env bash

echo "Starting build..."

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate

echo "Build completed!"
>>>>>>> 2a65adf (Clean project (no large files))
