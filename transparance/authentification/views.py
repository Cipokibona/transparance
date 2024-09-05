from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import login, authenticate, logout

# Create your views here.


class LoginPageView(View):
    template_name = 'authentification/index.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        msg_error = False
        if request.method == 'POST':
            username = request.POST.get("username")
            password = request.POST.get("password")
            if username and password:
                try:
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        login(request, user)
                        return redirect('home')
                    else:
                        msg_error = True
                except Exception as e:
                    msg_error = True
        return render(request, self.template_name, context={'msg_error': msg_error})

def logout_user(request):
    
    logout(request)
    return redirect('login')