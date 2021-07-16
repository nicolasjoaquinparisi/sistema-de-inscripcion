from django.core.exceptions import ValidationError
from django.db.models.fields import EmailField
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