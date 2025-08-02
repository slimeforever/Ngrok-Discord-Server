# Bot de Discord para Gestión de Túneles de Ngrok

Este es un bot de Discord diseñado para facilitar la gestión de túneles de Ngrok directamente desde un servidor de Discord. Permite a los usuarios con un rol específico iniciar, detener y verificar el estado de los túneles de Ngrok de manera sencilla, ideal para servidores de juegos, desarrollo o cualquier aplicación que requiera compartir una URL [TCP] local temporal.

<h2 style="color:#008000;">Características Principales</h2>

* **Comandos de Ngrok:** Inicia (`!ngrok_start`), detén (`!ngrok_stop`) y verifica el estado (`!ngrok_status`) de un túnel.
* **Gestión de Roles:** Un administrador puede configurar un rol específico (`!set_ngrok_role`[`Aunque esto es temporal`]) para controlar quién puede usar los comandos de Ngrok, garantizando seguridad y control.
* **Creación de Canales de Voz[Proximamente]:** Al iniciar un túnel, el bot crea automáticamente un canal de voz con la dirección de conexión para que los usuarios puedan unirse fácilmente.

---

<h2 style="color:#0000FF;">Requisitos</h2>

Antes de usar el bot, asegúrate de tener lo siguiente:

* **Python 3.8+** instalado.
* **Ngrok** instalado y el ejecutable (`ngrok.exe`) en la ubicación especificada en el código (`C:\ServerMC\`).
* Una cuenta y **tokens de autenticación** de Ngrok.
* Un servidor de Discord con un rol que tenga los permisos necesarios.

---

<h2 style="color:#FF5733;">Configuración del Bot</h2>

Para que el bot funcione, necesitas configurar las variables de entorno.

1.  Copia el archivo `ex.env.example` y renómbralo a `.env`.
2.  Edita el archivo `.env` con tus tokens.

El archivo `.env` debe tener el siguiente formato, sin comentarios ni texto adicional:

```ini
DISCORD_TOKEN= token de tu bot
NGROK_AUTH_TOKEN= Token de tu cuenta de ngrok
NGROK_PORT= aca solo pongan 8080
