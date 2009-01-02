from django.conf.urls.defaults import *
import django.views.static

from settings import MEDIA_ROOT

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
                       
    (r'^images/(?P<path>.*)$', django.views.static.serve,
     {'document_root': MEDIA_ROOT + '/images',
       'show_indexes': True}),

    (r'^(?P<path>favicon.ico)$', django.views.static.serve,
     {'document_root': MEDIA_ROOT + '/images',
       'show_indexes': True}),
                       
    (r'', include('fwc_mobile.mobile.urls')),
    
)
