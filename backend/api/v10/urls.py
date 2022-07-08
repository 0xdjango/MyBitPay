
from . import views
from django.views.decorators.csrf import csrf_exempt
from django.urls import path
#GET 	charts?userid=0&clientid=1
#GET 	charts?userid=0&clientid=1&chartid=2
#DELETE charts?userid=0&clientid=1&chartid=2
#POST 	charts?userid=0&clientid=1&chartid=2
#POST 	charts?userid=0&clientid=1

urlpatterns = [
	path('charts', csrf_exempt(views.doTheMagic)),
]
