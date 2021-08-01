"""sistema_de_inscripciones URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sistema_de_inscripciones.views import *

urlpatterns = [
    path('', index),
    path('logout/', logout),

    path('home/', home),

    path('listar-carreras/', listar_carreras),
    path('alta-carrera/', alta_carrera),
    path('editar-carrera/<int:carrera_id>', editar_carrera),
    path('ver-carrera/<int:carrera_id>', ver_carrera),
    path('eliminar-carrera/<int:carrera_id>', eliminar_carrera),

    path('listar-materias/', listar_materias),
    path('alta-materia/', alta_materia),
]
