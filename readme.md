
# Prerequisites

* Python 3.x (e.g. Python 3.5.1)
	* check your version by running `python3 --version`
* virtualenv
* virtualenvwrapper
* git
* sqlite

# Setup

## Local repo

Clone the repo

	git clone git@github.com:mcclatchy/docpub.git

## Virtualenv/virtualenvwrapper

Create an environment

	mkvirtualenv docpub

## Bash alias

Add this to your `bash_profile` (e.g. Mac) or `bash_rc` (e.g. Linux)

	alias='workon docpub && cd ~/path/to/docpub/docpub' 

## Requirements

Install the requirements 

	pip install -r requirements.txt

## Private settings

Create a private settings file

	vim ~/path/to/docpub/docpub/settings_private.py

Add your Django secret key and DocumentCloud credentials

	SECRET_KEY = ''
	DC_USERNAME = ''
	DC_PASSWORD = ''

## Test/prod server

Clone the repo

	git clone git@github.com:mcclatchy/docpub.git

# Dev work

## Local server

Start it 

	python3 manage.py runserver

If you want to run it on a different port, you can specify the port

	python3 manage.py runserver 8100


Open your browser and ensure you can see a Django page

	http://127.0.0.1:8100/

## Test/production server

[Digital Ocean guide](https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-uwsgi-and-nginx-on-ubuntu-16-04#setting-up-the-uwsgi-application-server)

Exit your virtualenv

	deactivate

Install necessary system packages

	sudo apt-get install python3-dev
	sudo -H pip3 install uwsgi

Make directory for sites

	sudo mkdir -p /etc/uwsgi/sites








