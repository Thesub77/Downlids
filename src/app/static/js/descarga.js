tablaFormatos.addEventListener("click", manejarClickDescarga);

let intervaloProgreso = null;

async function manejarClickDescarga(event) {
    const boton = event.target.closest(".btn-descargar");
    if (!boton) {
        return;
    }

    const formato = boton.dataset.id;
    const panelProgreso = document.getElementById("panel-progreso");
    const barraProgreso = document.getElementById("barra-progreso");
    const textoProgreso = document.getElementById("texto-progreso");
    const detalleProgreso = document.getElementById("detalle-progreso");

    bloquearBoton(boton, "Iniciando...");

    if (panelProgreso) {
        panelProgreso.classList.remove("oculto");
        barraProgreso.style.width = "0%";
        textoProgreso.textContent = "Iniciando descarga...";
        detalleProgreso.textContent = "";
    }

    try {
        const respuesta = await fetch("/descarga/iniciar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                url: urlActual,
                formato: formato,
                plataforma: typeof plataformaActual !== "undefined" ? plataformaActual : null
            })
        });

        if (!respuesta.ok) {
            const errorData = await respuesta.json().catch(() => ({}));
            throw new Error(errorData.detail || "Error al iniciar la descarga.");
        }

        const data = await respuesta.json();
        const downloadId = data.download_id;

        if (intervaloProgreso) {
            clearInterval(intervaloProgreso);
        }

        intervaloProgreso = setInterval(async () => {
            try {
                const resEstado = await fetch(`/descarga/estado/${downloadId}`);
                if (!resEstado.ok) {
                    throw new Error("No se pudo obtener el estado de la descarga.");
                }

                const estado = await resEstado.json();

                if (panelProgreso) {
                    const pct = Math.max(0, Math.min(100, estado.progreso || 0));
                    barraProgreso.style.width = `${pct}%`;

                    if (estado.estado === "descargando") {
                        textoProgreso.textContent = `Descargando... ${pct}%`;
                        const partes = [];
                        if (estado.velocidad) partes.push(estado.velocidad);
                        if (estado.eta) partes.push(`ETA: ${estado.eta}`);
                        detalleProgreso.textContent = partes.join(" • ");
                        boton.textContent = `Descargando ${pct}%`;
                    } else if (estado.estado === "procesando") {
                        textoProgreso.textContent = "Procesando y empaquetando archivo...";
                        detalleProgreso.textContent = "Por favor espera";
                        boton.textContent = "Procesando...";
                    } else if (estado.estado === "completado") {
                        clearInterval(intervaloProgreso);
                        intervaloProgreso = null;

                        textoProgreso.textContent = "¡Descarga completada! Guardando archivo...";
                        detalleProgreso.textContent = estado.nombre_archivo || "";
                        barraProgreso.style.width = "100%";
                        desbloquearBoton(boton);

                        // Descargar archivo en el navegador
                        const enlace = document.createElement("a");
                        enlace.href = `/descarga/archivo/${downloadId}`;
                        enlace.style.display = "none";
                        document.body.appendChild(enlace);
                        enlace.click();
                        document.body.removeChild(enlace);

                        setTimeout(() => {
                            if (panelProgreso) {
                                panelProgreso.classList.add("oculto");
                            }
                        }, 5000);
                    } else if (estado.estado === "error") {
                        clearInterval(intervaloProgreso);
                        intervaloProgreso = null;
                        throw new Error(estado.error || "Ocurrió un error durante la descarga.");
                    }
                }
            } catch (err) {
                if (intervaloProgreso) {
                    clearInterval(intervaloProgreso);
                    intervaloProgreso = null;
                }
                desbloquearBoton(boton);
                if (panelProgreso) {
                    panelProgreso.classList.add("oculto");
                }
                mostrarMensaje(err.message || "Error durante el progreso de descarga.", "error");
            }
        }, 500);

    } catch (error) {
        desbloquearBoton(boton);
        if (panelProgreso) {
            panelProgreso.classList.add("oculto");
        }
        mostrarMensaje(error.message || "Error al solicitar la descarga.", "error");
    }
}