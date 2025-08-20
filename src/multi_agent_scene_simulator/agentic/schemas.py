import json
from PIL import Image
from pydantic import BaseModel, field_validator

class SubTask(BaseModel):
    name: str # Name of the sub task
    instruction: str # Instruction that sub-agents must be obeyed


class ToolResult(BaseModel):
    tool_name: str
    tool_result: dict

    @field_validator('tool_result', mode='before')
    @classmethod
    def ensure_dict(cls, value: str) -> dict:
        if not isinstance(value, dict):
            return json.loads(value)

        raise TypeError("Expected str")

        
class ImageResult(BaseModel):
    tool_name: str
    img: Image.Image
