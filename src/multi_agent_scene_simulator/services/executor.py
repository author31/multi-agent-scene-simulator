from ..agentic.agents.lead_agent import LeadAgent
from ..agentic.agents.blender_code_generator import BlenderCodeGenerator
from ..agentic.agents.scene_evaluator import SceneEvaluator
from ..agentic import mcp_client
from ..logger import setup_logger
from .context_manager import ContextManager

logger = setup_logger(__name__)

WEAK_MODEL = "openrouter/z-ai/glm-4.5v"
STRONG_MODEL = "openrouter/google/gemini-2.5-flash"
MAX_ITERS = 3

async def execute(requirement: str):
    mcp_client.init_client()
    
    # Initialize context manager
    context = ContextManager()
    context.set_initial_requirement(requirement)
    
    # Get initial scene info
    curr_scene_info = await mcp_client.call_tool("get_scene_info")
    curr_viewport_screenshot = await mcp_client.call_tool("get_viewport_screenshot")
    
    # Store initial tool results
    context.store_tool_result("get_scene_info", curr_scene_info, {"iteration": 0})
    context.store_tool_result("get_viewport_screenshot", curr_viewport_screenshot, {"iteration": 0})

    scene_evaluator = SceneEvaluator(model=STRONG_MODEL)
    lead_agent = LeadAgent(model=STRONG_MODEL)
    blender_code_generator = BlenderCodeGenerator(model=STRONG_MODEL)

    scene_requirement = requirement
    for i in range(MAX_ITERS):
        context.start_iteration(i + 1)
        
        # Get context for lead agent
        context_for_lead = context.get_context_for_llm()
        
        lead_response = lead_agent.forward(
            scene_requirement=scene_requirement,
            curr_scene_info=curr_scene_info[0],
            curr_viewport_screenshot=curr_viewport_screenshot[0],
            context_for_lead=context_for_lead
        )
        
        sub_tasks = lead_response["sub_tasks"]
        
        # Store lead agent response
        context.store_lead_response(sub_tasks, lead_response["raw_response"])

        for task in sub_tasks:
            logger.info(
                f"Executing task: {task.name}, Instruction: {task.instruction}"
            )
            code_response = blender_code_generator.forward(
                instruction=task.instruction
            )
            
            # Store code generation
            context.store_code_generation(
                task_name=task.name,
                instruction=task.instruction,
                code=code_response["code"],
                raw_response=code_response["raw_response"]
            )
            
            code = code_response["code"]
            
            await mcp_client.call_tool(
                "execute_blender_code", call_kwargs={"code": code}
            )

        curr_scene_info = await mcp_client.call_tool("get_scene_info")
        curr_viewport_screenshot = await mcp_client.call_tool(
            "get_viewport_screenshot"
        )
        
        # Store tool results
        context.store_tool_result("get_scene_info", curr_scene_info, {"iteration": i + 1})
        context.store_tool_result("get_viewport_screenshot", curr_viewport_screenshot, {"iteration": i + 1})
        
        eval_response = scene_evaluator.forward(
            scene_requirement=scene_requirement, 
            curr_scene_info=curr_scene_info[0], 
            curr_viewport_screenshot=curr_viewport_screenshot[0]
        )
        
        # Store scene evaluation
        context.store_evaluation(
            match_score=eval_response["match_score"],
            suggestion=eval_response["suggestion"],
        )
        
        result = eval_response
        
        context.complete_iteration()

        if result["match_score"] == 1:
            logger.info("Scene is perfectly matched the user requirement.")
            context.set_final_result({
                "success": True,
                "iterations": i + 1,
                "final_match_score": result["match_score"],
                "final_suggestion": result["suggestion"]
            })
            break

        scene_requirement = result["suggestion"]
    else:
        # Max iterations reached
        context.set_final_result({
            "success": False,
            "iterations": MAX_ITERS,
            "reason": "Maximum iterations reached"
        })
    
    # Save context to file for debugging/analysis
    context.save_to_file("execution_context.json")
    
    return context
