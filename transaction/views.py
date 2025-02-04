from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from authentification.models import User
from transaction.models import Compte, CompteEnCompte, Depense, Retrait, Travail, MontantPayeTravail, DepenseTravail, Operation, DepenseDetailTravail
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import datetime
from transaction.operation_fonction import annuler_operation


@login_required
def home (request):

    comptes = Compte.objects.filter(is_active=True)
    sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
    total = sum_comptes['total']
    operations = Operation.objects.all().order_by('-date')[:10]
    # regrouper les depenses et les revenus par mois de l'année actuelle
    annee_actuelle = datetime.now().year
    depense_mensuelles = (Retrait.objects.filter(date__year=annee_actuelle).annotate(mois=TruncMonth('date')).values('mois').annotate(total_depenses=Sum('montant')))
    revenus_mensuels = (MontantPayeTravail.objects.filter(date__year=annee_actuelle).annotate(mois=TruncMonth('date')).values('mois').annotate(total_revenus=Sum('montant')))
    depenses_dict = {d['mois']:d['total_depenses'] for d in depense_mensuelles}
    revenus_dict = {r['mois']:r['total_revenus'] for r in revenus_mensuels}

    mois_communs = set(depenses_dict.keys()).union(set(revenus_dict.keys()))
    resultats = [
        {
            'mois': mois,
            'total_depenses': depenses_dict.get(mois, 0),
            'total_revenus' : revenus_dict.get(mois,0),
            'profit' : revenus_dict.get(mois,0) - depenses_dict.get(mois,0),
            'perc_depense' : ((depenses_dict.get(mois,0)/revenus_dict.get(mois,0))*100 if revenus_dict.get(mois,0)>0 else 0),
            'perc_profit' : (((revenus_dict.get(mois,0) - depenses_dict.get(mois,0))/revenus_dict.get(mois,0))*100 if revenus_dict.get(mois,0)>0 else 0),
        }
        for mois in sorted(mois_communs)
    ]

    return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations, 'resultats':resultats})

@login_required
def operation(request, id):

    is_compte_en_compte = False
    is_retrait = False
    is_depot = False
    is_depense_travail = False
    is_depense_detail = False
    depenses = ''
    # recuperation de l'opération
    operation = Operation.objects.get(id=id)
    # Vérification de type d'opération
    if operation.type_operation == 'Compte en compte':
        is_compte_en_compte = True
        
    if operation.type_operation == 'Retrait':
        is_retrait = True

    if operation.type_operation == 'Dépot':
        is_depot = True

    if operation.type_operation == 'Dépense sur travail':
        is_depense_travail = True

    if operation.type_operation == 'Dépenses détaillées':
        is_depense_detail = True
        depense_source = DepenseTravail.objects.get(id=operation.depense_travail.id)
        depenses = DepenseDetailTravail.objects.filter(depense_source=depense_source)

    return render (
        request,
        'transaction/operation.html',
        {
            'operation':operation,
            'is_compte_en_compte':is_compte_en_compte,
            'is_retrait':is_retrait,
            'is_depot':is_depot,
            'is_depense_travail':is_depense_travail,
            'is_depense_detail':is_depense_detail,
            'depenses':depenses,
            })

@login_required
def annuler(request,id):

    annuler_operation(id)

    return redirect('home')

@login_required
def all_evaluation(request):
    depense_mensuelles = (Retrait.objects.annotate(mois=TruncMonth('date')).values('mois').annotate(total_depenses=Sum('montant')))
    revenus_mensuels = (MontantPayeTravail.objects.annotate(mois=TruncMonth('date')).values('mois').annotate(total_revenus=Sum('montant')))
    depenses_dict = {d['mois']:d['total_depenses'] for d in depense_mensuelles}
    revenus_dict = {r['mois']:r['total_revenus'] for r in revenus_mensuels}

    mois_communs = set(depenses_dict.keys()).union(set(revenus_dict.keys()))
    mois_communs = set(depenses_dict.keys()).union(set(revenus_dict.keys()))
    resultats = [
        {
            'mois': mois,
            'total_depenses': depenses_dict.get(mois, 0),
            'total_revenus' : revenus_dict.get(mois,0),
            'profit' : revenus_dict.get(mois,0) - depenses_dict.get(mois,0),
            'perc_depense' : ((depenses_dict.get(mois,0)/revenus_dict.get(mois,0))*100 if revenus_dict.get(mois,0)>0 else 0),
            'perc_profit' : (((revenus_dict.get(mois,0) - depenses_dict.get(mois,0))/revenus_dict.get(mois,0))*100 if revenus_dict.get(mois,0)>0 else 0),
        }
        for mois in sorted(mois_communs)
    ]

    return render (request,'transaction/all_evaluations.html', {'resultats':resultats})

@login_required
def travail (request,id):

    travail = Travail.objects.get(id=id)
    avances = MontantPayeTravail.objects.filter(travail=travail)
    depenses = DepenseTravail.objects.filter(travail=travail)
    total_avance = 0
    total_depense = 0
    list_id_depense_detail = []
    for avance in avances:
        total_avance = total_avance + avance.montant
    for depense in depenses:
        total_depense = total_depense + depense.montant
        if depense.is_group == True:
            list_id_depense_detail.append(depense.id)
    depenses_detail = DepenseDetailTravail.objects.filter(depense_source__in=list_id_depense_detail)

    return render (request,'transaction/info_travail.html', {'travail':travail, 'avances':avances, 'depenses':depenses,'total_avance':total_avance,'total_depense':total_depense,'depenses_detail':depenses_detail})


@login_required
def depense_fixe(request):

    if request.method == 'POST':
        msg_error = False
        # operations = Operation.objects.all().order_by('-date')
        comptes = Compte.objects.filter(is_active=True)
        sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
        total = sum_comptes['total']
        depense_fixes = Depense.objects.filter(fixe=True)
        
        depenses_checked = request.POST.getlist('depenses_checked')
        list_id = []
        compte_id = request.POST.get('compte')
        # verification du choix du compte
        if compte_id == '':
            msg_error = True
            return render(request, 'transaction/depense.html', {'msg_error':msg_error,'comptes':comptes, 'total':total,'depense_fixes':depense_fixes})
        
        compte_id = int(compte_id)
        compte = Compte.objects.get(id=compte_id)
        # list des id des dépenses choisi
        for id in depenses_checked:
            list_id.append(id)
        # récupération des dépenses choisis
        depenses = Depense.objects.filter(id__in=list_id)

        # recuperation du montant total et des titres
        montant_total = 0
        list_depense = []
        for depense in depenses:
            montant_total = montant_total + depense.montant
            list_depense.append(f'{depense.titre}:{depense.montant} BIF')

        # verification du montant total et le montant du compte
        if montant_total > compte.montant:
            msg_error = True
            return render(request, 'transaction/depense.html', {'msg_error':msg_error,'comptes':comptes, 'total':total,'depense_fixes':depense_fixes})

        # creation de la tables depense
        depense_group = Depense(
            titre = 'Dépenses groupées',
            description = f'Liste des dépenses {list_depense}',
            montant = montant_total,
        )
        depense_group.save()
        # creation de retrait
        retrait = Retrait(
            author = request.user,
            compte = compte,
            depense = depense_group,
            montant = montant_total,
        )
        retrait.save()
        # mis a jour du compte
        compte.montant = compte.montant - montant_total
        compte.save()
        # creation du model Operation
        operation = Operation(
            compte = compte,
            author = request.user,
            type_operation = 'Retrait',
            description = f'Dépenses fixes choisies: {list_depense}',
            montant = montant_total,
            retrait = retrait,
        )
        operation.save()
        

    return redirect('home')

@login_required
def evaluation_month(request,month,year):

    month = int(month)
    year = int (year)
    operations = Operation.objects.filter(date__month=month,date__year=year)
    is_get = True

    return render (request,'transaction/all_operations.html', {'operations':operations, 'is_get':is_get})


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
            tel = request.POST.get("tel")
            post = request.POST.get("post")
            username = request.POST.get("username")
            password = request.POST.get("password")
            new_password = request.POST.get("newpassword")
            user = User.objects.get(id=request.user.id)
                #verification du tel
            if tel == '':
                tel = None
            else:
                tel = int(tel)
            # verification du new password
            if new_password and user.check_password(password):
                user.set_password(new_password)
            # enregistrement des nouveaux données du profil

            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.tel = tel
            user.post = post
            user.is_staff = True
            user.username = username
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
            tel = request.POST.get("tel")
            post = request.POST.get("post")
            username = request.POST.get("username")
            password = request.POST.get("password")
            # valid_password = request.POST.get("valid_password")
                
                # enregistrement du nouvel utilisateur
            if tel == '':
                tel = None
            else:
                tel = int(tel)

            if username and password:
                # enregistrement de user
                user = User.objects.create_user(
                        first_name=first_name,
                        last_name=last_name,
                        email = email,
                        tel = tel,
                        post = post,
                        username=username,
                        password=password,
                        is_staff = True,
                    )
                user.save()
                # msg_succes = True
                # comptes = Compte.objects.filter(is_active=True)
                # sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
                # total = sum_comptes['total']
                
                # operations = Operation.objects.all().order_by('-date')
                # return render (request, 'transaction/home.html', {'comptes':comptes, 'msg_succes':msg_succes,'total':total,'operations':operations})
                return redirect ('home')
            else:
                msg_error = True
            
        return render(request, self.template_name, context={'msg_error':msg_error})
    

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
            frais_transaction = request.POST.get("frais_transaction")
            if montant_saisi == '' or frais_transaction == '':
                msg_error = True
                return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes})
            else:
                montant = int(montant_saisi)
                frais_transaction = int(frais_transaction)

            # vérification de la valeur recuperer
            if emetteur == '' or recepteur == '':
                msg_error = True
                return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes})
            else:
                compte_emetteur = Compte.objects.get(id=emetteur)
                compte_recepteur = Compte.objects.get(id=recepteur)

                # verification du montant a retirer
                montant_retrait = montant + frais_transaction
                if compte_emetteur.montant < montant_retrait:
                    msg_error = True
                    return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes})
                else:
                    # annulation du transfert si le compte emetteur et le meme que le compte recepteur
                    if compte_emetteur == compte_recepteur:
                        msg_error = True
                        return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes})
                    # tranferer
                    compte_emetteur.montant = compte_emetteur.montant - montant_retrait
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
                        frais_transaction = frais_transaction,
                    )
                    transfer.save()
                    # depense des frais de transaction
                    retrait = ''
                    if frais_transaction > 0:
                        depense = Depense(
                        titre = 'Frais de transaction',
                        description = f'De {compte_emetteur.name} à {compte_recepteur.name}, frais de transaction {frais_transaction} BIF',
                        )
                        depense.save()
                        # creation du model Retrait
                        retrait = Retrait(
                            author = request.user,
                            compte = compte_emetteur,
                            depense = depense,
                            montant = frais_transaction,
                        )
                        retrait.save()
                    # enregistrement de l'operation
                    operation = Operation(
                        compte_en_compte = transfer,
                        retrait = retrait,
                        author = request.user,
                        type_operation = 'Compte en compte',
                        description = f'De {compte_emetteur.name} à {compte_recepteur.name}, frais de transaction {frais_transaction} BIF',
                        montant = montant,
                        frais_transaction = frais_transaction,
                    )
                    operation.save()
                    # msg_succes = True
                    # return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations,'msg_succes':msg_succes})
                    return redirect('home')
                
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
            # msg_succes = True
            # comptes = Compte.objects.filter(is_active=True)
            # sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
            # total = sum_comptes['total']
            # return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations,'msg_succes':msg_succes})
            return redirect ('home')

        return render (request, self.template_name, {'msg_error':msg_error})
    

class NewRetraitView(View):

    template_name = 'transaction/depense.html'

    def get(self, request):

        comptes = Compte.objects.filter(is_active=True)
        sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
        total = sum_comptes['total']
        depense_fixes = Depense.objects.filter(fixe=True)
        
        return render (request, self.template_name, {'comptes':comptes, 'total':total, 'depense_fixes':depense_fixes})
    
    def post(self, request):
        msg_error = False
        # operations = Operation.objects.all().order_by('-date')
        comptes = Compte.objects.filter(is_active=True)
        sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
        total = sum_comptes['total']
        depense_fixes = Depense.objects.filter(fixe=True)
        if request.method == 'POST':
            titre = request.POST.get("titre")
            description = request.POST.get("description")
            montant = request.POST.get("montant")
            compte_id = request.POST.get("compte")
            is_depense_fixe = request.POST.get("depense_fixe_statu")
            # si le montant n'est pas saisi initialiser a zero
            if montant == '' or compte_id == '' or titre == '':
                msg_error = True
                return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes, 'total':total,'depense_fixes':depense_fixes})
            else:
                montant = int(montant)
                compte_id = int(compte_id)
                compte = Compte.objects.get(id=compte_id)
                # annulation du retrait si le montant est supérieur du montant du compte
                if montant > compte.montant:
                    msg_error = True
                    return render(request, self.template_name, {'msg_error':msg_error,'comptes':comptes, 'total':total, 'depense_fixes':depense_fixes})
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
                # msg_succes = True
                sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
                total = sum_comptes['total']
            # return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations,'msg_succes':msg_succes})
            return redirect ('home')

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
        
        # operations = Operation.objects.all().order_by('-date')
        msg_error = False
        comptes = Compte.objects.filter(is_active=True)
        travaux = Travail.objects.filter(is_active=True)
        # sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
        # total = sum_comptes['total']
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
                # msg_succes = True
            # return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations,'msg_succes':msg_succes})
            return redirect ('home')

        return render (request, self.template_name)
    

class AvanceTravailPageView(View):

    template_name = 'transaction/avance_travail.html'

    def get(self, request, id):
        comptes = Compte.objects.filter(is_active=True)
        travail = Travail.objects.get(id=id)
        
        return render (request, self.template_name, {'comptes':comptes,'travail':travail})

    def post(self, request, id):
        
        # operations = Operation.objects.all().order_by('-date')
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
                # msg_succes = True
                # sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
                # total = sum_comptes['total']
            # return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations,'msg_succes':msg_succes})
            return redirect ('home')

        return render (request, self.template_name, {'comptes':comptes,'travail':travail})
    
class DepenseTravailPageView(View):

    template_name = 'transaction/depense_travail.html'
    msg_error = False

    def get(self, request, id):
        comptes = Compte.objects.filter(is_active=True)
        travail = Travail.objects.get(id=id)
        
        return render (request, self.template_name, {'comptes':comptes,'travail':travail})

    def post(self, request, id):

        # operations = Operation.objects.all().order_by('-date')
        comptes = Compte.objects.filter(is_active=True)
        travail = Travail.objects.get(id=id)

        if request.method == 'POST':
            nombre_total_depense = request.POST.get("nombre_total_depense")
            nombre_total_depense = int(nombre_total_depense)
            description = request.POST.get("description")
            compte_id = request.POST.get("compte_emetteur")
            # si c'est une dépense unique
            if nombre_total_depense < 2:
                montant = request.POST.get("montant")
                # msg error si le montant ou le code ne sont pas saisi
                if montant == '' or compte_id == '':
                    msg_error = True
                    return render(request, self.template_name, {'comptes':comptes,'travail':travail, 'msg_error':msg_error})
                else:
                    montant = int(montant)
                    compte_id = int(compte_id)
                    compte = Compte.objects.get(id=compte_id)
                    # annulation du retrait si le montant est inferieur a zero
                    if montant <= 0 or compte.montant < montant:
                        msg_error = True
                        return render(request, self.template_name, {'comptes':comptes,'travail':travail, 'msg_error':msg_error})
                    # creation du model DepenseTravail
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
                    # creation du model Retrait
                    retrait = Retrait(
                        author = request.user,
                        compte = compte,
                        depense_travail = depense_travail,
                        montant = montant,
                    )
                    retrait.save()
                    # enregistrement de l'operation
                    operation = Operation(
                        compte = compte,
                        author = request.user,
                        type_operation = 'Dépense sur travail',
                        description = description,
                        montant = montant,
                        depense_travail = depense_travail,
                    )
                    operation.save()
                    # msg_succes = True
                    # sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
                    # total = sum_comptes['total']
                # return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations,'msg_succes':msg_succes})
                return redirect ('home')
            else:
                # si c'est une depense détaillée
                montant_total = 0
                i = nombre_total_depense
                if compte_id == '':
                    msg_error = True
                    return render(request, self.template_name, {'comptes':comptes,'travail':travail,'msg_error':msg_error})
                
                compte_id = int(compte_id)
                compte = Compte.objects.get(id=compte_id)
                # creation de la depense principal
                depense_travail = DepenseTravail(
                        travail = travail,
                        author = request.user,
                        description = description,
                        compte = compte,
                        is_group = True,
                    )
                depense_travail.save()
                # tant que le nombre de depense est superieur a 0
                while i > 0:
                    montant_i = request.POST.get("montant{}".format(i))
                    dep_i = request.POST.get(f"dep{i}")
                    if montant_i == '':
                        msg_error = True
                        depense_travail.delete()
                        return render(request, self.template_name, {'comptes':comptes,'travail':travail,'msg_error':msg_error})
                    montant_i = int(montant_i)
                    montant_total = montant_total + montant_i
                    depense_i = DepenseDetailTravail(
                        depense_source = depense_travail,
                        depense = dep_i,
                        montant = montant_i,
                    )
                    depense_i.save()
                    depense_travail.montant = montant_total
                    i = i-1
                # annulation du retrait si le montant est inferieur a zero
                if montant_total <= 0 or compte.montant < montant_total:
                    msg_error = True
                    return render(request, self.template_name, {'comptes':comptes,'travail':travail, 'msg_error':msg_error})
                # mis a jour du compte
                compte.montant = compte.montant - montant_total
                compte.save()
                # enregistrement de la depense
                depense_travail.save()
                # creation du model Retrait
                retrait = Retrait(
                    author = request.user,
                    compte = compte,
                    depense_travail = depense_travail,
                    montant = montant_total,
                )
                retrait.save()
                # enregistrement de l'operation
                operation = Operation(
                    compte = compte,
                    author = request.user,
                    type_operation = 'Dépenses détaillées',
                    description = description + f' (Plusieurs dépenses)',
                    montant = montant_total,
                    depense_travail = depense_travail,
                )
                operation.save()
                # msg_succes = True
                sum_comptes = Compte.objects.filter(is_active=True).aggregate(total=Sum('montant'))
                # total = sum_comptes['total']

            # return render (request,'transaction/home.html', {'comptes':comptes,'total':total,'operations':operations,'msg_succes':msg_succes})
            return redirect ('home')

        return render (request, self.template_name, {'comptes':comptes,'travail':travail})
    
class AllOperations(View):

    template_name = 'transaction/all_operations.html'
    operations = Operation.objects.all().order_by('-date')

    def get(self, request):
        
        return render (request, self.template_name, {'operations':self.operations})
    
    def post(self, request):

        if request.method == 'POST':

            date_debut = request.POST.get("debut")
            date_fin = request.POST.get("fin")

            # au cas ou rien n'est saisi
            if date_debut == '' and date_fin == '':
                return render (request, self.template_name, {'operations':self.operations})
            
            # au cas ou c'est la date debut seulement qui est saisi
            if date_fin == '':
                operations = Operation.objects.filter(date__gte=date_debut)
                return render (request, self.template_name, {'operations':operations})
            
            # au cas ou c'est la date fin seulement qui est saisi
            if date_debut == '':
                operations = Operation.objects.filter(date__lte=date_fin)
                return render (request, self.template_name, {'operations':operations})
            
            # au cas ou la date debut et la date fin sont saisies
            operations = Operation.objects.filter(date__gte=date_debut,date__lte=date_fin)

        return render (request, self.template_name, {'operations':operations})
    

class AddDepenseFixe(View):

    template_name = 'transaction/add_depense_fixe.html'

    def get(self, request):
        
        return render (request, self.template_name)

    def post(self, request):

        if request.method == 'POST':
            titre = request.POST.get("titre")
            description = request.POST.get("description")
            montant = request.POST.get("montant")
            # si le montant n'est pas saisi initialiser a zero
            if montant == '' or titre == '':
                msg_error = True
                return render(request, self.template_name, {'msg_error':msg_error})
            else:
                montant = int(montant)
                # creation du model Depense
                depense = Depense(
                    titre = titre,
                    description = description,
                    montant = montant,
                    fixe = True,
                )
                depense.save()

                return redirect ('depense')

        return render (request, self.template_name)
    
    
class DepenseFixe(View):

    template_name = 'transaction/depense_fixe.html'

    def get(self, request, id):

        depense_fixe = Depense.objects.get(id=id)
        
        return render (request, self.template_name, {'depense_fixe':depense_fixe})

    def post(self, request, id):
        depense_fixe = Depense.objects.get(id=id)

        if request.method == 'POST':
            titre = request.POST.get("titre")
            description = request.POST.get("description")
            montant = request.POST.get("montant")
            # si le montant n'est pas saisi initialiser a zero
            if montant == '' or titre == '':
                msg_error = True
                return render(request, self.template_name, {'msg_error':msg_error})
            else:
                montant = int(montant)
                # creation du model Depense
                depense_fixe.titre = titre
                depense_fixe.description = description
                depense_fixe.montant = montant
                depense_fixe.save()

                return redirect ('depense')

        return render (request, self.template_name)
    

@login_required
def delete_depense_fixe(request, id):

    depense_fixe = Depense.objects.get(id=id)
    depense_fixe.delete()

    return redirect ('depense')
