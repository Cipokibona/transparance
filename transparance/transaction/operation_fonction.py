from transaction.models import Operation,Compte,CompteEnCompte,Retrait,MontantPayeTravail,DepenseTravail,Travail
from authentification.models import User


# annuler une operation, retourne une valeur bool
def annuler_operation(id):

    operation = Operation.objects.get(id=id)
    montant = operation.montant
    frais_transaction = operation.frais_transaction
    compte = operation.compte
    # cas de compte en compte
    if operation.type_operation == 'Compte en compte':
        # annuler le transfer
        compte_emetteur = Compte.objects.get(id=operation.compte_en_compte.compte_emetteur.id)
        compte_recepteur = Compte.objects.get(id=operation.compte_en_compte.compte_recepteur.id)
        compte_emetteur.montant = compte_emetteur.montant + montant + frais_transaction
        compte_recepteur.montant = compte_recepteur.montant - montant
        # annuler le retrait des frais de transaction
        if frais_transaction > 0:
            retrait = Retrait.objects.get(id=operation.retrait.id)
            retrait.delete()

        # delete la table CompteEnCompte
        transfer = CompteEnCompte.objects.get(id=operation.compte_en_compte.id)
        transfer.delete()
        compte_emetteur.save()
        compte_recepteur.save()
        operation.delete()
        
        return True
    # cas de retrait
    if operation.type_operation == 'Retrait':
        # annuler le retrait
        retrait = Retrait.objects.get(id=operation.retrait.id)
        retrait.delete()
        # recuperer le montant
        compte_retrait = Compte.objects.get(id=compte.id)
        compte_retrait.montant = compte_retrait.montant + montant
        compte_retrait.save()
        operation.delete()

        return True
    # cas de dépot
    if operation.type_operation == 'Dépot':
        # recuperation du travail et du montant payer
        montant_paye = MontantPayeTravail.objects.get(id=operation.avance.id)
        travail = Travail.objects.get(id=montant_paye.travail.id)
        # verification si c'est le premier avance pour supprimer le travail
        if montant_paye.description == f'Première avance sur le projet {travail.titre}.':
            travail.delete()
        montant_paye.delete()
        # supprimer le montant
        compte_recepteur = Compte.objects.get(id=compte.id)
        compte_recepteur.montant = compte_recepteur.montant - montant
        compte_recepteur.save()
        operation.delete()
        
        return True
    # cas de dépense sur travail
    if operation.type_operation == 'Dépense sur travail' or operation.type_operation == 'Dépenses détaillées':
        # suppression de la table DepenseTravail
        depense_travail = DepenseTravail.objects.get(id=operation.depense_travail.id)
        depense_travail.delete()
        # recuperation du montant
        compte_emetteur = Compte.objects.get(id=compte.id)
        compte_emetteur.montant = compte_emetteur.montant + montant
        compte_emetteur.save()
        operation.delete()

        return True

    return False