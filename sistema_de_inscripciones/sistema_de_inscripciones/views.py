from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from sistema_de_inscripciones.forms import *
import json


def index(request):
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
    carreras = Carrera.find_all()
    context = {'carreras':carreras}
    return render(request, 'admin/listar-carreras.html', context)


@login_required
def alta_carrera(request):
    if not request.user.is_superuser:
        raise Http404
    
    context = {'materias': Materia.find_all}
    return render(request, 'admin/alta-modificacion-carrera.html', context)


@login_required
def listar_materias(request):
    materias = Materia.find_all()
    context = {'materias':materias}
    return render(request, 'admin/listar-materias.html', context)


@login_required
def alta_materia(request):
    if not request.user.is_superuser:
        raise Http404
    
    if request.method == 'POST':
        form = AltaMateriaForm(request.POST)

        validacion = form.validar_materia()
        
        if validacion[0]:
            data = form.cleaned_data
            materia = Materia.crear_materia(data)
            print(validacion[1])
            return redirect('/listar-materias')
        else:
            mensaje = validacion[1]
            print(mensaje)

            context = {'form':form}
    else:
        context = {'form':AltaMateriaForm()}
    
    return render(request, 'admin/alta-modificacion-materia.html', context)