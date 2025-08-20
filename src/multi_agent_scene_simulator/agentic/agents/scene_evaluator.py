import dspy

from ...config import settings

class EvaluateResult(dspy.Signature):
    """
    Evaluate how well the current Blender scene matches the user’s initial scene requirements.
    The evaluation considers both structured scene information and the rendered viewport screenshot.
    The agent should output:
      - A numerical similarity score (0.0 = complete mismatch, 1.0 = perfect match).
      - Qualitative suggestions or adjustments to improve alignment with the requirements.
    """
    scene_requirement: str = dspy.InputField(
        desc="The original user-defined specification of the scene (objects, layout, lighting, style, etc.)."
    )
    curr_scene_info: str = dspy.InputField(
        desc="Structured description or metadata of the current scene, such as objects present, their properties, and scene configuration."
    )
    curr_viewport_screenshot: dspy.Image = dspy.InputField(
        desc="A rendered screenshot of the current scene from the active viewport."
    )
    match_score: float = dspy.OutputField(
        desc="A similarity score between 0.0 and 1.0, indicating how closely the current scene matches the requirement."
    )
    suggestion: str = dspy.OutputField(
        desc="Actionable feedback or recommendations to adjust the scene for better alignment with the requirement."
    )

class SceneEvaluator(dspy.Module):
    def __init__(self, model: str):
        self.model = model
        self.evaluator = dspy.Predict(EvaluateResult)

    def forward(self, scene_requirement: str, curr_scene_info: str, curr_viewport_screenshot: dspy.Image):
        with dspy.context(lm=dspy.LM(self.model, api_base=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)):
            evaluate_result = self.evaluator(scene_requirement=scene_requirement, curr_scene_info=curr_scene_info, curr_viewport_screenshot=curr_viewport_screenshot)
        return evaluate_result
