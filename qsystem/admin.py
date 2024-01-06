from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', )


admin.site.register(Profile, ProfileAdmin)
