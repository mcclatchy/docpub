#!/bin/bash

# variables
APP_NAME="DocPub"
ENV_NAME="docpub"
PYTHON_LOCATION="/home/ubuntu/Envs/docpub/bin/python3"
PROJECT_DIR="/home/ubuntu/docpub/docpub"
REQ_LOCATION="/home/ubuntu/docpub/docpub/requirements.txt"

echo "Deploying " $APP_NAME

# steps
echo ""
echo "STEP 1: change into the docpub directory..."
cd $PROJECT_DIR

echo ""
echo "STEP 2: invoke the virtualenv..."
workon $ENV_NAME

echo ""
echo "STEP 3: update the repo..."
git pull origin master

echo ""
echo "STEP 4: install/re-install required packages..."
pip3 install -r $REQ_LOCATION

echo ""
echo "STEP 5: migrate if needed for any new modules..."
$PYTHON_LOCATION manage.py migrate

echo ""
echo "STEP 6: make any necessary migrations..."
$PYTHON_LOCATION manage.py makemigrations

echo ""
echo "STEP 7: migrate if needed for database migrations..."
$PYTHON_LOCATION manage.py migrate

echo ""
echo "STEP 8: restart uwsgi..."
sudo systemctl restart uwsgi