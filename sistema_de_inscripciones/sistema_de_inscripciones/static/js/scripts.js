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
function onCheckBoxMateriaClick(nombreCorrelativa)
{
    let checkBoxCorrelativa = document.getElementById(nombreCorrelativa);
    console.log(checkBoxCorrelativa);

    if (checkBoxCorrelativa.checked)
    {
        checkBoxCorrelativa.value = "True";
        return;
    }

    checkBoxCorrelativa.value = "False";
}

function onSeleccionarTodasLasCorrelativasClick()
{
    let correlativas = document.getElementsByClassName("materia");

    for (let i = 0; i < correlativas.length; i++) {
        correlativas[i].checked = "True";
        correlativas[i].value = "True";
    }
}


function onEliminarCarreraClick(carreraID)
{
    $.ajax({
        url: `/eliminar-carrera/${carreraID}`,
        dataType: 'json',
        success: function (data) {
            showNotification(data.result, data.message);

            if(data.result == "OK")
            {
                $(".swal2-confirm").click(function () {
                    window.location.href = `/listar-carreras`;
                });
            }
        }
      });
}

function initializeEditarCarrera(duracion, materias)
{
    if (duracion === "Grado")
        document.getElementById("grado").checked = "True";
    else
        document.getElementById("terciario").checked = "True";
        
    console.log(duracion);
}