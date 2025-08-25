# Multi-agent-scene-simulator repo

Inspired by the blog post *“How We Built Our Multi-Agent Research System”*, this project explores a similar agentic architecture.
A **lead agent** breaks down user requirements into sub-tasks, while **search sub-agents** work on these sub-tasks.
In this design, each sub-agent is constrained to operate within its specific task scope.
In Anthropic’s multi-agent research, for example, sub-agents are only capable of browsing the internet.

I decided to apply this design to a different domain: **Blender scene generation**.

**Tech stack involved**:

* **blender-mcp** – Enables communication between agents and Blender
* **dspy** – Helps systematically optimize agents

---

## Design

1. **Lead Agent** (`lead_agent.py`): Decomposes scene requirements into sub-tasks
2. **Blender Code Generator** (`blender_code_generator.py`): Converts natural language instructions into Python code
3. **Scene Evaluator** (`scene_evaluator.py`): Assesses scene quality and identifies missing components

---

## Lead agent prompt optimization process

* **Scene description sources:** Crawled from [blenderkit.com](https://blenderkit.com)
* **LLM as a judge:** Uses LLMs capable of image recognition to return a **prompt-image match score** (range: `0` = not a match, `1` = perfect match).

---

## Issue

DSPy’s optimizers currently work only on a **single module**.
However, in a multi-agent setup, this approach is hard to adapt because our primary goal is to optimize only the **lead agent**, whose responsibility is breaking down scene requirements into sub-tasks.
The code generator sub-agents, on the other hand, simply act as “soldiers,” executing the task of generating code without requiring optimization.
