from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, forms
from django import forms as django_forms
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect

#Melodia-specific utilities
from web_utils import json_response as json

@login_required
def main(request):
	return render_to_response("main", context_instance = RequestContext(request))

def login_page(request):
	if request.method == "POST":
		#Someone is trying to log in
		return _user_authenticate(request)
	else:
		return render_to_response("login", context_instance = RequestContext(request,
																			{"auth_form": forms.AuthenticationForm()} ))

def _user_authenticate(request):
	form = forms.AuthenticationForm(data=request.POST)
	if form.is_valid():
		try:
			cleaned_data = form.clean()
			print cleaned_data
			login(request, form.get_user())
			return redirect("/")

		except django_forms.ValidationError:
			#Invalid login
			return json(success = False,
						message = "Either the username or the password was not recognized.")

	else:
		return render_to_response("login", context_instance = RequestContext(request,
																			{"auth_form": forms.AuthenticationForm(data=request.POST),
																			"login_error": form.errors} ))
