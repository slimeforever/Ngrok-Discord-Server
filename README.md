# Bot de Discord para Gestión de Túneles de Ngrok

Este es un bot de Discord diseñado para facilitar la gestión de túneles de Ngrok directamente desde un servidor de Discord. Permite a los usuarios con un rol específico iniciar, detener y verificar el estado de túneles de Ngrok de manera sencilla, ideal para servidores de juegos, desarrollo o cualquier aplicación que requiera compartir una URL local temporal.

## Características Principales

* **Comandos de Ngrok:** Inicia (`!ngrok_start`), detén (`!ngrok_stop`) y verifica el estado (`!ngrok_status`) de un túnel de Ngrok.
* **Gestión de Roles:** Un administrador puede configurar un rol específico (`!set_ngrok_role`) para controlar quién puede usar los comandos de Ngrok, garantizando seguridad y control.
* **Creación de Canales de Voz:** Al iniciar un túnel, el bot crea automáticamente un canal de voz con la dirección de conexión para que los jugadores o usuarios puedan unirse fácilmente.
* **Múltiples Tokens de Ngrok:** Soporta el uso de múltiples tokens de autenticación de Ngrok, asignándolos de forma rotativa para permitir que varios túneles estén activos simultáneamente en diferentes canales.
* **Manejo de Errores:** Incluye mensajes de error claros para guiar al usuario en caso de permisos faltantes, tokens no disponibles o problemas en la ejecución.

## Requisitos

Antes de usar el bot, asegúrate de tener lo siguiente:

* **Python 3.8+** instalado.
* **Ngrok** instalado en tu sistema.
* Una cuenta y tokens de autenticación de Ngrok.
* Un servidor de Discord donde puedas agregar el bot y configurarlo.

## Configuración del Bot

Para que el bot funcione, necesitas configurar las siguientes variables de entorno. Crea un archivo llamado `.env` en la misma carpeta que el bot y añade las siguientes líneas:

```ini
DISCORD_TOKEN=tu_token_de_discord_aqui
NGROK_AUTH_TOKENS=token1,token2,token3
