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

        fields = {'email', 'password'}

        widgets = {
            'email' : EmailInput(attrs={'type': 'email', 'class': 'form-control', 'id' : 'inputEmail'
                                        , 'placeholder' : 'Ingresa aquí tu email', 'required': 'True'}),
            'password': TextInput(attrs={'type' : 'password','class': 'form-control', 'id' : 'inputPassword',
                                        'placeholder' : 'Ingresa aquí tu contraseña', 'required': 'True'}),
        }

    def validar_login(self):
        if self.campos_vacios():
            return False

    def campos_vacios(self):
        if not self.data['email'] or not self.data['password']:
            return True
        return False