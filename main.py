import discord
from discord.ext import commands
import os
import requests
import subprocess
import asyncio
import time
from dotenv import load_dotenv

# Carga las variables de entorno
load_dotenv()

# --- Configuración del bot y Ngrok ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True # Nuevo intent necesario para la verificación de roles

bot = commands.Bot(command_prefix='!', intents=intents)

# Variables de configuración
NGROK_AUTH_TOKENS = os.getenv("NGROK_AUTH_TOKENS").split(',') if os.getenv("NGROK_AUTH_TOKENS") else []
NGROK_API_URL = "http://localhost:4040/api/tunnels"
CONFIG_FILE = "config.txt"

# Variables globales para la gestión de túneles y roles
active_tunnels = {}
required_ngrok_role = None

# --- Funciones de configuración y utilidades ---

def load_ngrok_role():
    """Carga el nombre del rol requerido desde el archivo de configuración."""
    global required_ngrok_role
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            required_ngrok_role = file.read().strip()
            print(f"Rol de Ngrok cargado: '{required_ngrok_role}'")
    else:
        print("El archivo de configuración no existe. Se debe establecer un rol con !set_ngrok_role.")
        required_ngrok_role = None

def save_ngrok_role(role_name):
    """Guarda el nombre del rol requerido en el archivo de configuración."""
    global required_ngrok_role
    with open(CONFIG_FILE, "w") as file:
        file.write(role_name)
    required_ngrok_role = role_name
    print(f"Rol de Ngrok guardado: '{required_ngrok_role}'")

def is_ngrok_role_user():
    """Verificador de comando para el rol requerido."""
    async def predicate(ctx):
        if not required_ngrok_role:
            await ctx.send("No se ha configurado un rol para Ngrok. Un administrador debe usar `!set_ngrok_role <nombre_del_rol>`.")
            return False
        
        user_roles = [role.name.lower() for role in ctx.author.roles]
        if required_ngrok_role.lower() not in user_roles:
            await ctx.send(f"Lo siento, solo los miembros con el rol '{required_ngrok_role}' pueden usar este comando.")
            return False
        return True
    return commands.check(predicate)

def get_available_token():
    """Busca y devuelve un token de Ngrok que no esté en uso."""
    used_tokens = [tunnel['token_in_use'] for tunnel in active_tunnels.values()]
    for token in NGROK_AUTH_TOKENS:
        if token not in used_tokens:
            return token
    return None

# --- Comandos del bot ---

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    load_ngrok_role() # Carga el rol al iniciar el bot

@bot.command()
@commands.has_permissions(administrator=True)
async def set_ngrok_role(ctx, *, role_name: str):
    """
    Establece el rol que puede usar los comandos de Ngrok.
    Solo para administradores.
    Ejemplo: !set_ngrok_role admin
    """
    save_ngrok_role(role_name)
    await ctx.send(f"El rol '{role_name}' ha sido configurado para usar los comandos de Ngrok.")

@bot.command()
@is_ngrok_role_user()
async def ngrok_start(ctx, proto: str = "tcp", port: int = 25565, region: str = "us"):
    """
    Inicia un túnel de Ngrok con argumentos.
    Uso: !ngrok_start [proto] [port] [region]
    Ejemplo: !ngrok_start tcp 25565 us
    """
    if ctx.channel.id in active_tunnels:
        await ctx.send("Ya hay un túnel activo en este canal. Usa `!ngrok_stop` para detenerlo.")
        return

    selected_token = get_available_token()
    if not selected_token:
        await ctx.send("Lo siento, no hay tokens de Ngrok disponibles en este momento. Por favor, espera a que se libere uno.")
        return

    try:
        subprocess.run(["C:\\ServerMC\\ngrok.exe", "config", "add-authtoken", selected_token], check=True)
    except FileNotFoundError:
        await ctx.send("Error: No se encontró 'ngrok.exe' en la ruta especificada.")
        return

    await ctx.send(f"Iniciando Ngrok con el token `{selected_token[:5]}...` (oculto). Protocolo: `{proto}`, Puerto: `{port}`, Región: `{region}`. Por favor, espera.")

    try:
        ngrok_process = subprocess.Popen([
            "C:\\ServerMC\\ngrok.exe", proto, "--region", region, str(port)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError:
        await ctx.send("Error: No se pudo iniciar el proceso de ngrok. ¿Está el ejecutable en la ubicación correcta?")
        return
    
    time.sleep(5)
    
    try:
        response = requests.get(NGROK_API_URL)
        response.raise_for_status()
        tunnels = response.json().get('tunnels', [])
        
        if tunnels:
            tunnel_info = tunnels[0]
            public_url = tunnel_info['public_url']
            channel_name = public_url.split('://')[-1]
            
            await ctx.send(f"¡Ngrok está activo! 🎉\n**URL:** `{public_url}`")
            
            try:
                new_channel = await ctx.guild.create_voice_channel(name=channel_name)
                temp_channel_id = new_channel.id
                await ctx.send(f"Canal de voz temporal `{channel_name}` creado. ¡Los jugadores pueden unirse!")
            except discord.Forbidden:
                await ctx.send("Error: No tengo permisos para crear canales de voz. Asegúrate de darme el rol adecuado.")
            
            active_tunnels[ctx.channel.id] = {
                'process': ngrok_process,
                'channel_id': temp_channel_id,
                'token_in_use': selected_token
            }
            return
        
        await ctx.send("No se pudo obtener la URL de Ngrok. Algo salió mal.")
        
    except requests.exceptions.RequestException:
        await ctx.send("Error al obtener la URL de Ngrok. ¿Está funcionando el servicio?")
    except Exception as e:
        await ctx.send(f"Ocurrió un error inesperado: {e}")

@bot.command()
@is_ngrok_role_user()
async def ngrok_stop(ctx):
    """Detiene el túnel de Ngrok en este canal si está en ejecución."""
    if ctx.channel.id not in active_tunnels:
        await ctx.send("No hay un túnel de Ngrok activo en este canal.")
        return

    tunnel_info = active_tunnels[ctx.channel.id]
    ngrok_process = tunnel_info['process']
    
    if ngrok_process and ngrok_process.poll() is None:
        ngrok_process.terminate()
        await ctx.send("Ngrok ha sido detenido.")
        
        temp_channel_id = tunnel_info['channel_id']
        if temp_channel_id:
            try:
                channel_to_delete = bot.get_channel(temp_channel_id)
                if channel_to_delete:
                    await channel_to_delete.delete()
                    await ctx.send("Canal de voz temporal eliminado.")
            except discord.Forbidden:
                await ctx.send("No tengo permisos para eliminar el canal de voz.")
        
        del active_tunnels[ctx.channel.id]
    else:
        await ctx.send("El túnel de Ngrok en este canal ya no está en ejecución.")
        del active_tunnels[ctx.channel.id]

@bot.command()
@is_ngrok_role_user()
async def ngrok_status(ctx):
    """Muestra el estado del túnel de Ngrok en este canal."""
    if ctx.channel.id not in active_tunnels:
        await ctx.send("No hay un túnel de Ngrok activo en este canal.")
        return

    tunnel_info = active_tunnels[ctx.channel.id]
    ngrok_process = tunnel_info['process']

    if ngrok_process and ngrok_process.poll() is None:
        try:
            response = requests.get(NGROK_API_URL)
            response.raise_for_status()
            tunnels = response.json().get('tunnels', [])
            
            if tunnels:
                public_url = tunnels[0]['public_url']
                channel_name = public_url.split('://')[-1]
                
                await ctx.send(
                    f"Ngrok está activo. ✨\n"
                    f"**URL:** `{public_url}`\n"
                    f"**Dirección de conexión:** `{channel_name}`"
                )
            else:
                await ctx.send("Ngrok está en ejecución, pero no se encontraron túneles activos.")
        except requests.exceptions.RequestException:
            await ctx.send("Ngrok está en ejecución, pero no se puede acceder a su API.")
    else:
        await ctx.send("El túnel de Ngrok en este canal ya no está en ejecución.")
        del active_tunnels[ctx.channel.id]

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No tienes permisos de administrador para usar este comando.")
    elif isinstance(error, commands.CommandInvokeError):
        # Desempaqueta el error para ver la causa real
        original_error = error.original
        if isinstance(original_error, discord.errors.Forbidden):
            await ctx.send("¡Ups! Parece que no tengo los permisos necesarios para realizar esta acción. Asegúrate de que mi rol tenga permisos como 'Gestionar Canales' y 'Enviar Mensajes'.")
        else:
            print(f"Error inesperado: {original_error}")
            await ctx.send(f"Ocurrió un error al ejecutar el comando: {original_error}")
    else:
        print(f"Error inesperado: {error}")

# --- Ejecutar el bot ---
if __name__ == "__main__":
    bot_token = os.getenv("DISCORD_TOKEN")
    if not bot_token:
        print("Error: El token de Discord no está configurado en el archivo .env.")
    else:
        try:
            asyncio.run(bot.run(bot_token))
        except discord.LoginFailure:
            print("Error: El token de Discord es inválido.")
        except Exception as e:
            print(f"Ocurrió un error al iniciar el bot: {e}")