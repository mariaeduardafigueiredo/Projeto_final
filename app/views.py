from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest

from app.models import UsuarioCustomizado, Equipamento, Emprestimo
from app.forms import UsuarioForm, EquipamentoForm, EmprestimoForm
from app.enums import TIPO_USUARIO
from django.contrib.auth.decorators import login_required


def home(request: WSGIRequest) -> HttpResponse:
    return render(request, 'home.html', status=200)


def contato(request: WSGIRequest) -> HttpResponse:
    return render(request, 'contato.html', status=200)


def logar(request: WSGIRequest) -> HttpResponse:

    if request.method == 'POST':
        _email = request.POST.get('email')
        _senha = request.POST.get('senha') 

        try:
            usuario = UsuarioCustomizado.objects.get(email=_email) 

            if usuario.verificar_senha(_senha):
                login(request, usuario)
                return redirect(home)
            else:
                messages.error(request, 'Login ou Senha inválidos')

        except UsuarioCustomizado.DoesNotExist:
            messages.error(request, 'Usuário inexistente!')

    return render(request, 'login.html', status=200)


def cadastrar(request: WSGIRequest) -> HttpResponse:

    if request.method == 'POST':
        form = UsuarioForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            #return redirect(logar)
    else:
        form = UsuarioForm()

    return render(request, 'cadastro.html', {'form': form}, status=200)


@login_required()
def interno(request: WSGIRequest) -> HttpResponse:
    user_groups: list[str] = []
    infos: list[str] = []

    if request.user.is_authenticated:
        user_groups = request.user.groups.values_list('name', flat=True)

        infos = [
            f"Seja Bem Vindo!",
        ]

    context = {
        'user_groups': user_groups,
        'infos': infos
    }
    return render(request, 'interno/interno.html', context, status=200)


@login_required()
def obter_usuarios(request: WSGIRequest) -> HttpResponse: 
    user: UsuarioCustomizado = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.warning(request, 'Você não está logado!')
        return redirect(login)


    # Verifica o 'ROLE' do 'Usuário' não é 'Admin'
    if not user.groups.filter(name='Admin').exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(home)    
    


    query = request.GET.get('search')
    if query:
        usuarios: list[UsuarioCustomizado] = UsuarioCustomizado.objects.filter(nome__icontains=query)
    else:
        usuarios: list[UsuarioCustomizado] = UsuarioCustomizado.objects.all()


    user_groups = request.user.groups.values_list('name', flat=True)
    context = {
        'user_groups': user_groups,
        'usuarios': usuarios
    }
        
    return render(request, 'usuarios/usuarios.html', context, status=200)
    

@login_required()
def deletar_usuario(request: WSGIRequest, id: int) -> HttpResponse:
    user: UsuarioCustomizado = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.warning(request, 'Você não está logado!')
        return redirect(login)

    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin'
    if not user.groups.filter(name='Admin').exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(home)    


    usuario: UsuarioCustomizado = get_object_or_404(UsuarioCustomizado, id=id)
    usuario.delete()

    return redirect(obter_usuarios) # 204 No Content


@login_required()
def atualizar_usuario(request: WSGIRequest, id: int) -> HttpResponse:
    user: UsuarioCustomizado = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.warning(request, 'Você não está logado!')
        return redirect(login)

    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin'
    if not user.groups.filter(name='Admin').exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(login)
    

    usuario: UsuarioCustomizado = get_object_or_404(UsuarioCustomizado, id=id) 
    infos: list[str] = []

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()  
            return redirect(obter_usuarios) # 200 OK ou 204 No Content

        infos.append("Formulário Inválido!")
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'usuarios/atualizar_usuario.html', {'form': form, 'usuario': usuario}, status=200)


@login_required()
def criar_usuario(request: WSGIRequest) -> HttpResponse:
    user: UsuarioCustomizado = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.warning(request, 'Você não está logado!')
        return redirect(login)

    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin'
    if not user.groups.filter(name='Admin').exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(login)


    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(obter_usuarios) # 201 Created
    else:
        form = UsuarioForm()

    return render(request, 'usuarios/criar_usuario.html', {'form': form}, status=200)


@login_required()
def obter_equipamentos(request: WSGIRequest) -> HttpResponse:
    user: UsuarioCustomizado = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.warning(request, 'Você não está logado!')
        return redirect(login)


    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin' ou 'Supervisor'
    if not user.groups.filter(name__in=['Admin', 'Supervisor']).exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(home)   


    query = request.GET.get('search')
    if query:
        equipamentos: list[Equipamento] = Equipamento.objects.filter(nome__icontains=query)
    else:
        equipamentos: list[Equipamento] = Equipamento.objects.all()


    user_groups = request.user.groups.values_list('name', flat=True)
    context = {
        'user_groups': user_groups,
        'equipamentos': equipamentos
    }

    return render(request, 'equipamentos/equipamentos.html', context=context, status=200)


@login_required()
def deletar_equipamento(request: WSGIRequest, id: int) -> HttpResponse:
    user: UsuarioCustomizado = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.warning(request, 'Você não está logado!')
        return redirect(login)

    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin' ou 'Supervisor'
    if not user.groups.filter(name__in=['Admin', 'Supervisor']).exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(home)    


    equipamento: Equipamento = get_object_or_404(Equipamento, id=id)
    equipamento.delete()

    return redirect(obter_equipamentos) # 204 No Content


@login_required()
def atualizar_equipamento(request: WSGIRequest, id: int) -> HttpResponse:
    user: UsuarioCustomizado = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.warning(request, 'Você não está logado!')
        return redirect(login)

    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin' ou 'Supervisor'
    if not user.groups.filter(name__in=['Admin', 'Supervisor']).exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(login)


    equipamento: Equipamento = get_object_or_404(Equipamento, id=id) 
    infos: list[str] = []
    
    if request.method == 'POST':
        form = EquipamentoForm(request.POST, instance=equipamento)
        if form.is_valid():
            form.save()  
            return redirect(obter_equipamentos) # 200 OK ou 204 No Content

        infos.append("Formulário Inválido!")

    else:
        form = EquipamentoForm(instance=equipamento)

    return render(request, 'equipamentos/atualizar_equipamento.html', {'form': form, 'equipamento': equipamento}, status=200)


@login_required()
def criar_equipamento(request: WSGIRequest) -> HttpResponse:
    user: UsuarioCustomizado = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.warning(request, 'Você não está logado!')
        return redirect(login)

    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin' ou 'Supervisor'
    if not user.groups.filter(name__in=['Admin', 'Supervisor']).exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(login)


    if request.method == 'POST':
        form = EquipamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(obter_equipamentos) # 201 Created
    else:
        form = EquipamentoForm()

    return render(request, 'equipamentos/criar_equipamento.html', {'form': form}, status=200)


@login_required()
def obter_emprestimos(request: WSGIRequest) -> HttpResponse:
    user: UsuarioCustomizado = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.warning(request, 'Você não está logado!')
        return redirect(login)


    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin' ou 'Supervisor' ou 'Colaborador'
    if not user.groups.filter(name__in=['Admin', 'Supervisor', 'Colaborador']).exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(home)   


    query = request.GET.get('search')
    if query:
        emprestimos: list[Emprestimo] = Emprestimo.objects.filter(status__icontains=query)
    else:
        emprestimos: list[Emprestimo] = Emprestimo.objects.all()


    user_groups = request.user.groups.values_list('name', flat=True)
    context = {
        'user_groups': user_groups,
        'emprestimos': emprestimos
    }

    return render(request, 'emprestimos/emprestimos.html', context=context, status=200)


@login_required()
def deletar_emprestimo(request: WSGIRequest, id: int) -> HttpResponse:
    user: UsuarioCustomizado = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.warning(request, 'Você não está logado!')
        return redirect(login)

    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin' ou 'Supervisor' ou 'Colaborador'
    if not user.groups.filter(name__in=['Admin', 'Supervisor', 'Colaborador']).exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(home)    


    emprestimo: Emprestimo = get_object_or_404(Emprestimo, id=id)
    emprestimo.delete()

    return redirect(obter_emprestimos) # 204 No Content


@login_required()
def atualizar_emprestimo(request: WSGIRequest, id: int) -> HttpResponse:
    user: UsuarioCustomizado = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.warning(request, 'Você não está logado!')
        return redirect(login)

    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin' ou 'Supervisor' ou 'Colaborador'
    if not user.groups.filter(name__in=['Admin', 'Supervisor', 'Colaborador']).exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(login)


    emprestimo: Emprestimo = get_object_or_404(Emprestimo, id=id) 
    infos: list[str] = []
    
    if request.method == 'POST':

        # Verifica se o Usuário e o Equipamento existem
        id_usuario = request.POST.get('usuario')
        id_equipamento = request.POST.get('equipamento')
        quantidade_desejada = int(request.POST.get('quantidade', 1))

        usuario = UsuarioCustomizado.objects.filter(id=id_usuario).first()
        if not usuario:
            infos.append(f"Cliente com id={id_usuario} não existe!")

        equipamento = Equipamento.objects.filter(id=id_equipamento).first()
        if not equipamento:
            infos.append(f"Produto com id={id_equipamento} não existe!")

        # Regra de negócio
        continuar: bool = True
        # if usuario and usuario.tipo != TIPO_USUARIO.get('Colaborador'):
        #     infos.append("Somente Colaboradores podem pedir Empréstimos!")
        #     continuar = False
        

        # Obtenha a quantidade total emprestada desse equipamento, exceto o empréstimo atual
        quantidade_emprestada = Emprestimo.objects.filter(equipamento_id=id_equipamento).exclude(id=emprestimo.id).aggregate(Sum('quantidade'))['quantidade__sum']
        
        # Caso não haja nenhum empréstimo do equipamento, o valor será None, então ajustamos para 0
        if quantidade_emprestada is None:
            quantidade_emprestada = 0

        # Quantidade disponível = quantidade total no estoque - quantidade já emprestada
        quantidade_disponivel = equipamento.quantidade - quantidade_emprestada

        # Valida se a quantidade desejada é possível
        if quantidade_desejada > quantidade_disponivel:
            continuar = False
            infos.append(f"O Equipamento {equipamento.nome} não possui estoque suficiente! Disponível: {quantidade_disponivel}")
        
        print(f"Quantidade emprestada: {quantidade_emprestada}")
        print(f"Quantidade disponível: {quantidade_disponivel}")
        print(f"Quantidade desejada: {quantidade_desejada}")
        print(f"Quantidade no estoque: {equipamento.quantidade}")
        
        # Se o Usuário e Equipamento existem, e as regras foram cumpridas, atualiza o Empréstimo
        if usuario and equipamento and continuar:
            emprestimo.usuario = usuario
            emprestimo.equipamento = equipamento
            emprestimo.quantidade = quantidade_desejada
            form = EmprestimoForm(request.POST, instance=emprestimo)

            if form.is_valid():
                form.save()
                return redirect(obter_emprestimos)  # Redireciona após sucesso
            else:
                # Adiciona os erros do formulário à lista de infos
                infos.append("Formulário Inválido!")
                for field in form:
                    for error in field.errors:
                        infos.append(f"{field.label}: {error}")
        else:
            form = EmprestimoForm(instance=emprestimo)
    else:
        form = EmprestimoForm(instance=emprestimo)

    context = {
        'form': form,
        'infos': infos,
        'emprestimo': emprestimo,
    }

    return render(request, 'emprestimos/atualizar_emprestimo.html', context=context, status=200)


@login_required()
def criar_emprestimo(request: WSGIRequest) -> HttpResponse:
    user: UsuarioCustomizado = request.user

    # O Usuário está autenticado?
    if not user.is_authenticated:
        messages.warning(request, 'Você não está logado!')
        return redirect(login)

    # Verifica se o 'ROLE' do 'Usuário' não é 'Admin' ou 'Supervisor'
    if not user.groups.filter(name__in=['Admin', 'Supervisor']).exists():
        messages.warning(request, 'Você não possui permissão!')
        return redirect(login)

    if request.method == 'POST':
        id_usuario: int = request.POST.get('usuario')

        continuar: bool = True
        usuario: UsuarioCustomizado = UsuarioCustomizado.objects.filter(id=id_usuario).first()
        # if usuario.tipo != TIPO_USUARIO.get('Colaborador'):
        #     messages.warning(request, "Somente Colaboradores poder pedir Empréstimos!")
        #     continuar = False


        id_equipamento: int = request.POST.get('equipamento')
        equipamento = Equipamento.objects.get(id=id_equipamento)

        # Obtenha a quantidade total emprestada desse equipamento
        quantidade_emprestada = Emprestimo.objects.filter(equipamento_id=id_equipamento).aggregate(Sum('quantidade'))['quantidade__sum']
        # Caso não haja nenhum empréstimo do equipamento, o valor será None, então ajustamos para 0
        if quantidade_emprestada is None:
            quantidade_emprestada = 0

        # Quantidade disponível = quantidade total no estoque - quantidade emprestada
        quantidade_disponivel = equipamento.quantidade - (quantidade_emprestada + int(request.POST.get('quantidade')))

        if quantidade_disponivel < 0:
            continuar = False
            messages.warning(request, f"O Equipamento {equipamento.nome} não possui estoque!")

        form = EmprestimoForm(request.POST)

        if form.is_valid() and continuar:
            form.save()
            return redirect(obter_emprestimos) # 201 Created
    else:
        form = EmprestimoForm()


    return render(request, 'emprestimos/criar_emprestimo.html', {'form': form}, status=200)
