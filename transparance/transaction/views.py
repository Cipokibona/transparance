from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from authentification.models import User
from transaction.models import Compte, CompteEnCompte, Depense, Retrait, Travail, MontantPayeTravail, DepenseTravail
from django.db.models import Sum


@login_required
def home (request):

    comptes = Compte.objects.filter(is_active=True)
    sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
    total = sum_comptes['total']

    return render (request,'transaction/home.html', {'comptes':comptes,'total':total})


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
                return render (request, 'transaction/home.html', {'comptes':comptes, 'msg_succes':msg_succes,'total':total})
            else:
                msg_error = True
            
        return render(request, self.template_name, context={'user':user, 'msg_error':msg_error})
    

class TransactionPageView(View):
    template_name = 'transaction/transaction.html'

    def get(self, request):
        
        comptes = Compte.objects.filter(is_active=True)

        return render (request, self.template_name, {'comptes':comptes})

    def post(self, request):
        comptes = Compte.objects.filter(is_active=True)
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
                
        return render(request, self.template_name,{'comptes':comptes})
    

class NewComptePageView(View):

    template_name = 'transaction/newcompte.html'

    def get(self, request):

        return render (request, self.template_name)
    
    def post(self, request):
        msg_error = False
        if request.method == 'POST':
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
            return render (request, 'transaction/home.html', {'comptes':comptes, 'msg_succes':msg_succes,'total':total})

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
        comptes = Compte.objects.filter(is_active=True)
        sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
        total = sum_comptes['total']
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
                msg_succes = True
            return render (request, 'transaction/home.html', {'comptes':comptes, 'msg_succes':msg_succes,'total':total})

        return render (request, self.template_name)
    

class TravailPagerView(View):
    template_name = 'transaction/travail.html'

    def get(self, request):
        comptes = Compte.objects.filter(is_active=True)
        travaux = Travail.objects.filter(is_active=True)
        
        return render (request, self.template_name, {'comptes':comptes,'travaux':travaux})
    
    def post(self, request):
        msg_error = False
        comptes = Compte.objects.filter(is_active=True)
        travaux = Travail.objects.filter(is_active=True)
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
                return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes,'travaux':travaux})
            else:
                montant = int(montant)
                compte_id = int(compte_id)
                valeur = int(valeur)
                compte = Compte.objects.get(id=compte_id)
                # annulation du depot si le montant est inferieur a zero
                if montant < 0:
                    msg_error = True
                    return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes,'travaux':travaux})
                # creation du model Travail
                travail = Travail(
                    titre = titre,
                    proprio = proprio,
                    adresse = adresse,
                    valeur = valeur,
                )
                travail.save()
                # creation du model Retrait
                montant_paye = MontantPayeTravail(
                    author = request.user,
                    compte = compte,
                    travail = travail,
                    montant = montant,
                )
                montant_paye.save()
                # mis a jour du montant sur le compte selectionner
                compte.montant = compte.montant + montant
                compte.save()
                msg_succes = True
            return render (request, 'transaction/home.html', {'comptes':comptes, 'msg_succes':msg_succes})

        return render (request, self.template_name)