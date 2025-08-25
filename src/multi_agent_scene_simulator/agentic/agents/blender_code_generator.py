import re
import dspy

from ...config import settings

class BlenderPythonCode(dspy.Signature):
    """
    Generate robust Python code using Blender's Python API based on a given instruction. 
    The produced code will be executed via `send_command` to create, modify, or query 
    objects within Blender, the open-source 3D creation suite.
    
    CRITICAL: This code runs in MCP server environment with limited UI context. Follow these patterns:
    
    1. **Context Safety**: Always ensure proper context before bpy.ops operations:
       - Check current mode: `if bpy.context.mode != 'OBJECT':`
       - Use context overrides for viewport operations
       - Avoid operations that require active 3D viewport
    
    2. **Direct API Usage**: Prefer direct bpy.data access over bpy.ops:
       - Use `bpy.data.objects.new()` instead of `bpy.ops.object.add()`
       - Use `bpy.data.meshes.new()` and `bpy.data.materials.new()`
       - Manipulate objects directly: `obj.location = (x, y, z)`
    
    3. **Mode Management**: Handle mode switches safely:
       - Always check current mode before switching
       - Use try-except for mode changes
       - Return to Object Mode after edit operations
    
    4. **Object Selection**: Use robust selection methods:
       - Select objects by name: `bpy.data.objects['ObjectName'].select_set(True)`
       - Use `bpy.context.view_layer.objects.active = obj` to set active object
       - Avoid `bpy.ops.object.select_all()` - use explicit object selection
    
    5. **Context Override Pattern**:
       ```python
       for area in bpy.context.screen.areas:
           if area.type == 'VIEW_3D':
               override = bpy.context.copy()
               override['area'] = area
               bpy.ops.some_operation(override, ...)
               break
       ```
    
    6. **Mesh Operations**: Use BMesh safely:
       - Always ensure object is in edit mode before BMesh operations
       - Use `bmesh.from_edit_mesh()` only when in edit mode
       - Always call `bm.free()` to prevent memory leaks
    
    7. **Error Prevention**: 
       - Check if objects exist before operations
       - Use try-except blocks for context-sensitive operations
       - Validate object states before mode switches
    
    8. **Safe Cleanup**: 
       - Deselect all objects before selection operations
       - Clear temporary data structures
       - Reset view state after operations
    
    Example safe pattern for object creation:
    ```python
    # Safe object creation without bpy.ops
    mesh = bpy.data.meshes.new("MeshName")
    obj = bpy.data.objects.new("ObjectName", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (0, 0, 0)
    ```
    
    Example safe selection pattern:
    ```python
    # Safe object selection
    bpy.ops.object.select_all(action='DESELECT')  # May fail - use alternative:
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    target_obj = bpy.data.objects.get("ObjectName")
    if target_obj:
        target_obj.select_set(True)
        bpy.context.view_layer.objects.active = target_obj
    ```
    """
    instruction: str = dspy.InputField(
        desc="A detailed and unambiguous description of the desired Blender task or scene operation."
    )
    code: str = dspy.OutputField(
        desc="Valid Python code using Blender's bpy API that fulfills the given instruction with proper context handling."
    )

class BlenderCodeGenerator(dspy.Module):
    def __init__(self, model: str):
        self.model = model
        self.generator = dspy.Predict(BlenderPythonCode)

    def _sanitize_code(self, raw_code: str) -> str:
        """
        Sanitize the raw code by extracting Python code from markdown blocks.
        
        Handles:
        - ```python ... ``` blocks
        - ``` ... ``` blocks (without language specifier)
        - Plain code without markdown
        """
        if not raw_code:
            return ""
        
        # Handle triple backtick with language specifier
        pattern = r'```(?:python|py)?\s*\n(.*?)\n```'
        matches = re.findall(pattern, raw_code, re.DOTALL)
        if matches:
            return matches[0].strip()
        
        # Handle triple backtick without language specifier
        pattern = r'```\s*\n(.*?)\n```'
        matches = re.findall(pattern, raw_code, re.DOTALL)
        if matches:
            return matches[0].strip()
        
        # Handle single backticks
        pattern = r'`([^`]+)`'
        matches = re.findall(pattern, raw_code, re.DOTALL)
        if matches and len(matches) == 1:
            return matches[0].strip()
        
        # Return original if no markdown patterns matched
        return raw_code.strip()

    def forward(self, instruction: str):
        with dspy.context(lm=dspy.LM(self.model, api_base=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)):
            result = self.generator(instruction=instruction)
            assert hasattr(result, "code"), "The LLM response didnt response with `code attr`"

        raw_code = result.code
        sanitized_code = self._sanitize_code(raw_code)
        
        return {
            "code": sanitized_code,
            "raw_response": str(result)
        }
