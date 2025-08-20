import dspy

from ...config import settings

class BlenderPythonCode(dspy.Signature):
    """
    Generate Python code using Blender’s Python API based on a given instruction. 
    The produced code will be executed via `send_command` to create, modify, or query 
    objects within Blender, the open-source 3D creation suite.
    """
    instruction: str = dspy.InputField(
        desc="A detailed and unambiguous description of the desired Blender task or scene operation."
    )
    code: str = dspy.OutputField(
        desc="Valid Python code using Blender's bpy API that fulfills the given instruction."
    )

class BlenderCodeGenerator(dspy.Module):
    def __init__(self, model: str):
        self.model = model
        self.generator = dspy.Predict(BlenderPythonCode)

    def forward(self, instruction: str):
        with dspy.context(lm=dspy.LM(self.model, api_base=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)):
            code = self.generator(instruction=instruction)
        return code
