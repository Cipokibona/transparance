from django.db import models
from django.utils import timezone
from authentification.models import User

# Create your models here.

class Compte(models.Model):

    name = models.fields.CharField(max_length=100)
    description = models.fields.CharField(max_length=100)
    montant = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class CompteEnCompte(models.Model):

    compte_emetteur = models.ForeignKey(Compte, related_name='transferts_emis', on_delete=models.CASCADE)
    compte_recepteur = models.ForeignKey(Compte, related_name='transferts_recus', on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    montant = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
