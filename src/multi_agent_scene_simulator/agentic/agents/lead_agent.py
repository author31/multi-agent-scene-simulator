import dspy

from ...config import settings
from ..schemas import SubTask


class TaskDecomposer(dspy.Signature):
    """
    You are given a high-level requirement for a Blender scene. Your task is to analyze what components are still missing or need improvement to achieve the complete scene requirement.
    
    APPROACH:
    1. First, analyze the current scene state to understand what already exists
    2. Identify gaps between current state and the requirement
    3. Generate ONLY the missing or incomplete components as subtasks
    4. Focus on incremental additions, not rebuilding existing elements
    
    GUIDELINES:
    - Each subtask should add a specific missing component (object, material, light, camera, etc.)
    - Use Blender's existing objects when possible (reference by name if they exist)
    - Tasks should be atomic: "add wooden table", "apply glass material to window", "add rim light"
    - Avoid tasks that would replace or remove existing work
    - Consider the current scene composition and add complementary elements
    - If something exists but is incomplete, create tasks to improve/complete it
    
    OUTPUT FORMAT:
    - Only generate subtasks for what's actually missing or needs improvement
    - Be specific about what each task should ADD to the existing scene
    """
    scene_requirement: str = dspy.InputField(desc="Users requirement of the scene.")
    curr_scene_info: str = dspy.InputField(desc="Current scene info.")
    curr_viewport_screenshot: dspy.Image = dspy.InputField(desc="Current screenshot of the viewport.")
    context_for_lead: str = dspy.InputField(desc="Previous execution context including current scene state, component progress, and what's already been built.")
    sub_tasks: list[SubTask] = dspy.OutputField(desc="A list of sub tasks for missing or incomplete components only.")


class AssetFinder(dspy.Module):
    """
    CONCERN: Where should this be fit in the big picture?
    """
    def __init__(self):
        self.allow_tool_list = [
            "get_polyhaven_categories", 
            "search_polyhaven_assets", 
            "download_polyhaven_asset", 
            "set_texture"
        ]


class LeadAgent(dspy.Module):
    def __init__(self, model: str):
        self.model = model
        self.decomposer = dspy.Predict(TaskDecomposer)

    def forward(self, scene_requirement: str, curr_scene_info: str, curr_viewport_screenshot: dspy.Image, context_for_lead: str = ""):
        with dspy.context(
            lm=dspy.LM(
                self.model, 
                api_base=settings.LLM_BASE_URL, 
                api_key=settings.LLM_API_KEY,
                temperature=0.7,
                max_tokens=settings.LLM_MAX_TOKENS
            )
        ):
            output = self.decomposer(
                scene_requirement=scene_requirement, 
                curr_scene_info=curr_scene_info, 
                curr_viewport_screenshot=curr_viewport_screenshot,
                context_for_lead=context_for_lead
            )
            assert hasattr(output, "sub_tasks"), "The LLM didnt response with `sub_tasks` attr"
        return {
            "sub_tasks": [sub_task for sub_task in output.sub_tasks],
            "raw_response": str(output)
        }
