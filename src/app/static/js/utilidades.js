const mensaje = document.getElementById("mensaje");

function mostrarMensaje(texto, tipo){

    mensaje.textContent = texto;

    mensaje.classList.remove(
        "oculto",
        "mensaje-exito",
        "mensaje-error"
    );

    mensaje.classList.add(
        tipo === "error"
            ? "mensaje-error"
            : "mensaje-exito"
    );

    clearTimeout(mensaje.timer);

    mensaje.timer = setTimeout(() => {

        ocultarMensaje();

    }, 4000);

}

function ocultarMensaje(){

    mensaje.classList.add("oculto");

}


function bloquearBoton(boton, texto){

    boton.disabled = true;
    boton.dataset.textoOriginal = boton.textContent;
    boton.textContent = texto;
    boton.classList.add("btn-cargando");

}

function desbloquearBoton(boton){

    boton.disabled = false;
    boton.textContent = boton.dataset.textoOriginal;
    boton.classList.remove("btn-cargando");

}