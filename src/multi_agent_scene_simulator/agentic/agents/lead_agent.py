import dspy

from ...config import settings
from ..schemas import SubTask


class TaskDecomposer(dspy.Signature):
    """
    You are given a high-level requirement for a Blender scene. Your task is to decompose this requirement into a clear, structured list of subtasks that a 3D artist or automated system can follow.
    - Break down the requirement into sequential and/or parallel subtasks.
    - Each subtask should be atomic, actionable, and Blender-relevant (e.g., "Model the main character," "Set up three-point lighting," "Apply realistic glass material," "Animate camera movement," "Render final frames").
    - Organize subtasks in logical order of execution.
    - Ensure the subtasks cover all major aspects: modeling, texturing, materials, lighting, animation, simulation, rendering, and post-processing, if applicable.
    - Keep the list concise but complete, avoiding overly vague steps.
    """
    scene_requirement: str = dspy.InputField(desc="Users requirement of the scene.")
    curr_scene_info: str = dspy.InputField(desc="Current scene info.")
    curr_viewport_screenshot: dspy.Image = dspy.InputField(desc="Current screenshot of the viewport.")
    sub_tasks: list[SubTask] = dspy.OutputField(desc="A list of sub tasks.")


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

    def forward(self, scene_requirement: str, curr_scene_info: str, curr_viewport_screenshot: dspy.Image):
        with dspy.context(lm=dspy.LM(self.model, api_base=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)):
            output = self.decomposer(scene_requirement=scene_requirement, curr_scene_info=curr_scene_info, curr_viewport_screenshot=curr_viewport_screenshot)
        return [sub_task for sub_task in output.sub_tasks]
