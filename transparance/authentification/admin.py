from django.contrib import admin
from authentification.models import User

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "password",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_active",
        "post",
        "tel",
    )

admin.site.register(User, UserAdmin)