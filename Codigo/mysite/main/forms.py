import os

from django import forms
from django.contrib.auth.models import User

from .models import Perfil, CuentaBanco, CategoriaGasto


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['rut', 'telefono', 'direccion', 'ciudad', 'codigo_postal']
        labels = {
            'rut': 'RUT',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
            'codigo_postal': 'Código Postal',
        }
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '12.345.678-9'}),
            'telefono': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+56 9 1234 5678'}),
            'direccion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Calle y número'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ciudad'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '0000000'}),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email']
        labels = {
            'first_name': 'Nombre',
            'email': 'Correo electrónico',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tu nombre'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'correo@ejemplo.com'}),
        }


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['profile_image']
        labels = {'profile_image': 'Nueva foto'}
        widgets = {
            'profile_image': forms.ClearableFileInput(
                attrs={
                    'class': 'form-input',
                    'accept': '.jpg,.jpeg,.png',
                }
            )
        }

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if not image:
            raise forms.ValidationError("Selecciona una imagen para continuar.")

        ext = os.path.splitext(image.name)[1].lower()
        if ext not in ('.jpg', '.jpeg', '.png'):
            raise forms.ValidationError("Solo se permiten imágenes JPG o PNG.")
        return image


class CuentaBancoForm(forms.ModelForm):
    class Meta:
        model = CuentaBanco
        fields = ['numero_cuenta', 'banco', 'nombre_identificador', 'saldo_inicial']
        labels = {
            'numero_cuenta': 'Número de cuenta',
            'banco': 'Banco',
            'nombre_identificador': 'Nombre identificador',
            'saldo_inicial': 'Saldo inicial',
        }
        widgets = {
            'numero_cuenta': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '123456789'}),
            'banco': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Banco Estado'}),
            'nombre_identificador': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Cuenta corriente sueldo'}),
            'saldo_inicial': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
        }


class CategoriaGastoForm(forms.ModelForm):
    class Meta:
        model = CategoriaGasto
        fields = ['nombre', 'descripcion', 'tipo', 'color']
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción (opcional)',
            'tipo': 'Tipo',
            'color': 'Color',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Alimentación'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Detalle para identificarla fácilmente', 'maxlength': '255'}),
            'tipo': forms.Select(attrs={'class': 'form-input'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-input', 'style': 'height: 48px; padding: 0 8px;'}),
        }
