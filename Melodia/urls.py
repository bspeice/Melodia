from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Melodia web client
from web.urls import web_urls

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Melodia.views.home', name='home'),
    # url(r'^Melodia/', include('Melodia.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

	# Defer handling urls to the web_urls controller
	url('', include(web_urls)),
)
