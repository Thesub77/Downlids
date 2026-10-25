# 🚀 Downlids Companion (Extensión para Brave / Chromium)

Esta extensión permite descargar videos y audios desde cualquier pestaña activa en el navegador **Brave** (o cualquier navegador basado en Chromium como Chrome, Edge u Opera) comunicándose con tu servidor local de **Downlids**.

---

## 🛠️ Requisitos Previos

Tener el backend de Downlids corriendo localmente en el puerto `8000`:

```powershell
uv run uvicorn app.main:app --app-dir src --reload
```

---

## 📦 Cómo Instalar la Extensión en Brave (en 3 pasos)

1. **Abre el administrador de extensiones en Brave:**
   * En la barra de direcciones de Brave escribe: `brave://extensions` (o `chrome://extensions` en Chrome).
2. **Activa el Modo de Desarrollador:**
   * En la esquina superior derecha, activa el interruptor **"Modo de desarrollador"** (Developer mode).
3. **Carga la extensión:**
   * Haz clic en el botón **"Cargar extensión sin empaquetar"** (Load unpacked).
   * Selecciona la carpeta `extension` ubicada en la raíz de este proyecto:
     ```
     C:\Users\USUARIO\Desktop\Downlids\extension
     ```
   * ¡Listo! El icono de **Downlids** aparecerá en la barra de herramientas de tu navegador.

---

## 🎯 Cómo Usar la Extensión

1. Abre cualquier video o audio en la web (por ejemplo en YouTube, TikTok, Twitch, Instagram, Facebook, Kick, Telegram, SoundCloud, Vimeo, etc.).
2. Haz clic en el icono de **Downlids** en la esquina superior derecha de Brave.
3. La extensión detectará automáticamente la pestaña actual, extraerá las cookies de sesión (necesarias para videos privados o con restricción en Facebook/Instagram) y consultará las calidades disponibles.
4. Elige la resolución deseada y haz clic en **"Descargar ahora"**. La descarga se gestionará a través de tu backend local y se guardará directamente en tu equipo.
5. También puedes pulsar en **"Abrir en Web"** para ver la interfaz completa de Downlids precargada con ese video.

---

## 🍪 Soporte de Cookies y Videos Protegidos (Facebook, Instagram, etc.)

* **Vía Extensión (Automático):** Al abrir la extensión en una pestaña de Facebook o Instagram donde estés autenticado, Downlids Companion extrae tus cookies de sesión de forma segura y las transmite al backend local. Esto permite descargar videos de grupos, Reels y videos con restricción sin que Meta bloquee la petición.
* **Vía Web Directa:** Si prefieres usar la interfaz web clásica de Downlids sin la extensión, puedes colocar un archivo `cookies.txt` (formato Netscape) en la carpeta raíz del proyecto y el servidor lo utilizará automáticamente para autenticar las peticiones a Facebook, YouTube o Instagram.
