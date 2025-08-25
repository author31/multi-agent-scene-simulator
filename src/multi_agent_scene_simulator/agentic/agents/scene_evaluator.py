import dspy

from ...config import settings

class EvaluateResult(dspy.Signature):
    """
    Evaluate the current Blender scene against the user's requirements with component-level analysis.
    
    ANALYSIS APPROACH:
    1. Break down the requirement into specific components (objects, materials, lighting, camera setup)
    2. Check which components are present vs. missing
    3. Assess quality/completeness of existing components
    4. Provide targeted suggestions for missing or incomplete components
    
    OUTPUT FORMAT:
    - Overall match score (0.0-1.0)
    - Component-level assessment:
      * Objects: present/missing, correct placement/style
      * Materials: applied correctly, realistic appearance
      * Lighting: adequate coverage, appropriate mood
      * Camera: proper framing, angle
    - Specific suggestions for next incremental additions
    """
    scene_requirement: str = dspy.InputField(
        desc="The original user-defined specification of the scene (objects, layout, lighting, style, etc.)."
    )
    curr_scene_info: str = dspy.InputField(
        desc="Structured description or metadata of the current scene, including objects, materials, lighting, and camera setup."
    )
    curr_viewport_screenshot: dspy.Image = dspy.InputField(
        desc="A rendered screenshot of the current scene from the active viewport."
    )
    match_score: float = dspy.OutputField(
        desc="Overall similarity score between 0.0 and 1.0, indicating how closely the current scene matches the requirement."
    )
    component_breakdown: dict = dspy.OutputField(
        desc="Detailed component-level analysis: objects, materials, lighting, camera."
    )
    missing_components: list = dspy.OutputField(
        desc="List of specific components that are still missing or incomplete."
    )
    next_priority: str = dspy.OutputField(
        desc="The most important next component to add or improve for maximum scene enhancement."
    )

class SceneEvaluator(dspy.Module):
    def __init__(self, model: str):
        self.model = model
        self.evaluator = dspy.Predict(EvaluateResult)

    def forward(self, scene_requirement: str, curr_scene_info: str, curr_viewport_screenshot: dspy.Image):
        with dspy.context(lm=dspy.LM(self.model, api_base=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)):
            evaluate_result = self.evaluator(scene_requirement=scene_requirement, curr_scene_info=curr_scene_info, curr_viewport_screenshot=curr_viewport_screenshot)
        return {
            "match_score": evaluate_result.match_score,
            "component_breakdown": evaluate_result.component_breakdown,
            "missing_components": evaluate_result.missing_components,
            "next_priority": evaluate_result.next_priority,
            "raw_response": str(evaluate_result)
        }
