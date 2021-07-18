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