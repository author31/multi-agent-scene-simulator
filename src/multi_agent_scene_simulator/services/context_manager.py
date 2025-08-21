from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class LeadAgentResponse:
    sub_tasks: List[Any]
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
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class IterationContext:
    iteration: int
    lead_agent_response: Optional[LeadAgentResponse]
    code_generation_tasks: List[CodeGenerationTask]
    scene_evaluation: Optional[SceneEvaluation]
    tool_results: List[ToolResult]
    timestamp: datetime


class ContextManager:
    def __init__(self):
        self.initial_requirement: str = ""
        self.iterations: List[IterationContext] = []
        self.current_iteration: Optional[IterationContext] = None
        self.final_result: Optional[Dict[str, Any]] = None
        
    def set_initial_requirement(self, requirement: str):
        self.initial_requirement = requirement
        
    def start_iteration(self, iteration: int):
        self.current_iteration = IterationContext(
            iteration=iteration,
            lead_agent_response=None,
            code_generation_tasks=[],
            scene_evaluation=None,
            tool_results=[],
            timestamp=datetime.now()
        )
        
    def store_lead_response(self, sub_tasks: List[Any], raw_response: str):
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
            
    def store_tool_result(self, tool_name: str, result: Any, metadata: Dict[str, Any] = None):
        if self.current_iteration:
            tool_result = ToolResult(
                tool_name=tool_name,
                result=result,
                metadata=metadata or {},
                timestamp=datetime.now()
            )
            self.current_iteration.tool_results.append(tool_result)
            
    def complete_iteration(self):
        if self.current_iteration:
            self.iterations.append(self.current_iteration)
            self.current_iteration = None
            
    def set_final_result(self, result: Dict[str, Any]):
        self.final_result = result
        
    def get_context_for_llm(self) -> str:
        """Generate context string for LLM consumption"""
        context_parts = []
        
        context_parts.append(f"Initial Requirement: {self.initial_requirement}")
        
        for iteration in self.iterations:
            context_parts.append(f"\nIteration {iteration.iteration}:")
            
            if iteration.lead_agent_response:
                context_parts.append(f"Lead Agent Tasks: {len(iteration.lead_agent_response.sub_tasks)} tasks generated")
                
            if iteration.code_generation_tasks:
                context_parts.append(f"Code Generated: {len(iteration.code_generation_tasks)} tasks")
                
            if iteration.scene_evaluation:
                context_parts.append(f"Evaluation Score: {iteration.scene_evaluation.match_score}")
                context_parts.append(f"Suggestion: {iteration.scene_evaluation.suggestion}")
                
        return "\n".join(context_parts)
        
    def get_full_context(self) -> Dict[str, Any]:
        """Get complete context for debugging/analysis"""
        return {
            "initial_requirement": self.initial_requirement,
            "iterations": [
                {
                    "iteration": iter_ctx.iteration,
                    "timestamp": iter_ctx.timestamp.isoformat(),
                    "lead_agent_response": asdict(iter_ctx.lead_agent_response) if iter_ctx.lead_agent_response else None,
                    "code_generation_tasks": [asdict(task) for task in iter_ctx.code_generation_tasks],
                    "scene_evaluation": asdict(iter_ctx.scene_evaluation) if iter_ctx.scene_evaluation else None,
                    "tool_results": [asdict(tool) for tool in iter_ctx.tool_results]
                }
                for iter_ctx in self.iterations
            ],
            "final_result": self.final_result
        }
        
    def save_to_file(self, filepath: str):
        """Save context to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.get_full_context(), f, indent=2, default=str)
            
    def load_from_file(self, filepath: str):
        """Load context from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        self.initial_requirement = data.get("initial_requirement", "")
        self.final_result = data.get("final_result")
        
        # Reconstruct iterations
        self.iterations = []
        for iter_data in data.get("iterations", []):
            iteration = IterationContext(
                iteration=iter_data["iteration"],
                lead_agent_response=None,
                code_generation_tasks=[],
                scene_evaluation=None,
                tool_results=[],
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
                    raw_response=eval_data["raw_response"],
                    timestamp=datetime.fromisoformat(eval_data["timestamp"])
                )
                
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
