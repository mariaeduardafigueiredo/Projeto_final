from django.contrib import admin
from app.models import UsuarioCustomizado, Equipamento, Emprestimo
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

admin.site.register(UsuarioCustomizado, UserAdmin)
admin.site.register(Equipamento)
admin.site.register(Emprestimo)
