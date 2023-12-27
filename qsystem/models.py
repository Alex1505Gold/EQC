from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="photos", blank=True)
    acc_type = models.TextField()

    def __str__(self):
        return str(self.user.username)
    