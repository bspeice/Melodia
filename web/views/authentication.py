from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth import forms
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect

#Melodia-specific utilities
from web_utils import json_response as json

def _user_authenticate(request):
	form = forms.AuthenticationForm(data=request.POST)
	if form.is_valid():
		try:
			cleaned_data = form.clean()
			django_login(request, form.get_user())
			return redirect("/")

		except: 
			#Invalid login, or ValidationError
			return render_to_response("login", context_instance = RequestContext(request,
																				{"auth_form": forms.AuthenticationForm(data=request.POST),
																				"login_error": "Internal error trying to log in."} ))
	else:
		return render_to_response("login", context_instance = RequestContext(request,
																			{"auth_form": forms.AuthenticationForm(data=request.POST),
																			"login_error": "Unrecognized username or password."} ))

def login(request):
	if request.method == "POST":
		#Someone is trying to log in
		return _user_authenticate(request)
	else:
		return render_to_response("login", context_instance = RequestContext(request,
																			{"auth_form": forms.AuthenticationForm()} ))

def logout(request):
	django_logout(request)
	return redirect("/login")
