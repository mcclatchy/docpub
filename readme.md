
# Prerequisites

* Python 3.x (e.g. Python 3.5.1)
	* check your version by running `python3 --version`
* virtualenv
* virtualenvwrapper
* git

# Setup

## Local repo

	git init docpub

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

Add your secret key

	SECRET_KEY = ''

# Dev work

## Local server

Start it 

	python3 manage.py runserver

If you want to run it on a different port, you can specify the port

	python3 manage.py runserver 8100


Open your browser and ensure you can see a Django page

	http://127.0.0.1:8100/


