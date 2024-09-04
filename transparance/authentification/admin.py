from django.contrib import admin
from authentification.models import Personnel

# Register your models here.

class PersonnelAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "name",
        "username",
        "password",
        "post",
        "active",
    )

admin.site.register(Personnel, PersonnelAdmin)