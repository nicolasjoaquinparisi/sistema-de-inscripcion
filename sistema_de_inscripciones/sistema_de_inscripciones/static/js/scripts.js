"use strict";

function setUpTime() {
    const days = [
        'Domingo',
        'Lunes',
        'Martes',
        'Miercoles',
        'Jueves',
        'Viernes',
        'Sabado'
    ]
    
    const months = [
        'Enero',
        'Febrero',
        'Marzo',
        'Abril',
        'Mayo',
        'Junio',
        'Julio',
        'Agosto',
        'Septiembre',
        'Octubre',
        'Noviembre',
        'Deciembre'
    ]

    let today = new Date();
    let currentDay = days[today.getDay()];
    let currentMonth = months[today.getMonth()];
    document.getElementById("fecha-1").innerHTML = `${currentDay} ${today.getDate()}`;
    document.getElementById("fecha-2").innerHTML = `${currentMonth} del ${today.getFullYear()}`;
}


// ALTA Y MODIFICACION MATERIAS
function onCheckBoxCorrelativaClick(nombreCorrelativa)
{
    let checkBoxCorrelativa = document.getElementById(nombreCorrelativa);
    console.log(checkBoxCorrelativa);

    if (checkBoxCorrelativa.checked)
    {
        checkBoxCorrelativa.value = "True"
        return;
    }

    checkBoxCorrelativa.value = "False"
}