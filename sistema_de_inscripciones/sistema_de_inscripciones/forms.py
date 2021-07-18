from django.core.exceptions import ValidationError
from django.db.models.fields import EmailField
from django.forms import widgets
from django.forms.widgets import Input
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm, EmailInput, TextInput, Select, ChoiceField, DateInput, CharField, ModelChoiceField, \
    IntegerField
from django.forms import forms
from datetime import datetime
from sistema_de_inscripciones.models import *


class LoginForm(ModelForm):
    class Meta:
        model = User

        fields = {'dni', 'password'}

        widgets = {
            'dni' : TextInput(attrs={'type': 'number', 'class': 'form-control', 'id' : 'inputDNI'
                                        , 'placeholder' : 'Ingresa aquí tu DNI', 'required': 'True'}),
            'password': TextInput(attrs={'type' : 'password','class': 'form-control', 'id' : 'inputPassword',
                                        'placeholder' : 'Ingresa aquí tu contraseña', 'required': 'True'}),
        }


class AltaMateriaForm(ModelForm):
    class Meta:
        model = Materia

        fields = {'codigo', 'nombre'}

        widgets = {
            'codigo' : TextInput(attrs={'type': 'text', 'class': 'form-control', 'id' : 'input-codigo'
                                        , 'placeholder' : 'Ingrese el codigo de la materia', 'required': 'True'}),
            'nombre' : TextInput(attrs={'type': 'text', 'class': 'form-control', 'id' : 'input-nombre'
                                        , 'placeholder' : 'Ingrese el nombre de la materia', 'required': 'True'}),
        }
    
    def puede_dar_de_alta(self):
        return Materia.puede_dar_de_alta(self.data['codigo'], self.data['nombre'])

    def validar_materia(self):
        if not self.puede_dar_de_alta():
            return False, Materia.get_mensaje_de_error(self.data['codigo'], self.data['nombre'])

        self.is_valid()
        return True, 'Se dió de alta a la materia de forma exitosa'