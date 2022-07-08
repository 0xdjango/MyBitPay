from django.contrib import admin
from save_chart.models import Chart, StudyTemplate, DrawingTemplate


# Register your models here.
class ChartAdmin(admin.ModelAdmin):
    list_display = ['ownerId', 'ownerSource', 'name', 'symbol', 'resolution', 'lastModified']


admin.site.register(Chart, ChartAdmin)


class StudyTemplateAdmin(admin.ModelAdmin):
    list_display = ['ownerSource', 'ownerId', 'name']


admin.site.register(StudyTemplate, StudyTemplateAdmin)


class DrawingTemplateAdmin(admin.ModelAdmin):
    list_display = ['ownerSource', 'ownerId', 'name', 'tool']


admin.site.register(DrawingTemplate, DrawingTemplateAdmin)
