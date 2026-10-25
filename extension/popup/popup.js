// ==========================================================================
// Downlids Companion - Lógica del Popup
// ==========================================================================

const BACKEND_URL = "http://127.0.0.1:8000";

// Elementos DOM
const statusPill = document.getElementById("status-pill");
const statusText = document.getElementById("status-text");
const servidorOfflinePanel = document.getElementById("servidor-offline-panel");
const btnReintentar = document.getElementById("btn-reintentar");

const inputUrl = document.getElementById("input-url");
const btnAnalizar = document.getElementById("btn-analizar");
const platformTag = document.getElementById("platform-tag");
const tabDomain = document.getElementById("tab-domain");

const loadingPanel = document.getElementById("loading-panel");
const loadingText = document.getElementById("loading-text");

const mensajePanel = document.getElementById("mensaje-panel");
const mensajeTexto = document.getElementById("mensaje-texto");

const resultadoPanel = document.getElementById("resultado-panel");
const videoMiniatura = document.getElementById("video-miniatura");
const videoDuracion = document.getElementById("video-duracion");
const videoPlataforma = document.getElementById("video-plataforma");
const videoTitulo = document.getElementById("video-titulo");
const videoAutor = document.getElementById("video-autor");
const selectFormato = document.getElementById("select-formato");

const btnDescargar = document.getElementById("btn-descargar");
const btnDescargarTexto = document.getElementById("btn-descargar-texto");
const btnAbrirWeb = document.getElementById("btn-abrir-web");

// Estado
let urlActual = "";
let datosActuales = null;
let cookiesActuales = null;
let servidorConectado = false;
let intervaloProgreso = null;
let descargandoActualmente = false;

// 1. Helpers de Persistencia en chrome.storage
async function guardarDescargaActiva(datosDescarga) {
  if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
    try {
      await chrome.storage.local.set({ descargaActiva: datosDescarga });
    } catch (e) {
      console.warn("No se pudo guardar la descarga activa en storage:", e);
    }
  }
}

async function obtenerDescargaActiva() {
  if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
    try {
      const res = await chrome.storage.local.get("descargaActiva");
      return res.descargaActiva || null;
    } catch (e) {
      console.warn("No se pudo obtener la descarga activa de storage:", e);
    }
  }
  return null;
}

async function limpiarDescargaActiva() {
  if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
    try {
      await chrome.storage.local.remove("descargaActiva");
    } catch (e) {
      console.warn("No se pudo limpiar la descarga activa en storage:", e);
    }
  }
}

// 2. Extractor de cookies de la sesión activa
async function obtenerCookiesDePestana(url) {
  if (typeof chrome === "undefined" || !chrome.cookies || !chrome.cookies.getAll) {
    return null;
  }
  try {
    const cookies = await chrome.cookies.getAll({ url: url });
    if (!cookies || cookies.length === 0) {
      return null;
    }
    // Formato Netscape HTTP Cookie File estándar para yt-dlp
    let netscape = "# Netscape HTTP Cookie File\n";
    for (const c of cookies) {
      const domain = c.domain.startsWith(".") ? c.domain : `.${c.domain}`;
      const flag = domain.startsWith(".") ? "TRUE" : "FALSE";
      const path = c.path || "/";
      const secure = c.secure ? "TRUE" : "FALSE";
      const expiry = c.expirationDate ? Math.round(c.expirationDate) : 2147483647;
      netscape += `${domain}\t${flag}\t${path}\t${secure}\t${expiry}\t${c.name}\t${c.value}\n`;
    }
    return netscape;
  } catch (err) {
    console.warn("No se pudieron obtener cookies de la pestaña:", err);
    return null;
  }
}

// 3. Inicialización
document.addEventListener("DOMContentLoaded", async () => {
  configurarEventos();
  const servidorOk = await verificarEstadoServidor();
  if (!servidorOk) return;

  // Comprobar si había una descarga en curso antes de cerrar el popup
  const descargaActiva = await obtenerDescargaActiva();
  if (descargaActiva && descargaActiva.downloadId) {
    restaurarDescargaActiva(descargaActiva);
    monitorearProgreso(descargaActiva.downloadId);
  } else {
    await detectarPestanaActiva();
  }
});

function configurarEventos() {
  btnReintentar.addEventListener("click", async () => {
    await verificarEstadoServidor();
    if (servidorConectado && inputUrl.value.trim() && !descargandoActualmente) {
      analizarVideo(inputUrl.value.trim());
    }
  });

  btnAnalizar.addEventListener("click", () => {
    if (descargandoActualmente) return;
    const url = inputUrl.value.trim();
    if (url) {
      analizarVideo(url);
    }
  });

  inputUrl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      if (descargandoActualmente) return;
      const url = inputUrl.value.trim();
      if (url) {
        analizarVideo(url);
      }
    }
  });

  btnDescargar.addEventListener("click", iniciarDescarga);

  btnAbrirWeb.addEventListener("click", () => {
    if (descargandoActualmente) return;
    const url = inputUrl.value.trim() || urlActual;
    const destino = url 
      ? `${BACKEND_URL}/?url=${encodeURIComponent(url)}`
      : `${BACKEND_URL}/`;
    
    if (typeof chrome !== "undefined" && chrome.tabs && chrome.tabs.create) {
      chrome.tabs.create({ url: destino });
    } else {
      window.open(destino, "_blank");
    }
  });
}

// 4. Verificación del Servidor Local Downlids
async function verificarEstadoServidor() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const resp = await fetch(`${BACKEND_URL}/api/estado`, { signal: controller.signal });
    clearTimeout(timeoutId);

    if (resp.ok) {
      servidorConectado = true;
      statusPill.className = "status-pill conectado";
      statusText.textContent = "Conectado";
      servidorOfflinePanel.classList.add("oculto");
      return true;
    }
  } catch (err) {
    // Servidor inactivo
  }

  servidorConectado = false;
  statusPill.className = "status-pill desconectado";
  statusText.textContent = "Desconectado";
  servidorOfflinePanel.classList.remove("oculto");
  return false;
}

// 5. Detección de la Pestaña Activa en Brave/Chrome
async function detectarPestanaActiva() {
  if (typeof chrome === "undefined" || !chrome.tabs || !chrome.tabs.query) {
    tabDomain.textContent = "Modo vista previa";
    return;
  }

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs || tabs.length === 0) return;
    const tab = tabs[0];
    const url = tab.url || "";

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      tabDomain.textContent = "Página no compatible";
      platformTag.textContent = "Navegador";
      return;
    }

    inputUrl.value = url;
    urlActual = url;

    try {
      const urlObj = new URL(url);
      tabDomain.textContent = urlObj.hostname;
      platformTag.textContent = detectarEtiquetaPlataforma(urlObj.hostname);
    } catch {
      tabDomain.textContent = "URL detectada";
    }

    // Auto-analizar si el servidor está online y es un sitio de video
    if (servidorConectado && esSitioDeVideo(url) && !descargandoActualmente) {
      analizarVideo(url);
    }
  });
}

function detectarEtiquetaPlataforma(hostname) {
  const host = hostname.toLowerCase();
  if (host.includes("youtube.com") || host.includes("youtu.be")) return "YouTube";
  if (host.includes("tiktok.com")) return "TikTok";
  if (host.includes("instagram.com")) return "Instagram";
  if (host.includes("twitch.tv")) return "Twitch";
  if (host.includes("kick.com")) return "Kick";
  if (host.includes("t.me") || host.includes("telegram.me")) return "Telegram";
  if (host.includes("facebook.com") || host.includes("fb.watch") || host.includes("fb.com")) return "Facebook";
  if (host.includes("vimeo.com")) return "Vimeo";
  if (host.includes("soundcloud.com")) return "SoundCloud";
  if (host.includes("x.com") || host.includes("twitter.com")) return "Twitter / X";
  return "Web";
}

function esSitioDeVideo(url) {
  const dominios = [
    "youtube.com", "youtu.be", "tiktok.com", "instagram.com",
    "twitch.tv", "kick.com", "t.me", "facebook.com", "fb.watch", "fb.com",
    "vimeo.com", "soundcloud.com", "reddit.com"
  ];
  return dominios.some(d => url.includes(d));
}

// 6. Extracción de Metadatos
async function analizarVideo(url) {
  if (!url || descargandoActualmente) return;

  if (!servidorConectado) {
    const conectado = await verificarEstadoServidor();
    if (!conectado) return;
  }

  mostrarCargando("Extrayendo información del video...");
  ocultarMensaje();
  resultadoPanel.classList.add("oculto");

  // Obtener cookies de sesión de la pestaña activa si están disponibles
  const cookies = await obtenerCookiesDePestana(url);
  cookiesActuales = cookies;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 35000);

  try {
    const resp = await fetch(`${BACKEND_URL}/metadata/metadatos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: url,
        plataforma: "auto",
        cookies: cookiesActuales
      }),
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      throw new Error(data.detail || "No fue posible obtener información del video.");
    }

    datosActuales = data;
    urlActual = url;
    mostrarResultado(data);
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === "AbortError") {
      mostrarMensaje("Tiempo de espera agotado al extraer el video.", "error");
    } else {
      mostrarMensaje(err.message || "Error de conexión con el backend.", "error");
    }
  } finally {
    ocultarCargando();
  }
}

// 7. Mostrar Resultados en UI
function mostrarResultado(data) {
  videoMiniatura.src = data.miniatura || "";
  videoTitulo.textContent = data.titulo || "Sin título";
  videoTitulo.title = data.titulo || "";
  videoAutor.textContent = data.autor || "Desconocido";
  videoPlataforma.textContent = data.plataforma || "Web";
  videoDuracion.textContent = formatearDuracion(data.duracion);

  // Llenar selector de formatos
  selectFormato.innerHTML = "";
  if (!data.formatos || data.formatos.length === 0) {
    const opt = document.createElement("option");
    opt.value = "best";
    opt.textContent = "Mejor calidad disponible";
    selectFormato.appendChild(opt);
  } else {
    data.formatos.forEach((f) => {
      const opt = document.createElement("option");
      opt.value = f.id;
      const tamanoStr = f.tamano ? ` (${f.tamano})` : "";
      opt.textContent = `${f.calidad} - ${f.extension}${tamanoStr}`;
      selectFormato.appendChild(opt);
    });
  }

  resultadoPanel.classList.remove("oculto");
}

function formatearDuracion(segundos) {
  if (!segundos || segundos <= 0) return "--:--";
  const m = Math.floor(segundos / 60);
  const s = segundos % 60;
  return `${m}:${s < 10 ? "0" : ""}${s}`;
}

// 8. Restaurar Descarga Activa
function restaurarDescargaActiva(descarga) {
  urlActual = descarga.url;
  inputUrl.value = descarga.url;
  datosActuales = descarga.datos;
  
  try {
    const urlObj = new URL(descarga.url);
    tabDomain.textContent = urlObj.hostname;
    platformTag.textContent = detectarEtiquetaPlataforma(urlObj.hostname);
  } catch {
    tabDomain.textContent = "Descarga en curso";
  }

  if (descarga.datos) {
    mostrarResultado(descarga.datos);
    if (descarga.formatoId) {
      selectFormato.value = descarga.formatoId;
    }
  }

  bloquearControlesDuranteDescarga("Descargando...");
}

// 9. Iniciar Descarga
async function iniciarDescarga() {
  if (!servidorConectado) {
    mostrarMensaje("Servidor local inactivo.", "error");
    return;
  }

  const formatoId = selectFormato.value || "best";
  bloquearControlesDuranteDescarga("Iniciando...");

  try {
    const resp = await fetch(`${BACKEND_URL}/descarga/iniciar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: urlActual,
        formato: formatoId,
        plataforma: "auto",
        cookies: cookiesActuales
      })
    });

    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      throw new Error(data.detail || "Error al solicitar la descarga.");
    }

    const downloadId = data.download_id;

    // Persistir estado de descarga activa para no perderla si el popup se cierra
    await guardarDescargaActiva({
      downloadId: downloadId,
      url: urlActual,
      formatoId: formatoId,
      datos: datosActuales
    });

    monitorearProgreso(downloadId);
  } catch (err) {
    desbloquearControles();
    mostrarMensaje(err.message, "error");
  }
}

// 10. Monitoreo de Progreso de Descarga (directamente en el botón)
function monitorearProgreso(downloadId) {
  if (intervaloProgreso) clearInterval(intervaloProgreso);

  intervaloProgreso = setInterval(async () => {
    try {
      const resp = await fetch(`${BACKEND_URL}/descarga/estado/${downloadId}`);
      if (resp.status === 404) {
        clearInterval(intervaloProgreso);
        intervaloProgreso = null;
        await limpiarDescargaActiva();
        desbloquearControles();
        mostrarMensaje("La descarga expiró o ya fue completada.", "error");
        return;
      }

      if (!resp.ok) throw new Error("Error consultando estado.");

      const estado = await resp.json();
      const pct = Math.max(0, Math.min(100, estado.progreso || 0));

      if (estado.estado === "descargando") {
        btnDescargarTexto.textContent = `Descargando ${pct}%...`;
      } else if (estado.estado === "procesando") {
        btnDescargarTexto.textContent = "Procesando...";
      } else if (estado.estado === "completado") {
        clearInterval(intervaloProgreso);
        intervaloProgreso = null;
        await limpiarDescargaActiva();
        desbloquearControles();

        btnDescargarTexto.textContent = "¡Descargado!";
        mostrarMensaje("¡Descarga completada! Guardando archivo...", "exito");

        // Disparar la descarga del archivo en el navegador
        const urlArchivo = `${BACKEND_URL}/descarga/archivo/${downloadId}`;
        if (typeof chrome !== "undefined" && chrome.tabs && chrome.tabs.create) {
          chrome.tabs.create({ url: urlArchivo, active: false });
        } else {
          window.open(urlArchivo, "_blank");
        }

        setTimeout(() => {
          btnDescargarTexto.textContent = "Descargar ahora";
        }, 5000);

      } else if (estado.estado === "error") {
        clearInterval(intervaloProgreso);
        intervaloProgreso = null;
        await limpiarDescargaActiva();
        desbloquearControles();
        throw new Error(estado.error || "Ocurrió un error en la descarga.");
      }
    } catch (err) {
      if (intervaloProgreso) {
        clearInterval(intervaloProgreso);
        intervaloProgreso = null;
      }
      await limpiarDescargaActiva();
      desbloquearControles();
      mostrarMensaje(err.message, "error");
    }
  }, 600);
}

// 11. Bloqueo y desbloqueo de Controles
function bloquearControlesDuranteDescarga(textoBoton = "Descargando...") {
  descargandoActualmente = true;
  inputUrl.disabled = true;
  btnAnalizar.disabled = true;
  btnAbrirWeb.disabled = true;
  selectFormato.disabled = true;
  btnDescargar.disabled = true;
  btnDescargarTexto.textContent = textoBoton;
}

function desbloquearControles() {
  descargandoActualmente = false;
  inputUrl.disabled = false;
  btnAnalizar.disabled = false;
  btnAbrirWeb.disabled = false;
  selectFormato.disabled = false;
  btnDescargar.disabled = false;
  btnDescargarTexto.textContent = "Descargar ahora";
}

function mostrarCargando(msg) {
  loadingText.textContent = msg;
  loadingPanel.classList.remove("oculto");
}

function ocultarCargando() {
  loadingPanel.classList.add("oculto");
}

function mostrarMensaje(texto, tipo) {
  mensajeTexto.textContent = texto;
  mensajePanel.className = `panel mensaje-panel ${tipo}`;
  mensajePanel.classList.remove("oculto");
}

function ocultarMensaje() {
  mensajePanel.classList.add("oculto");
}
