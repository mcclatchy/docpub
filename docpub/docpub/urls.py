from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from docpub.settings import DEBUG, DOCPUBENV
from docs.views import index


urlpatterns = [
    ## import any URL pattens defined in /docpub/docs/urls.py
    url(r'^docs/', include('docs.urls')),
    ## admin URLs
    url(r'^admin/', admin.site.urls),
    ## admin login for social auth or Django credentials
    url(r'^accounts/login/$', auth_views.LoginView.as_view()),
    ## social auth
    url(r'^$', index, name='index'),
    # url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('social_django.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    ## django-s3direct
    # url(r'^s3direct/', include('s3direct.urls')),
]

## if Django is in debug mode, then include toolbar URLs
if DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

## if we're not on prod, include the environment in the header
env = ''
if DOCPUBENV != 'prod':
    env = DOCPUBENV

admin.site.site_header = 'DocPub {}'.format(env)

## disable the 'View site' in the admin header
# admin.site.site_url = None

