from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response

@login_required
def main(request):
	return render_to_response("main", context_instance = RequestContext(request))

def login(request):
	return render_to_response("login", context_instance = RequestContext(request))
