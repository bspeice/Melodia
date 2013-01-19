from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

def login_page(request):
	return render_to_response("login.html", context_instance = RequestContext(request))
