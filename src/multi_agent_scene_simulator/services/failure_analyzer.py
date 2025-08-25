"""
Failure analysis system for diagnosing and recovering from task execution failures.

Provides root cause analysis and intelligent recovery strategies for failed
Blender operations.
"""

import re
import traceback
from dataclasses import dataclass


@dataclass
class FailureAnalysis:
    """Comprehensive failure analysis report."""
    failure_type: str
    root_cause: str
    specific_issue: str
    scene_impact: dict[str, object]
    suggested_fix: str
    alternative_approaches: list[str]
    recovery_complexity: int  # 1-5 scale
    likely_success_rate: float  # 0-1 probability
    prevention_strategy: str


@dataclass
class TaskContext:
    """Context information about a failed task."""
    task_name: str
    instruction: str
    generated_code: str
    error_message: str
    error_type: str
    stack_trace: str
    scene_state_before: dict[str, object]
    scene_state_after: dict[str, object]
    attempt_number: int
    previous_failures: list[str]


class FailureAnalyzer:
    """Intelligent failure analysis and recovery system."""
    
    def __init__(self):
        self.failure_patterns = self._build_failure_patterns()
        self.recovery_strategies = self._build_recovery_strategies()
    
    def analyze_task_failure(self, task_context: TaskContext) -> FailureAnalysis:
        """
        Perform comprehensive failure analysis for a task.
        
        Args:
            task_context: Context information about the failed task
            
        Returns:
            Detailed failure analysis with recovery recommendations
        """
        
        # Identify failure type
        failure_type = self._identify_failure_type(task_context)
        
        # Determine root cause
        root_cause = self._determine_root_cause(task_context, failure_type)
        
        # Analyze specific issue
        specific_issue = self._analyze_specific_issue(task_context, root_cause)
        
        # Assess scene impact
        scene_impact = self._assess_scene_impact(task_context, specific_issue)
        
        # Generate recovery plan
        suggested_fix = self._generate_suggested_fix(task_context, root_cause, specific_issue)
        
        # Provide alternative approaches
        alternative_approaches = self._get_alternative_approaches(task_context, root_cause)
        
        # Calculate recovery metrics
        recovery_complexity = self._calculate_recovery_complexity(task_context, root_cause)
        likely_success_rate = self._estimate_success_probability(task_context, suggested_fix)
        prevention_strategy = self._generate_prevention_strategy(task_context, root_cause)
        
        return FailureAnalysis(
            failure_type=failure_type,
            root_cause=root_cause,
            specific_issue=specific_issue,
            scene_impact=scene_impact,
            suggested_fix=suggested_fix,
            alternative_approaches=alternative_approaches,
            recovery_complexity=recovery_complexity,
            likely_success_rate=likely_success_rate,
            prevention_strategy=prevention_strategy
        )
    
    def _build_failure_patterns(self) -> dict[str, list[str]]:
        """Build comprehensive failure pattern database."""
        return {
            "context_error": [
                "context is incorrect",
                "poll() failed",
                "context error",
                "invalid context",
                "not in object mode"
            ],
            "geometry_error": [
                "mesh operation failed",
                "vertex group",
                "face index",
                "edge loop",
                "geometry error"
            ],
            "material_error": [
                "material not found",
                "texture missing",
                "shader error",
                "material slot"
            ],
            "object_error": [
                "object not found",
                "object does not exist",
                "no active object",
                "object selection"
            ],
            "constraint_error": [
                "constraint failed",
                "parenting error",
                "transform constraint"
            ],
            "render_error": [
                "render engine",
                "cycles error",
                "eevee error",
                "render settings"
            ],
            "memory_error": [
                "memory",
                "out of memory",
                "allocation failed"
            ],
            "syntax_error": [
                "syntax error",
                "indentation error",
                "name error",
                "attribute error"
            ],
            "runtime_error": [
                "runtime error",
                "value error",
                "type error",
                "index error"
            ]
        }
    
    def _build_recovery_strategies(self) -> dict[str, dict[str, object]]:
        """Build comprehensive recovery strategy database."""
        return {
            "context_error": {
                "immediate_fix": "Ensure proper context mode before operations",
                "code_pattern": """
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
                """,
                "alternatives": [
                    "Use context override for viewport operations",
                    "Switch to direct bpy.data manipulation",
                    "Add explicit object selection before operations"
                ],
                "prevention": "Always check context state before bpy.ops operations"
            },
            "geometry_error": {
                "immediate_fix": "Validate geometry before operations",
                "code_pattern": """
import bmesh
bm = bmesh.new()
bm.from_mesh(obj.data)
bm.validate()
                """,
                "alternatives": [
                    "Use bmesh validation before operations",
                    "Check for manifold geometry",
                    "Validate vertex/face indices"
                ],
                "prevention": "Validate mesh integrity before geometric operations"
            },
            "material_error": {
                "immediate_fix": "Ensure material exists before assignment",
                "code_pattern": """
material = bpy.data.materials.get('MaterialName')
if not material:
    material = bpy.data.materials.new(name='MaterialName')
                """,
                "alternatives": [
                    "Create default material if not found",
                    "Use material slot validation",
                    "Check material library availability"
                ],
                "prevention": "Always verify material existence before assignment"
            },
            "object_error": {
                "immediate_fix": "Use safe object access patterns",
                "code_pattern": """
obj = bpy.data.objects.get('ObjectName')
if obj:
    # Safe to use object
else:
    # Create or find alternative
                """,
                "alternatives": [
                    "Use bpy.data.objects.get() instead of direct access",
                    "Create object if not exists",
                    "Use object naming conventions"
                ],
                "prevention": "Always use safe object access patterns"
            },
            "constraint_error": {
                "immediate_fix": "Validate constraint setup",
                "code_pattern": """
if obj.parent:
    obj.parent = None
# Apply transforms before constraints
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                """,
                "alternatives": [
                    "Clear constraints before operations",
                    "Apply transforms before constraints",
                    "Use transform matrices instead"
                ],
                "prevention": "Apply transforms before applying constraints"
            }
        }
    
    def _identify_failure_type(self, task_context: TaskContext) -> str:
        """Identify the type of failure based on error message and context."""
        error_msg = task_context.error_message.lower()
        
        for failure_type, patterns in self.failure_patterns.items():
            for pattern in patterns:
                if pattern.lower() in error_msg:
                    return failure_type
        
        # Additional heuristics
        if "bpy.ops" in task_context.generated_code and "poll" in error_msg:
            return "context_error"
        elif "mesh" in task_context.generated_code and ("index" in error_msg or "vertex" in error_msg):
            return "geometry_error"
        elif "material" in task_context.generated_code:
            return "material_error"
        elif "object" in task_context.generated_code and "not found" in error_msg:
            return "object_error"
        
        return "unknown_error"
    
    def _determine_root_cause(self, task_context: TaskContext, failure_type: str) -> str:
        """Determine the root cause of the failure."""
        error_msg = task_context.error_message
        
        if failure_type == "context_error":
            if "object.mode" in error_msg:
                return "incorrect_object_mode"
            elif "poll" in error_msg:
                return "invalid_context_for_operation"
            else:
                return "context_validation_failure"
        
        elif failure_type == "geometry_error":
            if "index" in error_msg:
                return "invalid_geometry_index"
            elif "vertex" in error_msg and "group" in error_msg:
                return "missing_vertex_group"
            else:
                return "geometry_validation_failure"
        
        elif failure_type == "material_error":
            if "not found" in error_msg:
                return "missing_material"
            else:
                return "material_assignment_failure"
        
        elif failure_type == "object_error":
            if "not found" in error_msg:
                return "object_does_not_exist"
            else:
                return "object_access_failure"
        
        return "unknown_root_cause"
    
    def _analyze_specific_issue(self, task_context: TaskContext, root_cause: str) -> str:
        """Analyze the specific technical issue causing the failure."""
        
        # Extract specific error context
        lines = task_context.error_message.split('\n')
        specific_line = ""
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ["error", "exception", "failed"]):
                specific_line = line.strip()
                break
        
        # Create detailed issue description
        issue_map = {
            "incorrect_object_mode": f"Operation requires Object Mode, current mode prevents execution",
            "invalid_context_for_operation": f"Context validation failed for bpy.ops operation: {specific_line}",
            "missing_material": f"Material '{self._extract_material_name(task_context.generated_code)}' not found",
            "object_does_not_exist": f"Object '{self._extract_object_name(task_context.generated_code)}' does not exist",
            "invalid_geometry_index": f"Geometry index out of range: {specific_line}",
            "geometry_validation_failure": f"Mesh geometry validation failed: {specific_line}"
        }
        
        return issue_map.get(root_cause, f"Unknown specific issue: {specific_line}")
    
    def _assess_scene_impact(self, task_context: TaskContext, specific_issue: str) -> dict[str, object]:
        """Assess how the failure impacts the scene state."""
        impact = {
            "objects_affected": [],
            "scene_integrity": "intact",
            "user_requirement_impact": "minimal",
            "recovery_difficulty": "low"
        }
        
        # Analyze based on task name and instruction
        task_name = task_context.task_name.lower()
        instruction = task_context.instruction.lower()
        
        # Determine objects affected
        if "light" in task_name or "lighting" in instruction:
            impact["objects_affected"] = ["lighting_system"]
            impact["scene_integrity"] = "partial"
            impact["user_requirement_impact"] = "moderate"
            impact["recovery_difficulty"] = "low"
        
        elif "material" in task_name or "texture" in instruction:
            impact["objects_affected"] = ["material_system"]
            impact["scene_integrity"] = "partial"
            impact["user_requirement_impact"] = "high"
            impact["recovery_difficulty"] = "medium"
        
        elif "object" in task_name or "create" in instruction:
            impact["objects_affected"] = ["object_creation"]
            impact["scene_integrity"] = "partial"
            impact["user_requirement_impact"] = "high"
            impact["recovery_difficulty"] = "medium"
        
        elif "geometry" in task_name or "mesh" in instruction:
            impact["objects_affected"] = ["geometry_system"]
            impact["scene_integrity"] = "at_risk"
            impact["user_requirement_impact"] = "high"
            impact["recovery_difficulty"] = "high"
        
        return impact
    
    def _generate_suggested_fix(self, task_context: TaskContext, root_cause: str, specific_issue: str) -> str:
        """Generate a specific fix for the identified problem."""
        
        strategy = self.recovery_strategies.get(root_cause, {})
        immediate_fix = strategy.get("immediate_fix", "Retry with error handling")
        
        # Generate contextual fix code
        if root_cause == "incorrect_object_mode":
            return """
# Ensure correct object mode
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# Safe object operation
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = target_object
target_object.select_set(True)
            """.strip()
        
        elif root_cause == "missing_material":
            material_name = self._extract_material_name(task_context.generated_code)
            return f"""
# Ensure material exists
material = bpy.data.materials.get('{material_name}')
if not material:
    material = bpy.data.materials.new(name='{material_name}')
    material.use_nodes = True
    
# Safe material assignment
if target_object.data.materials:
    target_object.data.materials[0] = material
else:
    target_object.data.materials.append(material)
            """.strip()
        
        elif root_cause == "object_does_not_exist":
            object_name = self._extract_object_name(task_context.generated_code)
            return f"""
# Safe object access
obj = bpy.data.objects.get('{object_name}')
if not obj:
    # Create basic object or find alternative
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.name = '{object_name}'
            """.strip()
        
        return f"""
# General error recovery
try:
    {task_context.generated_code}
except Exception as e:
    print(f"Error during operation: {{e}}")
    # Fallback operation
    print("Applying fallback strategy...")
        """.strip()
    
    def _get_alternative_approaches(self, task_context: TaskContext, root_cause: str) -> list[str]:
        """Provide alternative approaches for task completion."""
        
        strategy = self.recovery_strategies.get(root_cause, {})
        alternatives = strategy.get("alternatives", [])
        
        # Add context-specific alternatives
        task_name = task_context.task_name.lower()
        
        if "create" in task_name:
            alternatives.extend([
                "Use procedural generation instead of asset loading",
                "Create simplified version of the object",
                "Use primitive shapes as placeholders"
            ])
        
        elif "light" in task_name:
            alternatives.extend([
                "Use environment lighting instead of specific lights",
                "Create area lights instead of point lights",
                "Adjust world lighting instead"
            ])
        
        elif "material" in task_name:
            alternatives.extend([
                "Use procedural materials instead of texture-based",
                "Apply basic color materials as fallback",
                "Create materials programmatically"
            ])
        
        return alternatives[:3]  # Limit to 3 alternatives
    
    def _calculate_recovery_complexity(self, task_context: TaskContext, root_cause: str) -> int:
        """Calculate complexity score for recovery (1-5 scale)."""
        
        base_complexity = {
            "context_error": 2,
            "geometry_error": 4,
            "material_error": 2,
            "object_error": 3,
            "constraint_error": 3,
            "render_error": 4,
            "memory_error": 5,
            "syntax_error": 1,
            "runtime_error": 2,
            "unknown_error": 3
        }
        
        complexity = base_complexity.get(root_cause, 3)
        
        # Adjust based on attempt number
        complexity += min(task_context.attempt_number - 1, 2)
        
        return min(complexity, 5)
    
    def _estimate_success_probability(self, task_context: TaskContext, suggested_fix: str) -> float:
        """Estimate probability of successful recovery."""
        
        base_prob = 0.8  # Base success rate
        
        # Reduce probability with each failure
        failure_penalty = (task_context.attempt_number - 1) * 0.15
        
        # Increase probability for simple fixes
        if "try" in suggested_fix.lower() or "fallback" in suggested_fix.lower():
            base_prob += 0.1
        
        # Decrease for complex operations
        if any(keyword in suggested_fix.lower() 
               for keyword in ["bmesh", "complex", "multiple"]):
            base_prob -= 0.1
        
        return max(0.3, min(0.95, base_prob - failure_penalty))
    
    def _generate_prevention_strategy(self, task_context: TaskContext, root_cause: str) -> str:
        """Generate strategy to prevent similar failures."""
        
        strategy = self.recovery_strategies.get(root_cause, {})
        prevention = strategy.get("prevention", "Add comprehensive error handling")
        
        # Add context-specific prevention
        task_name = task_context.task_name.lower()
        
        if "create" in task_name:
            return "Validate object existence before creation operations"
        elif "light" in task_name:
            return "Check lighting setup before illumination operations"
        elif "material" in task_name:
            return "Verify material availability before assignment"
        elif "geometry" in task_name:
            return "Validate mesh integrity before geometric operations"
        
        return prevention
    
    def _extract_material_name(self, code: str) -> str:
        """Extract material name from code."""
        # Look for material names in quotes
        matches = re.findall(r"['\"]([^'\"]*Material[^'\"]*)['\"]", code, re.IGNORECASE)
        if matches:
            return matches[0]
        
        # Look for variable names containing 'material'
        matches = re.findall(r'(\w*material\w*)', code, re.IGNORECASE)
        if matches:
            return matches[0]
        
        return "DefaultMaterial"
    
    def _extract_object_name(self, code: str) -> str:
        """Extract object name from code."""
        # Look for object names in quotes
        matches = re.findall(r"['\"]([^'\"]*object[^'\"]*)['\"]", code, re.IGNORECASE)
        if matches:
            return matches[0]
        
        # Look for variable names containing 'obj'
        matches = re.findall(r'(\w*obj\w*)', code, re.IGNORECASE)
        if matches:
            return matches[0]
        
        return "DefaultObject"
    
    def get_failure_summary(self, failures: list[TaskContext]) -> dict[str, object]:
        """Generate summary of multiple failures for pattern analysis."""
        if not failures:
            return {"patterns": [], "recommendations": []}
        
        failure_types = {}
        root_causes = {}
        
        for failure in failures:
            analysis = self.analyze_task_failure(failure)
            failure_types[analysis.failure_type] = failure_types.get(analysis.failure_type, 0) + 1
            root_causes[analysis.root_cause] = root_causes.get(analysis.root_cause, 0) + 1
        
        return {
            "most_common_type": max(failure_types.items(), key=lambda x: x[1])[0] if failure_types else "none",
            "most_common_cause": max(root_causes.items(), key=lambda x: x[1])[0] if root_causes else "none",
            "failure_count": len(failures),
            "patterns": list(failure_types.keys()),
            "recommendations": ["Focus on common failure types", "Implement preventive measures"]
        }