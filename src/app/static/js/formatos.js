const tablaFormatos = document.getElementById("tabla-formatos");

function limpiarFormatos(){

    tablaFormatos.innerHTML = "";

}

function crearFila(formato){

    const fila = document.createElement("tr");

    fila.innerHTML = `

        <td>${formato.calidad}</td>
        <td>${formato.extension}</td>
        <td>${formato.tipo}</td>
        <td>${formato.tamano ?? "-"}</td>
        <td>
            <button
                class="btn-descargar"
                data-id="${formato.id}">
                Descargar
            </button>
        </td>

    `;

    return fila;

}

function mostrarFormatos(formatos){
    limpiarFormatos();
    console.log(formatos);
    formatos.forEach(formato=>{
        tablaFormatos.appendChild(

            crearFila(formato)

        );

    });

}