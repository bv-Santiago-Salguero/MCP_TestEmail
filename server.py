from fastmcp import FastMCP
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar FastMCP
mcp = FastMCP('Funcionalidad Prueba')

@mcp.tool
def enviar_correo(
    destinatario: str,
    asunto: str,
    cuerpo: str,
    remitente: Optional[str] = None,
    smtp_server: Optional[str] = None,
    smtp_port: Optional[int] = 587,
    smtp_usuario: Optional[str] = None,
    smtp_password: Optional[str] = None
) -> str:
    """
    Envía un correo electrónico a través de SMTP.
    
    Args:
        destinatario: Dirección de email del destinatario
        asunto: Asunto del correo
        cuerpo: Contenido del mensaje
        remitente: Email del remitente (por defecto usa variable de entorno EMAIL_REMITENTE)
        smtp_server: Servidor SMTP (por defecto usa variable de entorno SMTP_SERVER)
        smtp_port: Puerto SMTP (por defecto 587)
        smtp_usuario: Usuario SMTP (por defecto usa variable de entorno SMTP_USUARIO)
        smtp_password: Contraseña SMTP (por defecto usa variable de entorno SMTP_PASSWORD)
    
    Returns:
        Mensaje de confirmación o error
    """
    try:
        # Usar variables de entorno como valores por defecto
        remitente = remitente or os.getenv("EMAIL_REMITENTE")
        smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_usuario = smtp_usuario or os.getenv("SMTP_USUARIO")
        smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        
        if not all([remitente, smtp_server, smtp_usuario, smtp_password]):
            return "Error: Faltan configuraciones SMTP. Verifica las variables de entorno o parámetros."
        
        # Crear el mensaje
        mensaje = MIMEMultipart()
        mensaje['From'] = remitente
        mensaje['To'] = destinatario
        mensaje['Subject'] = asunto
        mensaje.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
        
        # Conectar y enviar
        with smtplib.SMTP(smtp_server, smtp_port) as servidor:
            servidor.starttls()
            servidor.login(smtp_usuario, smtp_password)
            servidor.send_message(mensaje)
        
        return f"Correo enviado exitosamente a {destinatario}"
    
    except Exception as e:
        return f"Error al enviar correo: {str(e)}"

@mcp.resource('resource://Email')
def correo_electronico() -> str:
    """
    Proporciona información sobre cómo configurar el sistema de correo.
    """
    return """
    Configuración del Sistema de Correo Electrónico
    ================================================
    
    Variables de entorno necesarias:
    - EMAIL_REMITENTE: Email del remitente
    - SMTP_SERVER: Servidor SMTP (ej: smtp.gmail.com, smtp.office365.com)
    - SMTP_USUARIO: Usuario para autenticación SMTP
    - SMTP_PASSWORD: Contraseña o token de aplicación
    
    Ejemplo de uso de la herramienta enviar_correo:
    - destinatario: "usuario@ejemplo.com"
    - asunto: "Asunto del correo"
    - cuerpo: "Contenido del mensaje"
    
    Nota: Para Gmail, necesitas una contraseña de aplicación si tienes 2FA activado.
    """

@mcp.prompt
def prompt_enviar_correo() -> str:
    """
    Prompt para que el agente envíe un correo electrónico.
    """
    return """Eres un asistente que puede enviar correos electrónicos.

Cuando el usuario solicite enviar un correo, debes:
1. Obtener el destinatario, asunto y cuerpo del mensaje
2. Usar la herramienta 'enviar_correo' con los parámetros necesarios
3. Confirmar al usuario si el envío fue exitoso o reportar errores

Ejemplo de solicitud:
Usuario: "Envía un correo a juan@ejemplo.com con asunto 'Reunión' y mensaje 'Hola, ¿podemos reunirnos mañana?'"

Debes usar la herramienta enviar_correo con:
- destinatario: "juan@ejemplo.com"
- asunto: "Reunión"
- cuerpo: "Hola, ¿podemos reunirnos mañana?"
"""


if __name__ == "__main__":
    mcp.run()