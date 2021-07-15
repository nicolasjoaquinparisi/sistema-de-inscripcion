from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import json


def index(request):
    return render(request, 'index.html')


def login(request):
    if request.method == 'POST':
        user = auth.authenticate(email=request.POST['email'], password=request.POST['password'])
        if user is not None and user.habilitado:
            auth.login(request, user)
            response_data = {
                'result': 'Login',
                'message': 'Login'
            }
            return HttpResponse(json.dumps(response_data))
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
        formLogin = LoginForm()
    return render(request, 'funcionalidades/login.html', {'formLogin': formLogin})


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')