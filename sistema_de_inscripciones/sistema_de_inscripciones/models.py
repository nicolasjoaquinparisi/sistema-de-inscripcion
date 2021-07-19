from re import M, findall
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.html import conditional_escape
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
    
    @property
    def get_correlatividades(self):
        correlativas = Correlatividades.find_all(models.Q(codigo_de_materia=self))
        if len(correlativas) == 0:
            return "-"

        materias_correlativas = []
        for c in correlativas:
            materias_correlativas.append(c.codigo_de_correlativa)

        return materias_correlativas

    '''
    Recibe el request.POST enviado desde la view
    Genera una lista con todos los códigos de las correlativas seleccionadas
    Crea las instancias de las correlativas de la materia dada de alta
    '''
    @classmethod
    def crear_correlativas(cls, materia, post):
        correlativas = []
        for i in range(3, len(post)-1):
            correlativas.append(post[i])
        
        for correlativa in correlativas:
            correlativa = correlativa[correlativa.find("(")+1:correlativa.find(")")]
            c = Correlatividades.crear_correlativa(materia, correlativa)

    @classmethod
    def crear_materia(cls, data, año, post):
        materia = Materia()
        materia.codigo = data['codigo']
        materia.nombre = data['nombre']
        materia.año    = año
        materia.save()

        '''
        Se verifica si la materia tiene correlatividades
        Si el request.POST tiene 4 elementos, entonces es porque no tiene correlativas la materia
        (El primer elemento es el codigo, el segundo, el nombre, el tercero, el año y el último el token)
        '''
        if len(post) > 4:
            cls.crear_correlativas(materia, post)

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

    @classmethod
    def crear_correlativa(cls, materia, codigo):
        correlativa = Correlatividades()
        correlativa.codigo_de_materia = materia

        #Se busca la materia correlativa a partir del codigo obtenido
        materia = Materia.find_first(models.Q(codigo=codigo))
        correlativa.codigo_de_correlativa = materia

        correlativa.save()


class MateriasInscriptas(BaseModel):
    alumno            = models.ForeignKey(Alumno, on_delete=models.SET_NULL, null=True)
    codigo_de_materia = models.ForeignKey(Materia, on_delete=models.SET_NULL, null=True)


class MateriasAprobadas(BaseModel):
    alumno            = models.ForeignKey(Alumno, on_delete=models.SET_NULL, null=True)
    codigo_de_materia = models.ForeignKey(Materia, on_delete=models.SET_NULL, null=True)