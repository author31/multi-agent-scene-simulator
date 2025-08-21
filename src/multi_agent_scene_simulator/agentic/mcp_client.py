from fastmcp import Client

from .schemas import ImageResult, ToolResult

BLENDER_MCP_CONFIG = {
    "mcpServers": {
        "blender-mcp": {"command": "uvx", "args": ["blender-mcp"]}
    }
}

client = None

def init_client():
    global client
    if client: return client
    
    client = Client(BLENDER_MCP_CONFIG)
    return client


async def list_tools():
    global client
    if not client: 
        raise RuntimeError("MCP client is not initialized properply.")

    async with client:
        tools = await client.list_tools()

    return tools

async def call_tool(tool_name, call_kwargs: dict | None = None):
    global client
    if not client: 
        raise RuntimeError("MCP client is not initialized properply.")

    tool_results = []
    async with client:
        results = await client.call_tool(tool_name, arguments=call_kwargs or {})
        for result in results:
            raw_result = result.model_dump()
            if (result_type:=raw_result.get("type")) and result_type == "text":
                tool_results.append(
                    ToolResult(tool_name=tool_name, tool_result=raw_result["text"])
                )
            elif (result_type:=raw_result.get("type")) and result_type == "image":
                b64_data = raw_result.get("data") 
                if not b64_data: continue

                tool_results.append(
                    ImageResult(tool_name=tool_name, image_data=b64_data)
                )
                
    return tool_results
