# applications/admin.py

from django.contrib import admin
from .models import Application

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'program', 'email', 'date_of_application', 'status')
    list_filter = ('program', 'status')
    search_fields = ('full_name', 'email', 'program__name')

admin.site.register(Application, ApplicationAdmin)
