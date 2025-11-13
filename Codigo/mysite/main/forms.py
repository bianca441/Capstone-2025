from django import forms
from django.contrib.auth.models import User
from .models import Perfil

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['rut', 'telefono', 'direccion', 'ciudad', 'codigo_postal', 'foto']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email']
