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
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    montant = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)

class Depense(models.Model):

    titre = models.fields.CharField(max_length=100)
    description = models.fields.CharField(max_length=100)
    fixe = models.BooleanField(default=False)

class Retrait(models.Model):

    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    compte = models.ForeignKey(Compte, null=True, on_delete=models.CASCADE)
    depense = models.ForeignKey(Depense, null=True, on_delete=models.CASCADE)
    montant = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)


class Travail(models.Model):

    titre = models.fields.CharField(max_length=100)
    proprio = models.fields.CharField(max_length=100)
    adresse = models.fields.CharField(max_length=100)
    valeur = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_debut = models.DateTimeField(default=timezone.now)
    date_fin = models.DateTimeField(null=True)

class MontantPayeTravail(models.Model):

    travail = models.ForeignKey(Travail, null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    compte = models.ForeignKey(Compte, null=True, on_delete=models.CASCADE)
    montant = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)

class DepenseTravail(models.Model):

    travail = models.ForeignKey(Travail, null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    compte = models.ForeignKey(Compte, null=True, on_delete=models.CASCADE)
    montant = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)