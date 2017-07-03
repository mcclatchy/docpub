
# Prerequisites

* Mac OS X (local server)
* Ubuntu 16 (test/prod server)
* Python 3.x (e.g. Python 3.5.1)
	* check your version by running `python3 --version`
* virtualenv
* virtualenvwrapper
* git
* sqlite

# Local setup

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

	pip3 install -r requirements.txt

## Private settings

Create a private settings file

	vim ~/path/to/docpub/docpub/settings_private.py

Add the following

	# Django settings
	SECRET_KEY = ''
	ALLOWED_HOSTS = ['']

	# shared DocumentCloud credentials
	DC_USERNAME = ''
	DC_PASSWORD = ''

	# docpub settings
	DOCPUBENV = ''
	COMPANY = ''
	EMBED_CSS = ''

	# social auth (optional)
	SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
	SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''
	SOCIAL_AUTH_PASSWORDLESS = True
	SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = ['']

# Local server

Start it 

	python3 manage.py runserver

If you want to run it on a different port, you can specify the port

	python3 manage.py runserver 8100


Open your browser and ensure you can see a Django page

	http://127.0.0.1:8100/

# Test/production server

Thanks to this [Digital Ocean guide](https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-uwsgi-and-nginx-on-ubuntu-16-04#setting-up-the-uwsgi-application-server).

## System installations and config

Update your system

	sudo apt-get update
	sudo apt-get upgrade

Install necessary system packages

	sudo apt-get install python3-pip
	sudo -H pip3 install virtualenv virtualenvwrapper

Add the following to your `.bashrc` file

	## virtualenvwrapper vars
	export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3

	export WORKON_HOME=~/Envs
	source /usr/local/bin/virtualenvwrapper.sh

	## DOCPUB APP
	alias docpub='workon docpub && cd ~/docpub/docpub'

Make the virtualenvs directory

	mkdir -p ~/Envs

Enable the new settings

	source ~/.bashrc

Add an SSH key in your GitHub account

	https://help.github.com/articles/generating-an-ssh-key/

Clone the repo (or your fork)

	git clone git@github.com:mcclatchy/docpub.git

Create your virtualenv

	mkvirtualenv docpub

Enable the virtualenv

	docpub

### Set up the Django app

Install the requirements file (`../` included because `docpub` command takes you one level deeper)

	pip3 install -r ../requirements.txt

Create a private settings file

	vim ~/docpub/docpub/docpub/settings_private.py

Add your Django secret key and DocumentCloud credentials

	SECRET_KEY = ''
	ALLOWED_HOSTS = ['']
	DC_USERNAME = ''
	DC_PASSWORD = ''

Initial migration for admin tables

	python3 manage.py migrate

Initial migration for the app

	python3 manage.py makemigrations docs
	python3 manage.py migrate

Create a super user

	python3 manage.py createsuperuser

Update the firewall permissions

	sudo ufw allow 8080

Test the local server

	python3 manage.py runserver 0.0.0.0:8080

Go here, confirm the admin login page appears and log in to confirm everything works as expected.
	
	your-domain.com/admin

Stop the local server

	Ctrl + C

## Set up uWSGI application server

Exit your virtualenv

	deactivate

Install key pieces 

	sudo apt-get install python3-dev
	sudo -H pip3 install uwsgi

Make directory for sites

	sudo mkdir -p /etc/uwsgi/sites

Make the ini file

	sudo vim /etc/uwsgi/sites/docpub.ini

Paste in these settings

	[uwsgi]

	logto = /var/log/uwsgi/error.log

	project = docpub
	uid = ubuntu
	base = /home/%(uid)

	chdir = %(base)/%(project)/%(project)
	home = %(base)/Envs/%(project)
	module = %(project).wsgi:application

	master = true
	processes = 5

	socket = /run/uwsgi/%(project).sock
	chown-socket = %(uid):www-data
	chmod-socket = 660
	vacuum = true

Create a systemd unit file 

	sudo vim /etc/systemd/system/uwsgi.service

Paste this 

	[Unit]
	Description=uWSGI Emperor service

	[Service]
	ExecStartPre=/bin/bash -c 'mkdir -p /run/uwsgi; chown ubuntu:www-data /run/uwsgi'
	ExecStart=/usr/local/bin/uwsgi --emperor /etc/uwsgi/sites
	Restart=always
	KillSignal=SIGQUIT
	Type=notify
	NotifyAccess=all

	[Install]
	WantedBy=multi-user.target

## Set up nginx reverse proxy cache

Install nginx 

	sudo apt-get install nginx

Create a config file

	sudo vim /etc/nginx/sites-available/docpub

Add this

	server {
	    listen 80;
	    server_name YOUR-DOMAIN.COM;
	    access_log /var/log/nginx/docpub_access.log;
	    error_log /var/log/nginx/docpub_error.log;

	    location = /favicon.ico { access_log off; log_not_found off; }

	    location /static/ {
	        root /home/ubuntu/docpub/docpub;
	    }

	    location / {
	        include         uwsgi_params;
	        uwsgi_pass      unix:/run/uwsgi/docpub.sock;
	    }
	}	

Remove the symlink for the default site

	sudo rm /etc/nginx/sites-enabled/default

Symlink the available site to an enable site

	sudo ln -s /etc/nginx/sites-available/docpub /etc/nginx/sites-enabled

Check the configuration

	sudo nginx -t

## Server final prep

Restart nginx

	sudo systemctl restart nginx

Start uwsgi
	
	sudo systemctl start uwsgi

Update the firewall rules

	sudo ufw delete allow 8080
	sudo ufw allow 'Nginx Full'

Enable uwsgi and nginx to run on startup

	sudo systemctl enable nginx
	sudo systemctl enable uwsgi

# Google oauth

## Instructions

Follow steps in official documentation

	https://python-social-auth.readthedocs.io/en/latest/configuration/django.html

## Additional steps

* enable Google+ API (necessary?)

## Migration fix 

([via StackOverflow](https://stackoverflow.com/a/42946678/217955))

``` Migrating existing projects

According to the migration instructions here:

pip install python-social-auth==0.2.21
Run migrations: python manage.py migrate
Install the required module for Django: pip install social-auth-app-django
Run migrations again: python manage.py migrate
Update Django's app list and the backend-related settings according to the settings paragraph of the same page.
Now you can safely uninstall the old package: pip uninstall python-social-auth
New projects

pip install python-social-auth==0.2.21
pip install social-auth-app-django
Set Django's app list and the backend-related settings according to the settings paragraph of the migration page.
Apply migrations: python manage.py migrate
Uninstall the old package: pip uninstall python-social-auth ```
