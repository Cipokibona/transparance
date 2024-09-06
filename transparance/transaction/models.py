from django.db import models

# Create your models here.

class Compte(models.Model):

    name = models.fields.CharField(max_length=100)
    destription = models.fields.CharField(max_length=100)
    montant = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)