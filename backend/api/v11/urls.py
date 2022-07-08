from django.urls import path
from api.v11 import studyTemplates
from api.v11 import drawingTemplates
from api.v11 import charts
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
	path(r'charts', csrf_exempt(charts.processRequest)),
	path(r'study_templates', csrf_exempt(studyTemplates.processRequest)),
	path(r'drawing_templates', csrf_exempt(drawingTemplates.processRequest)),
]
