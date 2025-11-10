import os
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents import AgentsClient

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Inicializar Credenciales de Azure
credential = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET")
) 

# Inicializar el Cliente del Proyecto de Azure AI Foundry
project_client = AIProjectClient(
    endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
    credential=credential
)

# Conectar con el agente
agent = project_client.agents.get_agent(os.getenv("FOUNDRY_AGENT_ID"))
print(f"Conectado al agente: {agent.name} (ID: {agent.id})")

# MCP tool





# Crear un thread (conversación)
thread = project_client.agents.threads.create()

# Enviar un mensaje
message = project_client.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="¿Cuál es la información sobre persona natural?"
)

# Ejecutar el agente
run = project_client.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=os.getenv("FOUNDRY_AGENT_ID")
)

# Obtener respuesta
messages = project_client.agents.messages.list(thread_id=thread.id)
for msg in messages:
    if msg.role == "assistant":
        print(f"Respuesta: {msg.content[0].text.value}")