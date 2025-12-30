from fastmcp import Client
import asyncio

async def main():
    # The client will automatically handle Azure OAuth
    async with Client("https://ca-bv-ind-dev-mcpserver-002.purplemoss-090320df.eastus.azurecontainerapps.io/mcp", auth="oauth") as client:
        # First-time connection will open Azure login in your browser
        print("✓ Authenticated with Azure!")
        
        # Test the protected tool
        result = await client.call_tool("get_user_info")

        # print(f"Token de registro completo: {result}")
        print(f"Usuario autenticado: {result.structured_content['name']}")
        print(f"Azure ID: {result.structured_content['azure_id']}")

if __name__ == "__main__":
    asyncio.run(main())