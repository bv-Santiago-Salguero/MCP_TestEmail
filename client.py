import os
import asyncio
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import McpTool, ToolSet, ListSortOrder, MessageRole
from fastmcp import Client

# Cargar variables de entorno desde el archivo .env
load_dotenv()

async def main():
    async with Client("https://ca-bv-ind-dev-mcpserver-002.purplemoss-090320df.eastus.azurecontainerapps.io/mcp", auth="oauth") as client:
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

        # Inicializar con el Cliente de Agentes
        agents_client = AgentsClient(
            endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
            credential=credential
        )

        # Conectar con el agente
        agent = project_client.agents.get_agent(os.getenv("FOUNDRY_AGENT_ID"))
        print(f"Conectado al agente: {agent.name} (ID: {agent.id})")

        # MCP tool
        mcp_server_url = "https://ca-bv-ind-dev-mcpserver-002.purplemoss-090320df.eastus.azurecontainerapps.io/mcp"
        mcp_server_label = "enviar_correo"

        mcp_tool = McpTool(
            server_label=mcp_server_label,
            server_url=mcp_server_url
        )

        mcp_tool.set_approval_mode("never")

        toolset = ToolSet()
        toolset.add(mcp_tool)

        # Crear un thread (conversación)
        thread = project_client.agents.threads.create()
        print(f"Thread creado con ID: {thread.id}")

        # Conversación
        while True:
            prompt = input("Enter a prompt (or type 'quit' to exit): ")
            if prompt.lower() =="quit":
                break
            if len(prompt) == 0:
                print("Please enter a prompt.")
                continue
            message = agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )

            # Crear y procesar la ejecución del agente con la herramienta MCP
            run = agents_client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=os.getenv("FOUNDRY_AGENT_ID"),
                toolset=toolset
            )
            print(f"Run created with ID: {run.id}")

            # Check run status
            print(f"Run completed with status: {run.status}")
            if run.status == "failed":
                print(f"Run failed: {run.last_error}")

            last_msg = agents_client.messages.get_last_message_text_by_role(
                thread_id=thread.id,
                role=MessageRole.AGENT,
            )
            
            if last_msg:
                print(f"Agent Message: {last_msg.text.value}")

        # Display run steps and tool calls
        run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)
        for step in run_steps:
            print(f"Step {step['id']} status: {step['status']}")

            # Check if there are tool calls in the step details
            step_details = step.get("step_details", {})
            tool_calls = step_details.get("tool_calls", [])

            if tool_calls:
                # Display the MCP tool call details
                print("  MCP Tool calls:")
                for call in tool_calls:
                    print(f"    Tool Call ID: {call.get('id')}")
                    print(f"    Type: {call.get('type')}")
                    print(f"    Type: {call.get('name')}")

            print()  # add an extra newline between steps

    # Fetch and log all messages
    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    print("\nConversation:")
    print("-" * 50)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role.upper()}: {last_text.text.value}")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())