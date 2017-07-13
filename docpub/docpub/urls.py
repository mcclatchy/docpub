from django.conf.urls import include, url
from django.contrib import admin
from docpub.settings import DEBUG, DOCPUBENV
from docs.views import index


urlpatterns = [
    url(r'^docs/', include('docs.urls')),
    url(r'^admin/', admin.site.urls),
    ## social auth
    url(r'^$', index, name='index'),
    # url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('social_django.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    ## django-s3direct
    url(r'^s3direct/', include('s3direct.urls')),
]

## if Django is in debug mode...
if DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

## if we're not on prod, include the environment in the header
if DOCPUBENV != 'prod':
    env = DOCPUBENV

admin.site.site_header = 'DocPub {}'.format(env)

## disable the 'View site' in the admin header
admin.site.site_url = None

