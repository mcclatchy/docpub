from django.conf.urls import include, url
from django.contrib import admin
from docpub.settings import DEBUG as debug
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

if debug:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns