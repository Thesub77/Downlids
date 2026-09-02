const formulario = document.getElementById("form-metadatos");
const urlInput = document.getElementById("url");

let urlActual = "";

formulario.addEventListener("submit", manejarFormulario);

async function manejarFormulario(event){

    event.preventDefault();

    const url = urlInput.value.trim();
    urlActual = url;

    if(!url){
        return;
    }

    const boton = formulario.querySelector("button");

    bloquearBoton(
        boton,
        "Validando URL..."
    );

    try{

        const datos = await obtenerMetadatos(url);

        mostrarMensaje(
            "Metadatos obtenidos correctamente.",
            "exito"
        );
        mostrarMetadatos(datos);

        mostrarFormatos(datos.formatos);

        desbloquearBoton(boton)

    }catch(error){
        console.log(error)
        mostrarMensaje(
            "No fue posible obtener los metadatos.",
            "error"
        );

        desbloquearBoton(boton)

    }

}
