# MCP Server - Funcionalidad de Correo Electrónico

Este servidor MCP proporciona herramientas para enviar correos electrónicos que pueden ser utilizadas por agentes de IA.

## Configuración

1. Copia `.env.example` a `.env` y completa las variables:

```bash
copy .env.example .env
```

2. Configura las credenciales SMTP:
   - **Gmail**: Necesitas una [contraseña de aplicación](https://support.google.com/accounts/answer/185833)
   - **Outlook/Office365**: Usa `smtp.office365.com`
   - **Otros proveedores**: Consulta la documentación de tu proveedor

## Uso con Agente

El agente puede usar la herramienta `enviar_correo` con estos parámetros:

```python
enviar_correo(
    destinatario="usuario@ejemplo.com",
    asunto="Asunto del correo",
    cuerpo="Contenido del mensaje"
)
```

## Ejemplo de integración con Azure AI Agent

```python
# El agente puede llamar a la herramienta directamente
resultado = agent.call_tool(
    "enviar_correo",
    {
        "destinatario": "cliente@empresa.com",
        "asunto": "Confirmación de reunión",
        "cuerpo": "Tu reunión está confirmada para mañana a las 10:00 AM"
    }
)
```

## Ejecución

```bash
# Iniciar el servidor MCP
python server.py

# En otra terminal, ejecutar el cliente
python client.py
```