from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from app.enums import TIPO_USUARIO, CATEGORIA_EPI, CARGOS, Status

import pytz


def obter_data_atual() -> datetime:
    return datetime.now(pytz.timezone('UTC'))


class UsuarioCustomizado(AbstractUser):
    
    # Colunas da tabela 'UsuarioCustomizado'
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=255)
    foto = models.CharField(max_length=255)
    tipo = models.CharField(max_length=60, choices=TIPO_USUARIO)
    cargo = models.CharField(max_length=60, choices=CARGOS)
    data_admissao = models.DateTimeField(default=obter_data_atual)

    def save(self, *args, **kwargs) -> None:

        # NOTE: O Django obriga a ter um 'username'
        if not self.username:  
            self.username = self.email  

        super().save(*args, **kwargs)

        # Atribuindo 'Roles' aos Usuários
        if self.tipo == TIPO_USUARIO['Administrador']:
            admin_group = Group.objects.get(name='Admin')
            self.groups.add(admin_group)
        elif self.tipo == TIPO_USUARIO['Supervisor']:
            supervisor_group = Group.objects.get(name='Supervisor')
            self.groups.add(supervisor_group)
        elif self.tipo == TIPO_USUARIO['Colaborador']:
            colaborador_group = Group.objects.get(name='Colaborador')
            self.groups.add(colaborador_group)

        super().save(*args, **kwargs)


    def verificar_senha(self, senha) -> bool:
        return check_password(senha, self.password)


    def __str__(self) -> str:

        return self.nome
    

class Equipamento(models.Model):

    # Colunas 
    nome = models.CharField(max_length=255) 
    quantidade = models.PositiveIntegerField(default=1)
    validade = models.DateTimeField(default=datetime.now)
    categoria = models.CharField(max_length=100, choices=CATEGORIA_EPI)


    def __str__(self) -> str:
        return self.nome
    

class Emprestimo(models.Model):

    # Colunas
    data_emprestimo = models.DateTimeField(default=datetime.now)
    data_devolucao = models.DateTimeField(null=True)
    quantidade = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices(), default=Status.EMPRESTADO.value)

    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    usuario = models.ForeignKey(UsuarioCustomizado, on_delete=models.CASCADE)


    def __str__(self) -> str:
        return str(self.data_emprestimo)
