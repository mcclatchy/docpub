
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

	alias='workon docpub && cd ~/path/to/code' 

## Requirements

Install the requirements 

	pip install -r requirements.txt

# Dev work

## Local server

Start it 

	python3 manage.py runserver

If you want to run it on a different port, you can specify the port

	python3 manage.py runserver 8100


Open your browser and ensure you can see a Django page

	http://127.0.0.1:8100/



# Misc

## creating private settings 

Create

	settings_private.py

Add

	SECRET_KEY = '8$wp+wq4*@ndfl+8fk04g8_^3bk29d54)$o7sdupxhid9b)q%!'


## Settings

Add 

	import settings_private

Update

	TIME_ZONE = 'America/New_York'

Add

	# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')


## Views

# from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

## docs urls

from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
]


## docpub urls

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^docs/', include('docs.urls')),
    url(r'^admin/', admin.site.urls),
]




