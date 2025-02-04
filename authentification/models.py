from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    
    post = models.fields.CharField(max_length=100)
    tel = models.IntegerField(null=True, blank=True)