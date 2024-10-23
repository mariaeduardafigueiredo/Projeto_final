from django import forms
from app.models import UsuarioCustomizado, Equipamento, Emprestimo
from app.enums import TIPO_USUARIO, CATEGORIA_EPI, CARGOS, Status

from datetime import datetime


class UsuarioForm(forms.ModelForm):

    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = UsuarioCustomizado
        fields = ['nome', 'foto', 'email', 'tipo', 'cargo', 'senha']
        widgets = {
            'tipo': forms.Select(
                choices=TIPO_USUARIO, 
                attrs={
                    'class': 'form-select',
                }
            ),
            'cargo': forms.Select(
                choices=CARGOS, 
                attrs={
                    'class': 'form-select',
                }
            ),
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['senha'])  # Define a senha de forma segura
        if commit:
            usuario.save()

        return usuario


class EquipamentoForm(forms.ModelForm):

    class Meta:
        
        model = Equipamento
        fields = ['nome', 'quantidade', 'validade', 'categoria']
        widgets = {
            'quantidade': forms.NumberInput(attrs={
                'placeholder': 'Quantidade',
                'min': '1',
            }),
            'categoria': forms.Select(
                choices=CATEGORIA_EPI, 
                attrs={
                    'class': 'form-select',
                }
            ),
        }


class EmprestimoForm(forms.ModelForm):

    class Meta:
        model = Emprestimo
        fields = ['status', 'data_emprestimo', 'data_devolucao', 'quantidade', 'usuario', 'equipamento']
        widgets = {
            'quantidade': forms.NumberInput(attrs={
                'placeholder': 'Quantidade',
                'min': '1',
            }),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se o formulário é para criação (sem instância), filtrar os status
        if not self.instance.pk:
            self.fields['status'].choices = Status.obter_status_para_cadastro()
            # Remover o campo 'data_devolucao' do formulário
            self.fields.pop('data_devolucao', None)
        else:
            # No formulário de atualização, definir valor inicial de data_devolucao como datetime.now()
            if not self.instance.data_devolucao:
                self.fields['data_devolucao'].initial = datetime.now()


    def save(self, commit=True):
        # Se o formulário é de criação, definir data_devolucao como None
        if not self.instance.pk:
            self.instance.data_devolucao = None

        return super().save(commit=commit)
    