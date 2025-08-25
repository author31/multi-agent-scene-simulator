import dspy
import json
from ..config import settings
from .agents.lead_agent import LeadAgent 


from dspy.teleprompt import COPRO




class PromptImageJudge(dspy.Signature):
    """Determine if the generated scene matches the scene description."""
    scene_description: str = dspy.InputField()
    generated_image: dspy.Image = dspy.InputField()
    is_match: bool = dspy.OutputField()

def load_examples():
    with open(settings.DSPY_EXAMPLE_FP, "r") as buf:
        raw_data = json.load(buf)

    return [
        dspy.Example(
            scene_description=data["scene_description"]
        ).with_input('scene_description')
        for data in raw_data
    ]

def prompt_image_match(example, pred, trace=None) -> float:
    assessor = dspy.Predict(PromptImageJudge)
    assert "scene_description" in example, "Missing 'scene_description' from example"
    result = assessor(example.scene_description)
    return 1. if result.is_match else 0.


def run_optimization():
    optimizer = dspy.MIPROv2(metric=prompt_image_match, auto="light")
    optimize_examples = load_examples()

    # lead agent does return prediction of an image???
    optimized = optimizer.compile(LeadAgent(settings.STRONG_MODEL), trainset=optimize_examples, max_bootstrapped_demos=3, max_labeled_demos=4)


