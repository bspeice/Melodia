from django.conf.urls import patterns, include, url

web_urls = patterns('web.views',
    # Examples:
    # url(r'^$', 'Melodia.views.home', name='home'),
    # url(r'^Melodia/', include('Melodia.foo.urls')),

	url(r'^$|main/', 'index.main'),
	url(r'^login/', 'authentication.login'),
	url(r'^logout/', 'authentication.logout'),
)
