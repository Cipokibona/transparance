from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from authentification.models import User


@login_required
def home (request):

    return render (request,'transaction/home.html')


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
