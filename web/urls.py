from django.conf.urls import patterns, include, url

web_urls = patterns('web.views',
    # Examples:
    # url(r'^$', 'Melodia.views.home', name='home'),
    # url(r'^Melodia/', include('Melodia.foo.urls')),

	url(r'^$|main/', 'main'),
	url(r'^login/', 'login'),
)
