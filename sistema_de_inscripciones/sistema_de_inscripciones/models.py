from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class AccountManager(BaseUserManager):
    def create_superuser(self, email, first_name, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, first_name, password, **other_fields)

    def crear_user(self, email, first_name, password, **other_fields):
        user = self.model(email=email, first_name=first_name, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_alumno(self, email, first_name, last_name, dni, fecha_nacimiento, password):
        if not email:
            raise ValueError(_('You must provide an email address'))

        alumno = self.model(email=email, first_name=first_name,
                             last_name=last_name, dni=dni, fecha_nacimiento=fecha_nacimiento)
        alumno.set_password(password)
        alumno.save()
        return alumno


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    email = models.EmailField(_('Email Address'), unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name  = models.CharField(max_length=150, blank=True)
    is_staff   = models.BooleanField(default=False)
    is_active  = models.BooleanField(default=True)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email
    
    def _get_not_unique_message(self, other):
        return f'Ya existe un usuario con email \'{self.email}\'.'
    
    @classmethod
    def _get_unique_check(cls, fields):
        return models.Q(email=fields['email'])


class Alumno(User):
    dni = models.IntegerField()
    fecha_nacimiento = models.DateTimeField()