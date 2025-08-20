from ..agentic.agents.lead_agent import LeadAgent
from ..agentic.agents.blender_code_generator import BlenderCodeGenerator
from ..agentic.agents.scene_evaluator import SceneEvaluator
from ..agentic import mcp_client
from ..logger import setup_logger

logger = setup_logger(__name__)

WEAK_MODEL = "openrouter/z-ai/glm-4.5v"
STRONG_MODEL = "openrouter/google/gemini-2.5-flash"
MAX_ITERS = 3

async def execute(requirement: str):
    mcp_client.init_client()
    curr_scene_info = await mcp_client.call_tool("get_scene_info")
    curr_viewport_screenshot = await mcp_client.call_tool("get_viewport_screenshot")

    scene_evaluator = SceneEvaluator(model=STRONG_MODEL)
    lead_agent = LeadAgent(model=STRONG_MODEL)
    blender_code_generator = BlenderCodeGenerator(model=WEAK_MODEL)

    scene_requirement = requirement
    for i in range(MAX_ITERS):
        sub_tasks = lead_agent(
            scene_requirement=scene_requirement,
            curr_scene_info=curr_scene_info[0],
            curr_viewport_screenshot=curr_viewport_screenshot[0]
        )

        for task in sub_tasks:
            logger.info(
                f"Executing task: {task.name}, Instruction: {task.instruction}"
            )
            code = blender_code_generator(instruction=task.instruction)
            await mcp_client.call_tool(
                "execute_blender_code", call_kwargs={"code": code}
            )

        curr_scene_info = await mcp_client.call_tool("get_scene_info")
        curr_viewport_screenshot = await mcp_client.call_tool(
            "get_viewport_screenshot"
        )
        result = scene_evaluator(
            scene_requirement=scene_requirement, 
            curr_scene_info=curr_scene_info, 
            curr_viewport_screenshot=curr_viewport_screenshot
        )

        if result.match_score == 1:
            logger.info("Scene is perfectly matched the user requirement.")
            break

        scene_requirement = result.suggestion
