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
        
        return render(request, self.template_name, context={'msg_error': msg_error})
