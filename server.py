import sys
from fastmcp import FastMCP
from fastmcp.server.auth.providers.azure import AzureProvider
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from fastmcp.server.dependencies import get_access_token
# from microsoft.graph import GraphServiceClient
# from microsoft.graph.models import Message, ItemBody, BodyType, Recipient, EmailAddress

# Cargar variables de entorno
load_dotenv()

# Configurar autenticación con Azure AD
auth_provider = AzureProvider(
    client_id=os.getenv("OAUTH2E_CLIENT_ID"),
    client_secret=os.getenv("OAUTH2E_CLIENT_SECRET"),
    tenant_id=os.getenv("OAUTH2E_TENANT_ID"), 
    base_url=os.getenv("OAUTH2E_BASE_URL"),
    required_scopes=os.getenv("OAUTH2E_REQUIRED_SCOPES").split(",")
)

# Inicializar FastMCP
mcp = FastMCP(name='TestEmail', auth=auth_provider)

# Tool de prueba (Información del usuario autenticado)
@mcp.tool
async def get_user_info() -> dict:
    """Returns information about the authenticated Azure user."""
    token = get_access_token()
    if not token or not token.claims:  # Validar que el token y los claims existan
        raise ValueError("Token inválido o no autenticado")
    
    # The AzureProvider stores user data in token claims
    return {
        "azure_id": token.claims.get("sub"),
        "email": token.claims.get("email"),
        "name": token.claims.get("name"),
        "job_title": token.claims.get("job_title"),
        "office_location": token.claims.get("office_location")
    }


@mcp.tool
def enviar_correo(
    destinatario: list,
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
        destinatario: Dirección de email del destinatario o lista de direcciones de email
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
        remitente = remitente or os.getenv('EMAIL_REMITENTE')
        smtp_server = smtp_server or os.getenv('SMTP_SERVER')
        smtp_usuario = smtp_usuario or os.getenv('SMTP_USUARIO')
        smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')
        smtp_port = smtp_port or os.getenv('SMTP_PORT')
                
        # Forzar destinatario como lista
        if isinstance(destinatario, str):
            destinatario = [destinatario]
        
        # Crear el mensaje
        mensaje = MIMEMultipart()
        mensaje['From'] = remitente
        mensaje['To'] = ', '.join(destinatario)  # Unir destinatarios con comas
        mensaje['Subject'] = asunto
        mensaje.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
        
        # Conectar y enviar
        with smtplib.SMTP(smtp_server, smtp_port) as servidor:
            servidor.starttls()
            servidor.login(smtp_usuario, smtp_password)
            servidor.sendmail(remitente, destinatario, mensaje.as_string())
        
        destinatarios_str = ', '.join(destinatario)
        return f"Correo enviado exitosamente a {destinatarios_str}"
    
    except Exception as e:
        return f"Error al enviar correo: {str(e)}"

@mcp.tool
def enviar_correo_graph(
    destinatarios: List[str],
    asunto: str,
    cuerpo: str,
    remitente: Optional[str] = None,
    client_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    client_secret: Optional[str] = None
) -> str:
    """
    Envía un correo electrónico usando Microsoft Graph API.
    
    Args:
        destinatarios: Lista de direcciones de email de los destinatarios
        asunto: Asunto del correo
        cuerpo: Contenido del mensaje (HTML)
        remitente: Email del remitente (por defecto usa variable de entorno GRAPH_EMAIL_FROM)
        client_id: Client ID de Azure AD (por defecto usa variable de entorno GRAPH_CLIENT_ID)
        tenant_id: Tenant ID de Azure AD (por defecto usa variable de entorno GRAPH_TENANT_ID)
        client_secret: Client Secret de Azure AD (por defecto usa variable de entorno GRAPH_CLIENT_SECRET)
    
    Returns:
        Mensaje de confirmación o error
    """
    try:
        # Usar variables de entorno como valores por defecto
        client_id = client_id or os.getenv('AGRAPH_CLIENT_ID')
        tenant_id = tenant_id or os.getenv('AZURE_TENANT_ID')
        client_secret = client_secret or os.getenv('AZURE_CLIENT_SECRET')
        remitente = remitente or os.getenv('GRAPH_EMAIL_FROM')
        
        # Validar parámetros requeridos
        if not all([client_id, tenant_id, client_secret, remitente]):
            return "Error: Faltan credenciales de Microsoft Graph. Verifica las variables de entorno."
        
        if not destinatarios:
            return "Error: La lista de destinatarios no puede estar vacía"
        
        # Crear credencial y cliente de Graph
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        graph_client = GraphServiceClient(credential)
        
        # Crear lista de destinatarios para Graph
        recipients = []
        for email in destinatarios:
            recipients.append(Recipient(
                email_address=EmailAddress(address=email)
            ))
        
        # Crear el mensaje
        message = Message(
            subject=asunto,
            body=ItemBody(
                content_type=BodyType.Html,
                content=cuerpo
            ),
            to_recipients=recipients
        )
        
        # Enviar el mensaje usando Graph API
        graph_client.users.by_user_id(remitente).send_mail.post(
            body={
                "message": message,
                "save_to_sent_items": True
            }
        )
        
        destinatarios_str = ', '.join(destinatarios)
        return f"Correo enviado exitosamente via Microsoft Graph a {destinatarios_str}"
        
    except Exception as e:
        return f"Error al enviar correo via Microsoft Graph: {str(e)}"

@mcp.resource('resource://Email')
def correo_electronico() -> str:
    """
    Proporciona información sobre cómo configurar el sistema de correo.
    """
    return """
    Configuración del Sistema de Correo Electrónico
    ================================================
    
    MÉTODO 1: SMTP (herramienta enviar_correo)
    Variables de entorno necesarias:
    - EMAIL_REMITENTE: Email del remitente
    - SMTP_SERVER: Servidor SMTP (ej: smtp.gmail.com, smtp.office365.com)
    - SMTP_USUARIO: Usuario para autenticación SMTP
    - SMTP_PASSWORD: Contraseña o token de aplicación
    
    MÉTODO 2: Microsoft Graph API (herramienta enviar_correo_graph)
    Variables de entorno necesarias:
    - GRAPH_CLIENT_ID: Client ID de la aplicación Azure AD
    - GRAPH_TENANT_ID: Tenant ID de Azure AD
    - GRAPH_CLIENT_SECRET: Client Secret de la aplicación Azure AD
    - GRAPH_EMAIL_FROM: Email del remitente autorizado en Azure AD
    
    Ejemplos de uso:
    
    SMTP - Un destinatario:
    - destinatario: "usuario@ejemplo.com"
    - asunto: "Asunto del correo"
    - cuerpo: "Contenido del mensaje"
    
    SMTP - Múltiples destinatarios:
    - destinatario: ["usuario1@ejemplo.com", "usuario2@ejemplo.com"]
    - asunto: "Asunto del correo"
    - cuerpo: "Contenido del mensaje"
    
    Graph API:
    - destinatarios: ["usuario1@ejemplo.com", "usuario2@ejemplo.com"]
    - asunto: "Asunto del correo"
    - cuerpo: "<h1>Contenido HTML del mensaje</h1>"
    
    Notas:
    - Para Gmail SMTP, necesitas una contraseña de aplicación si tienes 2FA activado.
    - Para Microsoft Graph, necesitas registrar una aplicación en Azure AD con permisos Mail.Send.
    """

@mcp.prompt
def prompt_enviar_correo() -> str:
    """
    Prompt para que el agente envíe un correo electrónico.
    """
    return """Eres un asistente que puede enviar correos electrónicos usando dos métodos:

1. SMTP (herramienta 'enviar_correo'): Para correos simples usando servidores SMTP tradicionales
2. Microsoft Graph API (herramienta 'enviar_correo_graph'): Para correos a través de Microsoft 365/Outlook

Cuando el usuario solicite enviar un correo, debes:
1. Obtener el destinatario, asunto y cuerpo del mensaje
2. Elegir el método más apropiado (SMTP para texto plano, Graph para HTML/funciones avanzadas)
3. Usar la herramienta correspondiente con los parámetros necesarios
4. Confirmar al usuario si el envío fue exitoso o reportar errores

Ejemplos de uso:

SMTP:
- destinatario: "juan@ejemplo.com" (o lista para múltiples)
- asunto: "Reunión"
- cuerpo: "Hola, ¿podemos reunirnos mañana?"

Microsoft Graph:
- destinatarios: ["juan@ejemplo.com", "maria@ejemplo.com"]
- asunto: "Reunión de equipo"
- cuerpo: "<h2>Reunión de equipo</h2><p>Hola, ¿podemos reunirnos mañana?</p>"
"""


if __name__ == "__main__":
    try:
        # Initialize and run the server
        print("Starting MCP server...")
        mcp.run(transport="http", host="0.0.0.0", port=80)
    except Exception as e:
        print(f"Error while running MCP server: {e}", file=sys.stderr)