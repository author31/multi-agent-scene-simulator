from ..agentic.agents.lead_agent import LeadAgent
from ..agentic import mcp_client

WEAK_MODEL = "openrouter/z-ai/glm-4.5v"
STRONG_MODEL = "openrouter/google/gemini-2.5-flash"

def execute(scene_requirement: str):
    mcp_client.init_client()
    curr_scene_info = mcp_client.call_tool("get_scene_info")
    curr_viewport_screenshot = mcp_client.call_tool("get_viewport_screenshot")


    sub_agent_registry = {
         "asset_finder": AssetFinder(),
        "blender_code_generator": BlenderCodeGenerator()
    }

    lead_agent = LeadAgent(model=STRONG_MODEL)
    sub_tasks = lead_agent(
        scene_requirement=scene_requirement,
        curr_scene_info=curr_scene_info,
        curr_viewport_screenshot=curr_viewport_screenshot
    )
