from ..agentic import mcp_client
from ..agentic.agents.blender_code_generator import BlenderCodeGenerator
from ..agentic.agents.lead_agent import LeadAgent
from ..agentic.agents.scene_evaluator import SceneEvaluator
from ..config import settings
from ..logger import setup_logger
from .context_manager import ContextManager
from .environment_probe import EnvironmentProbe
from .scene_parser import SceneParser
from .failure_analyzer import FailureAnalyzer, TaskContext

logger = setup_logger(__name__)

MAX_ITERS = 5  # Increased for incremental building

async def execute(requirement: str):
    mcp_client.init_client()

    # Initialize new feedback system components
    environment_probe = EnvironmentProbe()
    scene_parser = SceneParser()
    failure_analyzer = FailureAnalyzer()
    
    # Initialize context manager
    context = ContextManager()
    context.set_initial_requirement(requirement)
    
    # Get initial scene info
    curr_scene_info = await mcp_client.call_tool("get_scene_info")
    curr_viewport_screenshot = await mcp_client.call_tool("get_viewport_screenshot")
    
    # Parse scene info for initial state using new parser
    detailed_scene_state = scene_parser.parse_scene_info(curr_scene_info[0])
    initial_scene_state = scene_state_to_dict(detailed_scene_state)
    context.store_scene_state(initial_scene_state)
    
    # Perform comprehensive environment analysis
    detailed_analysis = environment_probe.analyze_complete_scene(curr_scene_info[0])
    context.store_detailed_analysis(detailed_analysis)
    
    # Store initial tool results
    context.store_tool_result("get_scene_info", curr_scene_info, {"iteration": 0})
    context.store_tool_result("get_viewport_screenshot", curr_viewport_screenshot, {"iteration": 0})

    scene_evaluator = SceneEvaluator(model=settings.STRONG_MODEL)
    lead_agent = LeadAgent(model=settings.STRONG_MODEL)
    blender_code_generator = BlenderCodeGenerator(model=settings.WEAK_MODEL)
    

    scene_requirement = requirement
    for i in range(MAX_ITERS):
        context.start_iteration(i + 1)
        
        # Get context for lead agent
        context_for_lead = context.get_context_for_llm()
        
        lead_response = lead_agent(
            scene_requirement=scene_requirement,
            curr_scene_info=curr_scene_info[0],
            curr_viewport_screenshot=curr_viewport_screenshot[0],
            context_for_lead=context_for_lead
        )
        
        sub_tasks = lead_response["sub_tasks"]
        
        
        # Store lead agent response
        context.store_lead_response(sub_tasks, lead_response["raw_response"])

        # Track if any tasks were successfully completed
        tasks_completed = 0
        
        for task in sub_tasks:
            logger.info(
                f"Executing task: {task.name}, Instruction: {task.instruction}"
            )
            code_response = blender_code_generator(
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
            
            # Get current scene state and detailed analysis before execution
            scene_before = scene_parser.parse_scene_info(curr_scene_info[0])
            analysis_before = environment_probe.analyze_complete_scene(curr_scene_info[0])
            
            try:
                await mcp_client.call_tool(
                    "execute_blender_code", call_kwargs={"code": code}
                )
                tasks_completed += 1
                
                # Get updated scene state and analysis after successful execution
                updated_scene_info_task = await mcp_client.call_tool("get_scene_info")
                analysis_after = environment_probe.analyze_complete_scene(updated_scene_info_task[0])
                
                # Update component progress with detailed analysis
                component_type = extract_component_type(task.name)
                context.update_component_progress(
                    component_type=component_type,
                    component_name=task.name,
                    status="complete",
                    details={
                        "instruction": task.instruction,
                        "quality_metrics": analysis_after.get("summary", {}),
                        "issues_resolved": len(analysis_before.get("issues", [])) - len(analysis_after.get("issues", [])),
                        "improvement_score": analysis_after.get("summary", {}).get("overall_score", 0.0)
                    }
                )
                
            except Exception as e:
                logger.error(f"Task execution failed: {task.name}, Error: {e}")
                
                # Get updated scene state and analysis after failure
                updated_scene_info = await mcp_client.call_tool("get_scene_info")
                scene_after = scene_parser.parse_scene_info(updated_scene_info[0])
                analysis_after = environment_probe.analyze_complete_scene(updated_scene_info[0])
                
                # Perform detailed failure analysis
                task_context_obj = TaskContext(
                    task_name=task.name,
                    instruction=task.instruction,
                    generated_code=code_response["code"],
                    error_message=str(e),
                    error_type=type(e).__name__,
                    stack_trace=str(e),
                    scene_state_before=scene_state_to_dict(scene_before),
                    scene_state_after=scene_state_to_dict(scene_after),
                    attempt_number=1,
                    previous_failures=[]
                )
                
                analysis = failure_analyzer.analyze_task_failure(task_context_obj)
                
                # Store detailed failure analysis
                context.update_component_progress(
                    component_type=extract_component_type(task.name),
                    component_name=task.name,
                    status="failed",
                    details={
                        "error": str(e),
                        "instruction": task.instruction,
                        "failure_type": analysis.failure_type,
                        "root_cause": analysis.root_cause,
                        "specific_issue": analysis.specific_issue,
                        "suggested_fix": analysis.suggested_fix,
                        "recovery_complexity": analysis.recovery_complexity,
                        "likely_success_rate": analysis.likely_success_rate,
                        "alternative_approaches": analysis.alternative_approaches,
                        "environment_impact": {
                            "issues_before": analysis_before.get("issues", []),
                            "issues_after": analysis_after.get("issues", []),
                            "quality_regression": max(0, analysis_before.get("summary", {}).get("overall_score", 0) - analysis_after.get("summary", {}).get("overall_score", 0))
                        }
                    }
                )
                
                # Log detailed analysis for debugging
                logger.info(f"Failure analysis for {task.name}: {analysis.specific_issue}")
                logger.info(f"Suggested fix: {analysis.suggested_fix}")
                logger.info(f"Recovery complexity: {analysis.recovery_complexity}/5")
                logger.info(f"Environmental impact: {analysis.scene_impact}")

        # Update scene state after task execution
        curr_scene_info = await mcp_client.call_tool("get_scene_info")
        curr_viewport_screenshot = await mcp_client.call_tool("get_viewport_screenshot")
        
        # Parse and store updated scene state using new parser
        updated_scene_state = scene_parser.parse_scene_info(curr_scene_info[0])
        context.store_scene_state(scene_state_to_dict(updated_scene_state))
        
        # Perform comprehensive post-execution analysis
        detailed_analysis = environment_probe.analyze_complete_scene(curr_scene_info[0])
        context.store_detailed_analysis(detailed_analysis)
        
        # Store tool results
        context.store_tool_result("get_scene_info", curr_scene_info, {"iteration": i + 1})
        context.store_tool_result("get_viewport_screenshot", curr_viewport_screenshot, {"iteration": i + 1})
        
        # Enhanced evaluation with rich environmental data
        eval_response = scene_evaluator(
            scene_requirement=scene_requirement, 
            curr_scene_info=curr_scene_info[0], 
            curr_viewport_screenshot=curr_viewport_screenshot[0]
        )
        
        # Store component-level evaluation with rich analysis
        for missing_comp in eval_response["missing_components"]:
            context.update_component_progress(
                component_type=extract_component_type(missing_comp),
                component_name=missing_comp,
                status="missing",
                details={
                    "priority": "high",
                    "environment_context": detailed_analysis.get("summary", {}),
                    "issues_remaining": detailed_analysis.get("issues", [])
                }
            )
        
        # Store scene evaluation with detailed analysis
        context.store_evaluation(
            match_score=eval_response["match_score"],
            suggestion=eval_response["next_priority"],
            detailed_analysis=detailed_analysis,
            quality_metrics=detailed_analysis.get("summary", {}),
            issues=detailed_analysis.get("issues", []),
            recommendations=detailed_analysis.get("recommendations", [])
        )
        
        result = eval_response
        
        context.complete_iteration()

        if result["match_score"] >= 0.9:  # Adjusted threshold for practical completion
            logger.info(f"Scene sufficiently matched user requirement with score {result['match_score']}")
            context.set_final_result({
                "success": True,
                "iterations": i + 1,
                "final_match_score": result["match_score"],
                "final_missing_components": result["missing_components"],
                "component_breakdown": result["component_breakdown"]
            })
            break

        # Only update requirement if we made progress
        if tasks_completed > 0 or len(eval_response["missing_components"]) < len([c for c in context.component_registry.values() if c.status == "missing"]):
            scene_requirement = result["next_priority"]
        else:
            # No progress made, try broader approach
            scene_requirement = f"Add missing elements to complete the scene: {', '.join(result['missing_components'][:3])}"
    else:
        # Max iterations reached
        context.set_final_result({
            "success": False,
            "iterations": MAX_ITERS,
            "reason": "Maximum iterations reached",
            "final_missing_components": eval_response["missing_components"],
            "component_breakdown": eval_response["component_breakdown"]
        })
    
    # Create final checkpoint
    context.create_checkpoint(len(context.iterations))
    
    # Save context to file for debugging/analysis
    context.save_to_file("execution_context.json")
    
    return context


def scene_state_to_dict(scene_state) -> dict[str, object]:
    """Convert SceneState to dictionary format for context storage."""
    from .scene_parser import scene_parser
    return scene_parser.scene_state_to_dict(scene_state)


def parse_scene_info(scene_info: str) -> dict:
    """Parse scene info string into structured scene state"""
    # This is a simplified parser - in practice, you'd want more robust parsing
    try:
        # Try to parse as JSON if the format supports it
        if isinstance(scene_info, dict):
            return scene_info
        elif isinstance(scene_info, str):
            # Basic string parsing for typical scene info format
            lines = scene_info.split('\n')
            objects = []
            lights = []
            cameras = []
            materials = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('Object:') or line.startswith('-'):
                    objects.append({"name": line, "type": "object"})
                elif line.startswith('Light:'):
                    lights.append({"name": line, "type": "light"})
                elif line.startswith('Camera:'):
                    cameras.append({"name": line, "type": "camera"})
                elif line.startswith('Material:'):
                    materials.append({"name": line, "type": "material"})
            
            return {
                "objects": objects,
                "lights": lights,
                "cameras": cameras,
                "materials": materials,
                "scene_info": {"raw": scene_info}
            }
    except Exception:
        # Fallback to basic structure
        return {
            "objects": [],
            "lights": [],
            "cameras": [],
            "materials": [],
            "scene_info": {"raw": str(scene_info)}
        }


def extract_component_type(task_name: str) -> str:
    """Extract component type from task name for progress tracking"""
    task_lower = task_name.lower()
    if any(word in task_lower for word in ['light', 'lighting', 'illumination']):
        return "light"
    elif any(word in task_lower for word in ['camera', 'view', 'shot']):
        return "camera"
    elif any(word in task_lower for word in ['material', 'texture', 'shader']):
        return "material"
    elif any(word in task_lower for word in ['object', 'model', 'create', 'add']):
        return "object"
    else:
        return "component"
