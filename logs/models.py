from django.db import models
from qsystem.models import Profile
from datetime import datetime
# Create your models here.

class Log(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    photo = models.ImageField(upload_to="logs")
    is_correct = models.BooleanField(default=False)
    succesful = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        dt = self.created
        return "ID: " + str(self.id) + " Time: " + (dt.strftime('%Y-%m-%d %H:%M'))
    