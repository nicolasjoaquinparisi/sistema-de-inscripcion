from re import M, findall
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class AccountManager(BaseUserManager):
    def create_superuser(self, dni, first_name, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(dni, first_name, password, **other_fields)

    def create_user(self, dni, first_name, password, **other_fields):
        user = self.model(dni=dni, first_name=first_name, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_alumno(self, dni, first_name, last_name, fecha_nacimiento, password):
        if not dni:
            raise ValueError(_('You must provide an dni address'))

        alumno = self.model(dni=dni, first_name=first_name,
                             last_name=last_name, fecha_nacimiento=fecha_nacimiento)
        alumno.set_password(password)
        alumno.save()
        return alumno


class BaseModel(models.Model):
    class Meta:
        abstract = True
    
    is_active = models.BooleanField(default=True)
    
    def delete(self):
        if self.is_active:
            self.is_active = False
            self.save()
    
    @classmethod
    def find_all(cls, qobject=None):
        if qobject:
            qobject &= models.Q(is_active=True)
        else:
            qobject = models.Q(is_active=True)

        return cls.objects.filter(qobject)

    @classmethod
    def find_first(cls, qobject=None):
        query = cls.find_all(qobject)
        if query.exists():
            instance = query.first()
        else:
            instance = None
        
        return instance
    
    @classmethod
    def find_pk(cls, pk):
        return cls.find_first(models.Q(pk=pk))


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    dni              = models.IntegerField(unique=True)
    first_name       = models.CharField(max_length=150, blank=True)
    last_name        = models.CharField(max_length=150, blank=True)
    is_staff         = models.BooleanField(default=False)
    is_active        = models.BooleanField(default=True)
    
    objects = AccountManager()

    USERNAME_FIELD = 'dni'
    REQUIRED_FIELDS = ['first_name', 'last_name']


class Alumno(User):
    fecha_nacimiento = models.DateTimeField()
    fecha_de_alta    = models.DateField()
    domicilio        = models.CharField(max_length=150, blank=True)
    legajo           = models.IntegerField()

    def __str__(self):
        return f'\'{self.last_name}\', \'{self.first_name}\''
    
    @property
    def descripcion(self):
        return f'\'{self.first_name}\', \'{self.last_name}\' \'({self.legajo})\''
    

class Carrera(BaseModel):
    nombre = models.CharField(max_length=50, blank=False, unique=True)


class Materia(BaseModel):
    codigo            = models.CharField(max_length=50, blank=False, unique=True, null=False)
    codigo_de_carrera = models.ForeignKey(Carrera, on_delete=models.SET_NULL, null=True)
    nombre            = models.CharField(max_length=150, blank=False)
    año               = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return f'({self.codigo}) {self.nombre}'

    @classmethod
    def crear_materia(cls, data, año):
        materia = Materia()
        materia.codigo = data['codigo']
        materia.nombre = data['nombre']
        materia.año    = año
        materia.save()
        return materia

    @classmethod
    def puede_dar_de_alta(cls, codigo, nombre):
        return cls.codigo_valido(codigo) and cls.nombre_valido(nombre)
    
    @classmethod
    def codigo_valido(cls, codigo):
        return cls.find_first(models.Q(codigo=codigo)) == None
    
    @classmethod
    def nombre_valido(cls, nombre):
        return cls.find_first(models.Q(nombre=nombre)) == None
    
    @classmethod
    def get_mensaje_de_error(cls, codigo, nombre):
        if not cls.codigo_valido(codigo):
            return 'El código ingresado se encuentra en uso.'
        if not cls.nombre_valido(nombre):
            return 'El nombre ingresado se encuentra en uso.'
        return 'Se ha producido un error.'


class Correlatividades(BaseModel):
    codigo_de_materia     = models.ForeignKey(Materia, on_delete=models.SET_NULL, null=True, related_name='codigo_de_materia')
    codigo_de_correlativa = models.ForeignKey(Materia, on_delete=models.SET_NULL, null=True, related_name='codigo_de_correlativa')


class MateriasInscriptas(BaseModel):
    alumno            = models.ForeignKey(Alumno, on_delete=models.SET_NULL, null=True)
    codigo_de_materia = models.ForeignKey(Materia, on_delete=models.SET_NULL, null=True)


class MateriasAprobadas(BaseModel):
    alumno            = models.ForeignKey(Alumno, on_delete=models.SET_NULL, null=True)
    codigo_de_materia = models.ForeignKey(Materia, on_delete=models.SET_NULL, null=True)