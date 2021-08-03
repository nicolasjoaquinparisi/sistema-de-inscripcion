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
    
    @classmethod
    def find_all_actives(cls, qobject=None):
        if qobject:
            qobject &= models.Q(is_active=True)
        else:
            qobject = models.Q(is_active=True)

        return cls.objects.filter(qobject)

    @classmethod
    def find_first(cls, qobject=None):
        query = cls.find_all_actives(qobject)
        if query.exists():
            instance = query.first()
        else:
            instance = None
        
        return instance
    
    @classmethod
    def find_pk(cls, pk):
        return cls.find_first(models.Q(pk=pk))
    
    @classmethod
    def find_all(cls, qobject):
        return cls.objects.filter(qobject)
    
    def delete(self):
        self.is_active = False
        self.save()

    @classmethod
    def validar(cls):
        raise NotImplementedError
    
    @classmethod
    def get_mensaje_de_error(cls):
        raise NotImplementedError

    @classmethod
    def get_mensaje_de_error_modificacion(cls):
        raise NotImplementedError

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    dni              = models.IntegerField(unique=True)
    first_name       = models.CharField(max_length=150, blank=True)
    last_name        = models.CharField(max_length=150, blank=True)
    is_staff         = models.BooleanField(default=False)
    is_active        = models.BooleanField(default=True)
    
    objects = AccountManager()

    USERNAME_FIELD = 'dni'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Alumno(User):
    fecha_nacimiento = models.DateTimeField()
    fecha_de_alta    = models.DateField()
    domicilio        = models.CharField(max_length=150, blank=True)
    legajo           = models.IntegerField()
    
    @property
    def descripcion(self):
        return f'\'{self.first_name}\', \'{self.last_name}\' \'({self.legajo})\''
    

class Carrera(BaseModel):
    nombre      = models.CharField(max_length=50, blank=False, unique=True)
    descripcion = models.CharField(max_length=2000, blank=True)
    año         = models.CharField(max_length=10, blank=False)

    @classmethod
    def crear_carrera(cls, post):
        carrera             = Carrera()
        carrera.nombre      = post['nombre']
        carrera.descripcion = post['descripcion']
        carrera.año         = post['radio-button-año']
        carrera.save()

        "Se genera una lista con las referencias a las materias dadas de altas que se seleccionaron y se generan las asociaciones"
        materias = cls.get_materias(post)
        cls.asociar_materias(carrera, materias)

        return carrera
    
    '''
    Se crean las instancias correspondientes a las materias de la carrera
    post = [nombre, descripcion, año,   TODAS LAS MATERIAS,         token]
            0           1         2     a partir de pos = 3     post = length
    '''
    @classmethod
    def asociar_materias(cls, carrera, materias):
        for materia in materias:
            codigo  = materia[materia.find("(")+1:materia.find(")")]
            materia = Materia.find_first(models.Q(codigo=codigo))
            c = CarreraMaterias.crear_asociacion(carrera, materia)

    ''' Validaciones - Inicio'''
    @classmethod
    def validar(cls, nombre):
        if cls.nombre_valido(nombre):
            return True, 'Se dió de alta a la carrera de forma exitosa'
        return False, Carrera.get_mensaje_de_error(nombre)

    @classmethod
    def nombre_valido(cls, nombre):
        existe = Carrera.objects.filter(nombre=nombre).exists()
        if not existe:
            return True

        carrera = Carrera.objects.filter(nombre=nombre).first()
        if carrera and carrera.is_active == False:
            Carrera.find_all(models.Q(nombre=nombre)).delete()
            return True

        return False
    
    @classmethod
    def get_mensaje_de_error(cls, nombre):
        if not cls.nombre_valido(nombre):
            return 'El nombre ingresado se encuentra en uso.'
        return 'Se ha producido un error.'
    
    ''' Validaciones - Fin'''   
        
    
    '''
    Recibe el request.POST enviado desde la view
    Genera una lista con todos los códigos de las correlativas seleccionadas
    Crea las instancias de las correlativas de la materia dada de alta
    '''
    @classmethod
    def get_materias(cls, post):
        post = list(post)
        materias = []
        for i in range(3, len(post)-1):
            materias.append(post[i])
        return materias
    
    @classmethod
    def find_carrera(cls, carrera_id):
        return Carrera.find_pk(carrera_id)

    @property
    def materias(self):
        return CarreraMaterias.get_materias(self)
    
    def materias_de_año(self, año):
        materias = self.materias

        materias_año = []
        for materia in materias:
            if materia.año == año:
                materias_año.append(materia)

        return materias_año


class Materia(BaseModel):
    codigo            = models.CharField(max_length=50, blank=False, unique=True, null=False)
    nombre            = models.CharField(max_length=150, blank=False)
    año               = models.CharField(max_length=50, blank=False)
    semestre          = models.CharField(max_length=30, blank=False)

    def __str__(self):
        return f'({self.codigo}) {self.nombre}'
    
    @classmethod
    def set_values(cls, materia, post):
        materia.codigo    = post['input-codigo']
        materia.nombre    = post['input-nombre']
        materia.año       = post.get('radio-button-año', 'value')
        materia.semestre  = post.get('radio-button-semestre', 'value')
        materia.save()

    @classmethod
    def crear_materia(cls, post):
        materia = Materia()
        cls.set_values(materia, post)
        cls.crear_correlativas(materia, list(post))
    
    '''
    Recibe el request.POST enviado desde la view
    Genera una lista con todos los códigos de las correlativas seleccionadas
    Crea las instancias de las correlativas de la materia dada de alta
    '''
    @classmethod
    def crear_correlativas(cls, materia, post):
        correlativas = []
        for i in range(4, len(post)-1):
            correlativas.append(post[i])
        
        for correlativa in correlativas:
            correlativa = correlativa[correlativa.find("(")+1:correlativa.find(")")]
            c = Correlatividades.crear_correlativa(materia, correlativa)
    
    ''' Validaciones - Inicio '''
    @classmethod
    def validar(cls, codigo, nombre):
        if cls.puede_dar_de_alta(codigo, nombre):
            return True, 'Se dió de alta a la materia de forma exitosa'
        return False, Materia.get_mensaje_de_error(codigo, nombre) 

    @classmethod
    def puede_dar_de_alta(cls, codigo, nombre):
        existe = cls.objects.filter(codigo=codigo).exists()
        if not existe:
            return True
        else:
            materia = cls.objects.filter(codigo=codigo).first()
            if materia.is_active == False:
                cls.find_all(models.Q(codigo=codigo)).delete()
                return True

        return False
    
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
    

    def validar_modificacion(self, codigo, nombre):
        validaciones = {'codigo' : self.validar_modificacion_codigo(codigo),
                        'nombre' : self.validar_modificacion_nombre(nombre)}
        
        if not validaciones['codigo']:
            return False, 'El código ingresado pertenece a otra materia'

        if not validaciones['nombre']:
            return False, 'El nombre ingresado pertenece a otra materia'
        
        return True, 'Se realizó la modificación de la materia de forma exitosa'
    
    def validar_modificacion_codigo(self, codigo):
        #Si es la misma materia
        if self.codigo == codigo:
            return True
        
        existe = Materia.objects.filter(codigo=codigo).exists()
        if existe:
            materia = Materia.objects.filter(codigo=codigo).first()

            #Si es la misma materia
            if materia.pk == self.pk:
                return True

            #Si hay una materia dada de baja lógicamente con el mismo código
            if materia.is_active == False:
                Materia.objects.filter(codigo=codigo).delete()
                return True
            else:
                return False

        return True
    
    def validar_modificacion_nombre(self, nombre):
        if self.nombre == nombre:
            return True

        existe = Materia.objects.filter(nombre=nombre).exists()
        if existe:
            materia = Materia.objects.filter(nombre=nombre).first()

            #Si es la misma materia
            if materia.pk == self.pk:
                return True

            if materia.is_active == False:
                Materia.objects.filter(nombre=nombre).delete()
                return True
            else:
                return False

        return True

    ''' Validaciones - Fin '''

    @classmethod
    def find_all_actives_except(cls, materia):
        return cls.find_all_actives(~models.Q(codigo=materia.codigo))
    
    @classmethod
    def get_materia(cls, materia_id):
        return Materia.find_pk(materia_id)
    
    @classmethod
    def get_sorted_materias(cls):
        materias = []

        query = Materia.find_all_actives(models.Q(semestre="Curso de ingreso"))
        for materia in query:
            materias.append(materia)
        
        query = Materia.find_all_actives(models.Q(año="Primer año") & models.Q(semestre="Primer semestre"))
        for materia in query:
            materias.append(materia)
        
        query = Materia.find_all_actives(models.Q(año="Primer año") & models.Q(semestre="Segundo semestre"))
        for materia in query:
            materias.append(materia)
        
        query = Materia.find_all_actives(models.Q(año="Segundo año") & models.Q(semestre="Primer semestre"))
        for materia in query:
            materias.append(materia)
        
        query = Materia.find_all_actives(models.Q(año="Segundo año") & models.Q(semestre="Segundo semestre"))
        for materia in query:
            materias.append(materia)
        
        query = Materia.find_all_actives(models.Q(año="Tercer año") & models.Q(semestre="Primer semestre"))
        for materia in query:
            materias.append(materia)
        
        query = Materia.find_all_actives(models.Q(año="Tercer año") & models.Q(semestre="Segundo semestre"))
        for materia in query:
            materias.append(materia)
        
        query = Materia.find_all_actives(models.Q(año="Cuarto año") & models.Q(semestre="Primer semestre"))
        for materia in query:
            materias.append(materia)
        
        query = Materia.find_all_actives(models.Q(año="Cuarto año") & models.Q(semestre="Segundo semestre"))
        for materia in query:
            materias.append(materia)
        
        query = Materia.find_all_actives(models.Q(año="Quinto año") & models.Q(semestre="Primer semestre"))
        for materia in query:
            materias.append(materia)
        
        query = Materia.find_all_actives(models.Q(año="Quinto año") & models.Q(semestre="Segundo semestre"))
        for materia in query:
            materias.append(materia)
        
        return materias


    @property
    def duracion(self):
        if self.semestre == "Primer semestre" or self.semestre == "Segundo semestre":
            return "Semestral"
        return "6 semanas"
    
    @property
    def get_correlatividades(self):
        correlativas = Correlatividades.find_all_actives(models.Q(codigo_de_materia=self))

        if len(correlativas) == 0:
            return " "

        materias_correlativas = ''
        for c in range(0, len(correlativas)-1):
            materias_correlativas += f'{correlativas[c].codigo_de_correlativa.codigo}, '
        materias_correlativas += correlativas[len(correlativas)-1].codigo_de_correlativa.codigo

        return materias_correlativas
    
    def get_correlativas(self):
        materias = Correlatividades.get_correlativas_de_materia(self)
        
        materias_formateadas = []
        for materia in materias:
            materias_formateadas.append(materia.codigo)
        
        return materias_formateadas
    
    def modificar(self, post):
        Materia.set_values(self, post)
        Correlatividades.eliminar_correlatividades(self)
        Materia.crear_correlativas(self, list(post))


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

    @classmethod
    def eliminar_correlatividades(cls, materia):
        instancias = cls.find_all_actives(models.Q(codigo_de_materia=materia))
        for instancia in instancias:
            instancia.delete()
    
    @classmethod
    def get_correlativas_de_materia(cls, materia):
        instancias = cls.find_all_actives(models.Q(codigo_de_materia=materia))
        materias = []
        for instancia in instancias:
            materias.append(Materia.find_pk(instancia.codigo_de_correlativa.pk))
        return materias

class CarreraMaterias(BaseModel):
    carrera = models.ForeignKey(Carrera, on_delete=models.SET_NULL, null=True)
    materia = models.ForeignKey(Materia, on_delete=models.SET_NULL, null=True)

    @classmethod
    def crear_asociacion(cls, carrera, materia):
        asociacion = CarreraMaterias()
        asociacion.carrera = carrera
        asociacion.materia = materia
        asociacion.save()
    
    @classmethod
    def get_materias(cls, carrera):
        materias_de_la_carrera = CarreraMaterias.find_all_actives(models.Q(carrera=carrera)).all()

        materias = []
        for instancia in materias_de_la_carrera:
            materias.append(instancia.materia)

        return materias


class MateriasInscriptas(BaseModel):
    alumno  = models.ForeignKey(Alumno, on_delete=models.SET_NULL, null=True)
    materia = models.ForeignKey(Materia, on_delete=models.SET_NULL, null=True)


class MateriasAprobadas(BaseModel):
    alumno  = models.ForeignKey(Alumno, on_delete=models.SET_NULL, null=True)
    materia = models.ForeignKey(Materia, on_delete=models.SET_NULL, null=True)