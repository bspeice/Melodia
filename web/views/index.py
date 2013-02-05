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
	return render_to_response("index", context_instance = RequestContext(request))
