function getIcon(type)
{
    switch (type)
    {
        case "OK":
            return 'success';
        case "Warning":
            return 'warning';
        case "Error":
            return 'error';
        default:
            return null;
    }
}

function showNotification(type, message)
{
    let icon = getIcon(type);

    if (type == "OK")
        type = "Éxito";

    if (type === "Warning")
        type = "Atención";
    
    Swal.fire({
      icon: icon,
      title: type,
      text: message,
      confirmButtonColor: '#0D6FED'
    })
}

function onFormRequestError()
{
    let response = {
        "result": "Error",
        "message": "Error en la conexión con el servidor."
    };
    showNotification(response.result, response.message);
}

function onFormSubmit(e)
{
    e.preventDefault();

    let req = new XMLHttpRequest();
    req.onload = function() {
        if (req.status === 200)
        {
            let response = JSON.parse(req.responseText);
            showNotification(response.result, response.message);
        }
        else
        {
            onFormRequestError();
        }
    }
    req.onerror = function() {
        onFormRequestError();
    }

    req.open("post", "#");
    req.send(new FormData(e.target));
}

window.addEventListener("load", function() {
    let forms = document.querySelectorAll("form")
    for (let i = 0; i < forms.length; i++)
        forms[i].addEventListener("submit", onFormSubmit);
})