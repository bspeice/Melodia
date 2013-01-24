from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect

@login_required
def main(request):
	return render_to_response("main", context_instance = RequestContext(request))

def login_page(request):
	return render_to_response("login", context_instance = RequestContext(request))

def authenticate(request):
	username = request.POST["username"]
	password = request.POST["password"]
	user = authenticate(username, password)

	if user is not None:
		if user.isactive:
			login(request, user)
			redirect("/")
		else:
			#User is inactive
			pass
	else:
		#Authentication failed
		pass
