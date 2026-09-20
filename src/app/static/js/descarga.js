tablaFormatos.addEventListener("click", manejarClickDescarga);

function manejarClickDescarga(event){

    const boton = event.target.closest(".btn-descargar");

    if(!boton){
        return;
    }

    bloquearBoton(boton, "Preparando...");

    const formato = boton.dataset.id;
    const platParam = (typeof plataformaActual !== "undefined" && plataformaActual) ? `&plataforma=${encodeURIComponent(plataformaActual)}` : "";

    const urlDescarga =
        `/descarga?url=${encodeURIComponent(urlActual)}&formato=${encodeURIComponent(formato)}${platParam}`;

    const enlace = document.createElement("a");
    enlace.href = urlDescarga;
    enlace.style.display = "none";

    document.body.appendChild(enlace);

    enlace.click();

    setTimeout(() => {
        desbloquearBoton(boton);
    }, 10000);

    document.body.removeChild(enlace);

    

}