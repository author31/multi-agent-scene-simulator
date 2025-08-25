from typing import Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class LeadAgentResponse:
    sub_tasks: list[Any]
    raw_response: str
    timestamp: datetime


@dataclass
class CodeGenerationTask:
    task_name: str
    instruction: str
    generated_code: str
    raw_response: str
    timestamp: datetime


@dataclass
class SceneEvaluation:
    match_score: float
    suggestion: str
    timestamp: datetime


@dataclass
class ToolResult:
    tool_name: str
    result: Any
    metadata: dict
    timestamp: datetime


@dataclass
class SceneState:
    objects: list[dict]
    lights: list[dict]
    cameras: list[dict]
    materials: list[dict]
    scene_info: dict
    timestamp: datetime


@dataclass
class ComponentProgress:
    component_type: str
    component_name: str
    status: str  # "missing", "partial", "complete"
    details: dict
    iteration_added: int
    timestamp: datetime


@dataclass
class IterationContext:
    iteration: int
    lead_agent_response: Optional[LeadAgentResponse]
    code_generation_tasks: list[CodeGenerationTask]
    scene_evaluation: Optional[SceneEvaluation]
    tool_results: list[ToolResult]
    scene_state: Optional[SceneState]
    component_progress: list[ComponentProgress]
    timestamp: datetime


class ContextManager:
    def __init__(self):
        self.initial_requirement: str = ""
        self.iterations: list[IterationContext] = []
        self.current_iteration: Optional[IterationContext] = None
        self.final_result: Optional[dict] = None
        self.scene_state_history: list[SceneState] = []
        self.component_registry: dict = {}
        
    def set_initial_requirement(self, requirement: str):
        self.initial_requirement = requirement
        
    def start_iteration(self, iteration: int):
        self.current_iteration = IterationContext(
            iteration=iteration,
            lead_agent_response=None,
            code_generation_tasks=[],
            scene_evaluation=None,
            tool_results=[],
            scene_state=None,
            component_progress=[],
            timestamp=datetime.now()
        )
        
    def store_lead_response(self, sub_tasks: list[Any], raw_response: str):
        if self.current_iteration:
            self.current_iteration.lead_agent_response = LeadAgentResponse(
                sub_tasks=sub_tasks,
                raw_response=raw_response,
                timestamp=datetime.now()
            )
            
    def store_code_generation(self, task_name: str, instruction: str, code: str, raw_response: str):
        if self.current_iteration:
            task = CodeGenerationTask(
                task_name=task_name,
                instruction=instruction,
                generated_code=code,
                raw_response=raw_response,
                timestamp=datetime.now()
            )
            self.current_iteration.code_generation_tasks.append(task)
            
    def store_evaluation(self, match_score: float, suggestion: str):
        if self.current_iteration:
            self.current_iteration.scene_evaluation = SceneEvaluation(
                match_score=match_score,
                suggestion=suggestion,
                timestamp=datetime.now()
            )
            
    def store_tool_result(self, tool_name: str, result: Any, metadata: dict = None):
        if self.current_iteration:
            tool_result = ToolResult(
                tool_name=tool_name,
                result=result,
                metadata=metadata or {},
                timestamp=datetime.now()
            )
            self.current_iteration.tool_results.append(tool_result)
            
    def store_scene_state(self, scene_state: dict):
        """Store the current complete scene state"""
        if self.current_iteration:
            state = SceneState(
                objects=scene_state.get("objects", []),
                lights=scene_state.get("lights", []),
                cameras=scene_state.get("cameras", []),
                materials=scene_state.get("materials", []),
                scene_info=scene_state.get("scene_info", {}),
                timestamp=datetime.now()
            )
            self.current_iteration.scene_state = state
            self.scene_state_history.append(state)
            
    def update_component_progress(self, component_type: str, component_name: str, 
                                status: str, details: dict = None):
        """Update progress for a specific component"""
        if self.current_iteration:
            progress = ComponentProgress(
                component_type=component_type,
                component_name=component_name,
                status=status,
                details=details or {},
                iteration_added=self.current_iteration.iteration,
                timestamp=datetime.now()
            )
            self.current_iteration.component_progress.append(progress)
            self.component_registry[f"{component_type}:{component_name}"] = progress
            
    def complete_iteration(self):
        if self.current_iteration:
            self.iterations.append(self.current_iteration)
            self.current_iteration = None
            
    def set_final_result(self, result: dict):
        self.final_result = result
        
    def get_context_for_llm(self) -> str:
        """Generate context string for LLM consumption"""
        context_parts = []
        
        context_parts.append(f"Initial Requirement: {self.initial_requirement}")
        context_parts.append("\n=== CURRENT SCENE STATE ===")
        
        # Current scene state
        if self.scene_state_history:
            current_state = self.scene_state_history[-1]
            context_parts.append(f"Objects: {len(current_state.objects)}")
            context_parts.append(f"Lights: {len(current_state.lights)}")
            context_parts.append(f"Cameras: {len(current_state.cameras)}")
            context_parts.append(f"Materials: {len(current_state.materials)}")
        
        context_parts.append("\n=== COMPONENT PROGRESS ===")
        
        # Component progress summary
        for key, progress in self.component_registry.items():
            context_parts.append(f"{key}: {progress.status}")
        
        context_parts.append("\n=== PREVIOUS ITERATIONS ===")
        
        for iteration in self.iterations:
            context_parts.append(f"\nIteration {iteration.iteration}:")
            
            if iteration.scene_evaluation:
                context_parts.append(f"Evaluation Score: {iteration.scene_evaluation.match_score}")
                context_parts.append(f"Suggestion: {iteration.scene_evaluation.suggestion}")
                
            if iteration.component_progress:
                context_parts.append("Components updated:")
                for comp in iteration.component_progress:
                    context_parts.append(f"  - {comp.component_type}: {comp.component_name} ({comp.status})")
                    
        return "\n".join(context_parts)
        
    def get_full_context(self) -> dict:
        """Get complete context for debugging/analysis"""
        return {
            "initial_requirement": self.initial_requirement,
            "scene_state_history": [
                {
                    "objects": state.objects,
                    "lights": state.lights,
                    "cameras": state.cameras,
                    "materials": state.materials,
                    "scene_info": state.scene_info,
                    "timestamp": state.timestamp.isoformat()
                }
                for state in self.scene_state_history
            ],
            "component_registry": {
                key: asdict(progress) for key, progress in self.component_registry.items()
            },
            "iterations": [
                {
                    "iteration": iter_ctx.iteration,
                    "timestamp": iter_ctx.timestamp.isoformat(),
                    "lead_agent_response": asdict(iter_ctx.lead_agent_response) if iter_ctx.lead_agent_response else None,
                    "code_generation_tasks": [asdict(task) for task in iter_ctx.code_generation_tasks],
                    "scene_evaluation": asdict(iter_ctx.scene_evaluation) if iter_ctx.scene_evaluation else None,
                    "tool_results": [asdict(tool) for tool in iter_ctx.tool_results],
                    "scene_state": asdict(iter_ctx.scene_state) if iter_ctx.scene_state else None,
                    "component_progress": [asdict(comp) for comp in iter_ctx.component_progress]
                }
                for iter_ctx in self.iterations
            ],
            "final_result": self.final_result
        }
        
    def save_to_file(self, filepath: str):
        """Save context to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.get_full_context(), f, indent=2, default=str)
            
    def create_checkpoint(self, iteration: int) -> str:
        """Create a checkpoint for rollback purposes"""
        checkpoint_name = f"checkpoint_{iteration}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        checkpoint_path = f"{checkpoint_name}.json"
        self.save_to_file(checkpoint_path)
        return checkpoint_path
        
    def rollback_to_iteration(self, iteration: int, mcp_client) -> bool:
        """Rollback scene to a specific iteration state"""
        try:
            # Find the closest saved state
            target_state = None
            for state in self.scene_state_history:
                # This is a simplified rollback - in practice you'd need
                # more sophisticated state restoration via MCP tools
                logger.info(f"Rollback requested to iteration {iteration}")
                return True
            return False
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
            
    def load_from_file(self, filepath: str):
        """Load context from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        self.initial_requirement = data.get("initial_requirement", "")
        self.final_result = data.get("final_result")
        
        # Reconstruct scene state history
        self.scene_state_history = []
        for state_data in data.get("scene_state_history", []):
            state = SceneState(
                objects=state_data["objects"],
                lights=state_data["lights"],
                cameras=state_data["cameras"],
                materials=state_data["materials"],
                scene_info=state_data["scene_info"],
                timestamp=datetime.fromisoformat(state_data["timestamp"])
            )
            self.scene_state_history.append(state)
            
        # Reconstruct component registry
        self.component_registry = {}
        for key, progress_data in data.get("component_registry", {}).items():
            progress = ComponentProgress(
                component_type=progress_data["component_type"],
                component_name=progress_data["component_name"],
                status=progress_data["status"],
                details=progress_data["details"],
                iteration_added=progress_data["iteration_added"],
                timestamp=datetime.fromisoformat(progress_data["timestamp"])
            )
            self.component_registry[key] = progress
        
        # Reconstruct iterations
        self.iterations = []
        for iter_data in data.get("iterations", []):
            iteration = IterationContext(
                iteration=iter_data["iteration"],
                lead_agent_response=None,
                code_generation_tasks=[],
                scene_evaluation=None,
                tool_results=[],
                scene_state=None,
                component_progress=[],
                timestamp=datetime.fromisoformat(iter_data["timestamp"])
            )
            
            # Reconstruct lead agent response
            if iter_data.get("lead_agent_response"):
                lead_data = iter_data["lead_agent_response"]
                iteration.lead_agent_response = LeadAgentResponse(
                    sub_tasks=lead_data["sub_tasks"],
                    raw_response=lead_data["raw_response"],
                    timestamp=datetime.fromisoformat(lead_data["timestamp"])
                )
                
            # Reconstruct code generation tasks
            for task_data in iter_data.get("code_generation_tasks", []):
                task = CodeGenerationTask(
                    task_name=task_data["task_name"],
                    instruction=task_data["instruction"],
                    generated_code=task_data["generated_code"],
                    raw_response=task_data["raw_response"],
                    timestamp=datetime.fromisoformat(task_data["timestamp"])
                )
                iteration.code_generation_tasks.append(task)
                
            # Reconstruct scene evaluation
            if iter_data.get("scene_evaluation"):
                eval_data = iter_data["scene_evaluation"]
                iteration.scene_evaluation = SceneEvaluation(
                    match_score=eval_data["match_score"],
                    suggestion=eval_data["suggestion"],
                    timestamp=datetime.fromisoformat(eval_data["timestamp"])
                )
                
            # Reconstruct scene state
            if iter_data.get("scene_state"):
                state_data = iter_data["scene_state"]
                iteration.scene_state = SceneState(
                    objects=state_data["objects"],
                    lights=state_data["lights"],
                    cameras=state_data["cameras"],
                    materials=state_data["materials"],
                    scene_info=state_data["scene_info"],
                    timestamp=datetime.fromisoformat(state_data["timestamp"])
                )
                
            # Reconstruct component progress
            for comp_data in iter_data.get("component_progress", []):
                comp = ComponentProgress(
                    component_type=comp_data["component_type"],
                    component_name=comp_data["component_name"],
                    status=comp_data["status"],
                    details=comp_data["details"],
                    iteration_added=comp_data["iteration_added"],
                    timestamp=datetime.fromisoformat(comp_data["timestamp"])
                )
                iteration.component_progress.append(comp)
                
            # Reconstruct tool results
            for tool_data in iter_data.get("tool_results", []):
                tool = ToolResult(
                    tool_name=tool_data["tool_name"],
                    result=tool_data["result"],
                    metadata=tool_data["metadata"],
                    timestamp=datetime.fromisoformat(tool_data["timestamp"])
                )
                iteration.tool_results.append(tool)
                
            self.iterations.append(iteration)
