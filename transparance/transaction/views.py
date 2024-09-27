from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from authentification.models import User
from transaction.models import Compte, CompteEnCompte, Depense, Retrait, Travail, MontantPayeTravail, DepenseTravail, Operation
from django.db.models import Sum
from django.utils import timezone


@login_required
def home (request):

    comptes = Compte.objects.filter(is_active=True)
    sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
    total = sum_comptes['total']
    operations = Operation.objects.all().order_by('-date')

    return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations})


@login_required
def travail (request):

    return render (request,'transaction/travail.html')

class ProfilPageView(View):
    template_name = 'transaction/profil.html'

    def get(self, request):
        msg_error = False
        try:
            user = User.objects.get(id=request.user.id)

        except Exception as e:
            msg_error = True
        
        return render (request, self.template_name, {'user':user, 'msg_error':msg_error})

    def post(self, request):
        msg_error = False
        if request.method == 'POST':
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            # tel = request.POST.get("tel")
            post = request.POST.get("post")
            # username = request.POST.get("username")
            # password = request.POST.get("password")
            # valid_password = request.POST.get("valid_password")
                
                # enregistrement des nouveaux données du profil

            user = User.objects.get(id=request.user.id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            # user.tel = tel
            user.post = post
            user.is_staff = True
            # user.username = username
            # user.password = password
            user.save()
            
        return render(request, self.template_name, context={'user':user, 'msg_error':msg_error})


class NewUserPageView(View):
    template_name = 'transaction/newuser.html'

    def get(self, request):
        
        return render (request, self.template_name)

    def post(self, request):
        msg_error = False
        if request.method == 'POST':
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            # tel = request.POST.get("tel")
            post = request.POST.get("post")
            username = request.POST.get("username")
            password = request.POST.get("password")
            # valid_password = request.POST.get("valid_password")
                
                # enregistrement du nouvel utilisateur

            if username and password:
                # enregistrement de user
                user = User.objects.create_user(
                        first_name=first_name,
                        last_name=last_name,
                        email = email,
                        post = post,
                        username=username,
                        password=password,
                        is_staff = True,
                    )
                user.save()
                msg_succes = True
                comptes = Compte.objects.filter(is_active=True)
                sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
                total = sum_comptes['total']
                
                operations = Operation.objects.all().order_by('-date')
                return render (request, 'transaction/home.html', {'comptes':comptes, 'msg_succes':msg_succes,'total':total,'operations':operations})
            else:
                msg_error = True
            
        return render(request, self.template_name, context={'user':user, 'msg_error':msg_error})
    

class TransactionPageView(View):
    template_name = 'transaction/transaction.html'

    def get(self, request):
        
        comptes = Compte.objects.filter(is_active=True)

        return render (request, self.template_name, {'comptes':comptes})

    def post(self, request):
        operations = Operation.objects.all().order_by('-date')
        comptes = Compte.objects.filter(is_active=True)
        sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
        total = sum_comptes['total']
        msg_error = False
        if request.method == 'POST':
            emetteur = request.POST.get("compte_emetteur")
            recepteur = request.POST.get("compte_recepteur")
            montant_saisi = request.POST.get("montant")
            if montant_saisi == '':
                msg_error = True
                return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes})
            else:
                montant = int(montant_saisi)

            # vérification de la valeur recuperer
            if emetteur == '' or recepteur == '':
                msg_error = True
                return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes})
            else:
                compte_emetteur = Compte.objects.get(id=emetteur)
                compte_recepteur = Compte.objects.get(id=recepteur)

                # verification du montant a retirer
                if compte_emetteur.montant < montant:
                    msg_error = True
                    return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes})
                else:
                    # annulation du transfert si le compte emetteur et le meme que le compte recepteur
                    if compte_emetteur == compte_recepteur:
                        msg_error = True
                        return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes})
                    # tranferer
                    compte_emetteur.montant = compte_emetteur.montant - montant
                    compte_recepteur.montant = compte_recepteur.montant + montant
                    # save data
                    compte_emetteur.save()
                    compte_recepteur.save()
                    # table compte en compte
                    transfer = CompteEnCompte(
                        compte_emetteur=compte_emetteur,
                        compte_recepteur=compte_recepteur,
                        author=request.user,
                        montant=montant,
                    )
                    transfer.save()
                    # enregistrement de l'operation
                    operation = Operation(
                        compte_en_compte = transfer,
                        author = request.user,
                        type_operation = 'Compte en compte',
                        description = f'De {compte_emetteur.name} à {compte_recepteur.name}',
                        montant = montant,
                    )
                    operation.save()
                    msg_succes = True
                    return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations,'msg_succes':msg_succes})
                
        return render(request, self.template_name,{'comptes':comptes})
    

class NewComptePageView(View):

    template_name = 'transaction/newcompte.html'

    def get(self, request):

        return render (request, self.template_name)
    
    def post(self, request):
        msg_error = False
        if request.method == 'POST':
            
            operations = Operation.objects.all().order_by('-date')
            compte_name = request.POST.get("name")
            description = request.POST.get("description")
            montant = request.POST.get("montant")
            # si le montant n'est pas saisi initialiser a zero
            if montant == '':
                montant = 0
            elif compte_name == '':
                msg_error = True
                return render(request, self.template_name, {'msg_error':msg_error})
            else:
                montant = int(montant)
            new_compte = Compte(
                name = compte_name,
                description = description,
                montant = montant,

            )
            new_compte.save()
            msg_succes = True
            comptes = Compte.objects.filter(is_active=True)
            sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
            total = sum_comptes['total']
            return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations,'msg_succes':msg_succes})

        return render (request, self.template_name, {'msg_error':msg_error})
    

class NewRetraitView(View):

    template_name = 'transaction/depense.html'

    def get(self, request):

        comptes = Compte.objects.filter(is_active=True)
        sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
        total = sum_comptes['total']
        
        return render (request, self.template_name, {'comptes':comptes, 'total':total})
    
    def post(self, request):
        msg_error = False
        operations = Operation.objects.all().order_by('-date')
        comptes = Compte.objects.filter(is_active=True)
        if request.method == 'POST':
            titre = request.POST.get("titre")
            description = request.POST.get("description")
            montant = request.POST.get("montant")
            compte_id = request.POST.get("compte")
            # si le montant n'est pas saisi initialiser a zero
            if montant == '' or compte_id == '' or titre == '':
                msg_error = True
                return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes, 'total':total})
            else:
                montant = int(montant)
                compte_id = int(compte_id)
                compte = Compte.objects.get(id=compte_id)
                # annulation du retrait si le montant est supérieur du montant du compte
                if montant > compte.montant:
                    msg_error = True
                    return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes, 'total':total})
                # creation du model Depense
                depense = Depense(
                    titre = titre,
                    description = description,
                )
                depense.save()
                # creation du model Retrait
                retrait = Retrait(
                    author = request.user,
                    compte = compte,
                    depense = depense,
                    montant = montant,
                )
                retrait.save()
                # mis a jour du montant sur le compte selectionner
                compte.montant = compte.montant - montant
                compte.save()
                # enregistrement de l'operation
                operation = Operation(
                    compte = compte,
                    author = request.user,
                    type_operation = 'Retrait',
                    description = description,
                    montant = montant,
                    retrait = retrait,
                )
                operation.save()
                msg_succes = True
                sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
                total = sum_comptes['total']
            return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations,'msg_succes':msg_succes})

        return render (request, self.template_name)
    

class TravailPagerView(View):
    template_name = 'transaction/travail.html'

    def get(self, request):
        comptes = Compte.objects.filter(is_active=True)
        travaux = Travail.objects.filter(is_active=True)
        for travail in travaux:
            total_depenses = travail.depenses.aggregate(Sum('montant'))['montant__sum'] or 0
            total_avance = travail.avance_travail.aggregate(Sum('montant'))['montant__sum'] or 0
            travail.total_depenses = total_depenses
            travail.total_avance = total_avance
        travaux_finis = Travail.objects.filter(is_active=False)
        for travail_fini in travaux_finis:
            final_depenses = travail_fini.depenses.aggregate(Sum('montant'))['montant__sum'] or 0
            final_avance = travail_fini.avance_travail.aggregate(Sum('montant'))['montant__sum'] or 0
            travail_fini.final_depenses = final_depenses
            travail_fini.final_avance = final_avance
            travail_fini.montant_net = travail_fini.final_avance - (travail_fini.final_depenses or 0)
        
        return render (request, self.template_name, {'comptes':comptes,'travaux':travaux,'travaux_finis':travaux_finis})
    
    def post(self, request):
        
        operations = Operation.objects.all().order_by('-date')
        msg_error = False
        comptes = Compte.objects.filter(is_active=True)
        travaux = Travail.objects.filter(is_active=True)
        sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
        total = sum_comptes['total']
        for travail in travaux:
            total_depenses = travail.depenses.aggregate(Sum('montant'))['montant__sum'] or 0
            total_avance = travail.avance_travail.aggregate(Sum('montant'))['montant__sum'] or 0
            travail.total_depenses = total_depenses
            travail.total_avance = total_avance
        travaux_finis = Travail.objects.filter(is_active=False)
        for travail_fini in travaux_finis:
            final_depenses = travail_fini.depenses.aggregate(Sum('montant'))['montant__sum'] or 0
            final_avance = travail_fini.avance_travail.aggregate(Sum('montant'))['montant__sum'] or 0
            travail_fini.final_depenses = final_depenses
            travail_fini.final_avance = final_avance
            travail_fini.montant_net = travail_fini.final_avance - (travail_fini.final_depenses or 0)

        if request.method == 'POST':
            titre = request.POST.get("titre")
            proprio = request.POST.get("proprio")
            adresse = request.POST.get("adresse")
            valeur = request.POST.get("valeur")
            montant = request.POST.get("montant")
            compte_id = request.POST.get("compte")
            # si le montant n'est pas saisi initialiser a zero
            if montant == '' or compte_id == '' or titre == '' or valeur == '':
                msg_error = True
                return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes,'travaux':travaux, 'travaux_finis':travaux_finis})
            else:
                montant = int(montant)
                compte_id = int(compte_id)
                valeur = int(valeur)
                compte = Compte.objects.get(id=compte_id)
                # annulation du depot si le montant est inferieur a zero
                if montant < 0:
                    msg_error = True
                    return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes,'travaux':travaux, 'travaux_finis':travaux_finis})
                # creation du model Travail
                travail = Travail(
                    titre = titre,
                    proprio = proprio,
                    adresse = adresse,
                    valeur = valeur,
                )
                travail.save()
                # creation du model MontantPayeTravail
                montant_paye = MontantPayeTravail(
                    author = request.user,
                    compte = compte,
                    travail = travail,
                    montant = montant,
                    description = f'Première avance sur le projet {travail.titre}.'
                )
                montant_paye.save()
                # mis a jour du montant sur le compte selectionner
                compte.montant = compte.montant + montant
                # enregistrement de l'operation
                operation = Operation(
                    compte = compte,
                    author = request.user,
                    type_operation = 'Dépot',
                    description = montant_paye.description,
                    montant = montant,
                    avance = montant_paye,
                )
                operation.save()
                compte.save()
                msg_succes = True
            return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations,'msg_succes':msg_succes})

        return render (request, self.template_name)
    

class AvanceTravailPageView(View):

    template_name = 'transaction/avance_travail.html'

    def get(self, request, id):
        comptes = Compte.objects.filter(is_active=True)
        travail = Travail.objects.get(id=id)
        
        return render (request, self.template_name, {'comptes':comptes,'travail':travail})

    def post(self, request, id):
        
        operations = Operation.objects.all().order_by('-date')
        comptes = Compte.objects.filter(is_active=True)
        travail = Travail.objects.get(id=id)

        if request.method == 'POST':
            description = request.POST.get("description")
            compte_recepteur = request.POST.get("compte_recepteur")
            montant = request.POST.get("montant")
            # si le montant n'est pas saisi initialiser a zero
            if montant == '' or compte_recepteur == '':
                msg_error = True
                return render(request, self.template_name, {'comptes':comptes,'travail':travail})
            else:
                montant = int(montant)
                compte_recepteur = int(compte_recepteur)
                compte = Compte.objects.get(id=compte_recepteur)
                # annulation du depot si le montant est inferieur a zero
                if montant <= 0:
                    msg_error = True
                    return render(request, self.template_name, {'comptes':comptes,'travail':travail, 'msg_error':msg_error})
                # creation du model MontantPayeTravail
                avance_travail = MontantPayeTravail(
                    travail = travail,
                    author = request.user,
                    description = description,
                    compte = compte,
                    montant = montant,
                )
                avance_travail.save()
                # mis a jour du montant sur le compte selectionner
                compte.montant = compte.montant + montant
                compte.save()
                # classer le travail en travaux finis au cas ou le payement total est egal a la valeur du travail
                somme_totale = MontantPayeTravail.objects.filter(travail=travail).aggregate(Sum('montant'))
                total_avance = somme_totale['montant__sum']
                if travail.valeur <= total_avance:
                    travail.is_active = False
                    travail.date_fin = timezone.now()
                    travail.save()
                # enregistrement de l'operation
                operation = Operation(
                    compte = compte,
                    author = request.user,
                    type_operation = 'Dépot',
                    description = description,
                    montant = montant,
                    avance = avance_travail,
                )
                operation.save()
                msg_succes = True
                sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
                total = sum_comptes['total']
            return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations,'msg_succes':msg_succes})

        return render (request, self.template_name, {'comptes':comptes,'travail':travail})
    
class DepenseTravailPageView(View):

    template_name = 'transaction/depense_travail.html'

    def get(self, request, id):
        comptes = Compte.objects.filter(is_active=True)
        travail = Travail.objects.get(id=id)
        
        return render (request, self.template_name, {'comptes':comptes,'travail':travail})

    def post(self, request, id):

        operations = Operation.objects.all().order_by('-date')
        comptes = Compte.objects.filter(is_active=True)
        travail = Travail.objects.get(id=id)

        if request.method == 'POST':
            nombre_total_depense = request.POST.get("nombre_total_depense")
            nombre_total_depense = int(nombre_total_depense)
            # si c'est une dépense unique
            if nombre_total_depense < 2:
                description = request.POST.get("description")
                compte_id = request.POST.get("compte_emetteur")
                montant = request.POST.get("montant")
                # si le montant n'est pas saisi initialiser a zero
                if montant == '' or compte_id == '':
                    msg_error = True
                    return render(request, self.template_name, {'comptes':comptes,'travail':travail})
                else:
                    montant = int(montant)
                    compte_id = int(compte_id)
                    compte = Compte.objects.get(id=compte_id)
                    # annulation du retrait si le montant est inferieur a zero
                    if montant <= 0 or compte.montant < montant:
                        msg_error = True
                        return render(request, self.template_name, {'comptes':comptes,'travail':travail, 'msg_error':msg_error})
                    # creation du model MontantPayeTravail
                    depense_travail = DepenseTravail(
                        travail = travail,
                        author = request.user,
                        description = description,
                        compte = compte,
                        montant = montant,
                    )
                    depense_travail.save()
                    # mis a jour du montant sur le compte selectionner
                    compte.montant = compte.montant - montant
                    compte.save()
                    # enregistrement de l'operation
                    operation = Operation(
                        compte = compte,
                        author = request.user,
                        type_operation = 'Retrait',
                        description = description,
                        montant = montant,
                        depense_travail = depense_travail,
                    )
                    operation.save()
                    msg_succes = True
                    sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
                    total = sum_comptes['total']
                return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations,'msg_succes':msg_succes})
            else:
                return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations,'msg_succes':msg_succes})

        return render (request, self.template_name, {'comptes':comptes,'travail':travail})