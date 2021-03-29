from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import MyUser


class MyUserInline(admin.StackedInline):
    model = MyUser
    can_delete = False
    verbose_name_plural = 'Дополнительные данные'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (MyUserInline,)
    list_display = ('username', 'email', 'get_phone_number', 'get_confirm_email')

    def get_phone_number(self, obj):
        return obj.myuser.phone_number

    def get_confirm_email(self, obj):
        return obj.myuser.confirm_email

    get_phone_number.short_description = 'Телефон'
    get_confirm_email.short_description = 'Пользователь подтвержден'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
