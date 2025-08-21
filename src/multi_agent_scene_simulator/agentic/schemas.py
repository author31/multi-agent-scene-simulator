import base64
import json
from io import BytesIO

from PIL import Image
from pydantic import BaseModel, field_validator


class SubTask(BaseModel):
    name: str # Name of the sub task
    instruction: str # Instruction that sub-agents must be obeyed


class ToolResult(BaseModel):
    tool_name: str
    tool_result: dict | str

    @field_validator('tool_result', mode='before')
    @classmethod
    def normalize_tool_result(cls, value):
        # If already a dict, return as-is
        if isinstance(value, dict):
            return value

        # If it's a string, try to parse as JSON
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
                return value  # leave as string if parsed value is not a dict
            except json.JSONDecodeError:
                return value  # leave as string if invalid JSON

        # For other unexpected types
        raise TypeError(f"Invalid type for tool_result: {type(value)}")
        
class ImageResult(BaseModel):
    tool_name: str
    image_data: str

    def get_image(self) -> Image.Image:
        decoded_bytes = base64.b64decode(self.image_data)
        return Image.open(BytesIO(decoded_bytes))
