from django.contrib import admin
from .models import Log

class LogAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'succesful', 'profile', 'photo')

# Register your models here.
admin.site.register(Log, LogAdmin)
