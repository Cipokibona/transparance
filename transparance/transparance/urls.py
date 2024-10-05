"""
URL configuration for transparance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from authentification import views as auth
from transaction import views as trans

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth.LoginPageView.as_view(), name='login'),
    path('home/', trans.home, name='home'),
    path('logout/', auth.logout_user, name='logout'),
    path('travail/', trans.TravailPagerView.as_view(), name='travail'),
    path('profil/', trans.ProfilPageView.as_view(), name='profil'),
    path('new_user/', trans.NewUserPageView.as_view(), name='new_user'),
    path('transaction/', trans.TransactionPageView.as_view(), name='transaction'),
    path('new_compte/', trans.NewComptePageView.as_view(), name='new_compte'),
    path('depense/', trans.NewRetraitView.as_view(), name='depense'),
    path('avance_travail/<int:id>/', trans.AvanceTravailPageView.as_view(), name='avance_travail'),
    path('depense_travail/<int:id>/', trans.DepenseTravailPageView.as_view(), name='depense_travail'),
    path('operation/<int:id>/', trans.operation, name='operation'),
    path('delete_operation/<int:id>/', trans.annuler, name='delete_operation'),
    path('all_operations/', trans.AllOperations.as_view(), name='all_operations'),
    path('add_depense_fixe/', trans.AddDepenseFixe.as_view(), name='add_depense_fixe'),
    path('depense_fixe/<int:id>/', trans.DepenseFixe.as_view(), name='depense_fixe'),
    path('delete_depense_fixe/<int:id>/', trans.delete_depense_fixe, name='delete_depense_fixe'),
]
