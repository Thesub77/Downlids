const resultado = document.getElementById("resultado");
const miniatura = document.getElementById("miniatura");
const titulo = document.getElementById("titulo");
const autor = document.getElementById("autor");
const duracion = document.getElementById("duracion");
const vistas = document.getElementById("vistas");
const plataforma = document.getElementById("plataforma");

async function obtenerMetadatos(url, plataformaSeleccionada){

    const respuesta = await fetch("/metadata/metadatos",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({
            url: url,
            plataforma: plataformaSeleccionada || null
        })

    });

    if(!respuesta.ok){
        const errorData = await respuesta.json().catch(() => ({}));
        throw new Error(errorData.detail || "No fue posible obtener los metadatos.");
    }


    return await respuesta.json();

}

function mostrarMetadatos(datos){

    miniatura.src = datos.miniatura;

    titulo.textContent = datos.titulo;

    autor.textContent = "Autor: " + datos.autor;

    duracion.textContent = "Duración: " + datos.duracion;

    vistas.textContent = "Vistas: " + datos.vistas.toLocaleString();

    plataforma.textContent = "Plataforma: " + datos.plataforma;

    resultado.classList.remove("oculto");

}