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
    frais_transaction = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)

class Depense(models.Model):

    titre = models.fields.CharField(max_length=100)
    description = models.fields.CharField(max_length=100)
    montant = models.IntegerField(null=True, blank=True)
    fixe = models.BooleanField(default=False)


class Travail(models.Model):

    titre = models.fields.CharField(max_length=100)
    proprio = models.fields.CharField(max_length=100)
    adresse = models.fields.CharField(max_length=100)
    valeur = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_debut = models.DateTimeField(default=timezone.now)
    date_fin = models.DateTimeField(null=True)

class MontantPayeTravail(models.Model):

    travail = models.ForeignKey(Travail, related_name='avance_travail', on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    description = models.fields.CharField(max_length=100)
    compte = models.ForeignKey(Compte, null=True, on_delete=models.CASCADE)
    montant = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)

class DepenseTravail(models.Model):

    travail = models.ForeignKey(Travail, related_name='depenses', on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    description = models.fields.CharField(max_length=100)
    compte = models.ForeignKey(Compte, null=True, on_delete=models.CASCADE)
    montant = models.IntegerField(null=True, blank=True)
    is_group = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

class DepenseDetailTravail(models.Model):

    depense_source = models.ForeignKey(DepenseTravail, null=True, on_delete=models.CASCADE)
    depense = models.fields.CharField(max_length=100)
    montant = models.IntegerField(null=True, blank=True)

class Retrait(models.Model):

    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    compte = models.ForeignKey(Compte, null=True, on_delete=models.CASCADE)
    depense = models.ForeignKey(Depense, null=True, on_delete=models.CASCADE)
    depense_travail = models.ForeignKey(DepenseTravail, null=True, on_delete=models.CASCADE)
    montant = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)


class Operation(models.Model):

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    compte = models.ForeignKey(Compte, on_delete=models.SET_NULL, null=True, blank=True)
    compte_en_compte = models.ForeignKey(CompteEnCompte, on_delete=models.SET_NULL, null=True, blank=True)
    retrait = models.ForeignKey(Retrait, on_delete=models.SET_NULL, null=True, blank=True)
    avance = models.ForeignKey(MontantPayeTravail, on_delete=models.SET_NULL, null=True, blank=True)
    depense_travail = models.ForeignKey(DepenseTravail, on_delete=models.SET_NULL, null=True, blank=True)
    type_operation = models.fields.CharField(max_length=100)
    description = models.fields.CharField(max_length=100)
    montant = models.IntegerField(null=True, blank=True)
    frais_transaction = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)