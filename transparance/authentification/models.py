from django.db import models

# Create your models here.


class personnel(models.Model):

    first_name = models.fields.CharField(max_length=100)
    name = models.fields.CharField(max_length=100)
    user_name = models.fields.CharField(max_length=100)
    password = models.fields.CharField(max_length=100)
    post = models.fields.CharField(max_length=100)
    active = models.fields.BooleanField(default=True)