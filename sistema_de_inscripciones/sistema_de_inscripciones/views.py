from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from sistema_de_inscripciones.forms import *
import json


def index(request):
    if request.user.is_authenticated:
        return redirect('/home')

    if request.method == 'POST':
        user = auth.authenticate(dni=request.POST['dni'], password=request.POST['password'])
        if user is not None and user.is_active:
            auth.login(request, user)
            return redirect('/home')
        else:
            response_data = {
             'result': 'Error',
             'message': 'Los datos ingresados son inválidos.'
            }

            if LoginForm(request.POST).campos_vacios():
                response_data = {
                    'result': 'Error',
                    'message': 'Se deben completar los campos.'
                }
            return HttpResponse(json.dumps(response_data))
    else:
        loginForm = LoginForm()
    return render(request, 'index.html', {'form': loginForm})


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required
def home(request):
    return render(request, 'home.html')


@login_required
def listar_carreras(request):
    carreras = Carrera.find_all_actives()
    context = {'carreras':carreras}
    return render(request, 'admin/listar-carreras.html', context)


@login_required
def ver_carrera(request, carrera_id):
    carrera = Carrera.find_carrera(carrera_id)
    
    materias_primer_año  = carrera.materias_de_año("Primer año")
    materias_segundo_año = carrera.materias_de_año("Segundo año")
    materias_tercer_año  = carrera.materias_de_año("Tercer año")

    context = {'carrera':carrera, 'primero':materias_primer_año, 'segundo':materias_segundo_año,
                'tercero':materias_tercer_año}
    
    if carrera.año == 'Grado':
        context['cuarto'] = carrera.materias_de_año("Cuarto año")
        context['quinto'] = carrera.materias_de_año("Quinto año")

    return render(request, 'admin/ver-carrera.html', context)


@login_required
def alta_carrera(request):
    if not request.user.is_superuser:
        raise Http404
    
    if request.method == 'POST':
        post = request.POST

        validacion = Carrera.validar_carrera(post['nombre'])
        resultado_validacion = validacion[0]
        mensaje_validaciones = validacion[1]

        response_data = {
            'result': 'OK' if resultado_validacion else 'Error',
            'message': mensaje_validaciones
        }

        if resultado_validacion:
            Carrera.crear_carrera(post)
        else:
            context = {'materias':Materia.find_all_actives()}

        return HttpResponse(json.dumps(response_data))
    else:
        context = {'materias':Materia.find_all_actives()}
    return render(request, 'admin/alta-modificacion-carrera.html', context)


@login_required
def editar_carrera(request, carrera_id):
    carrera = Carrera.find_carrera(carrera_id)
    context = {'carrera': carrera, 'materias': Materia.find_all_actives()}
    return render(request, 'admin/alta-modificacion-carrera.html', context)


@login_required
def eliminar_carrera(request, carrera_id):
    carrera = Carrera.find_carrera(carrera_id)
    carrera.eliminar()
    response_data = {
        'result': 'OK',
        'message': "Se ha eliminado la carrera de forma exitosa"
    }
    return HttpResponse(json.dumps(response_data))


@login_required
def listar_materias(request):
    materias = Materia.find_all_actives()
    context = {'materias':materias}
    return render(request, 'admin/listar-materias.html', context)


@login_required
def alta_materia(request):
    if not request.user.is_superuser:
        raise Http404
    
    if request.method == 'POST':
        post = request.POST

        validacion           = Materia.validar_materia(post['input-codigo'], post['input-nombre'])
        resultado_validacion = validacion[0]
        mensaje_validaciones = validacion[1]

        response_data = {
            'result': 'OK' if resultado_validacion else 'Error',
            'message': mensaje_validaciones
        }

        if resultado_validacion:
            Materia.crear_materia(post)
        else:
            context = {'materias':Materia.find_all_actives()}

        return HttpResponse(json.dumps(response_data))
    else:
        context = {'materias':Materia.find_all_actives()}
    
    return render(request, 'admin/alta-modificacion-materia.html', context)