#Utilities file for the web client
from django.utils import simplejson
from django.http import HttpResponse

def json_response(**kwargs):
	#This is used to make sure that we have a standard json response
	response[]
	for key, value in kwargs.iteritems():
		response[key] = value

	#After including anything specified in our arguments, make sure that we have a "success" parameter
	if not "success" in response:
		response["success"] = True

	return HttpResponse(simplejson.dumps(response))
