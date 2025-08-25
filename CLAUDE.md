# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Multi-agent scene simulator that uses LLMs and MCP (Model Context Protocol) to generate Blender scenes through iterative refinement. The system decomposes high-level scene requirements into executable tasks using a hierarchical agent architecture.

## Architecture

### Core Components

- **Agentic Framework**: Uses DSPy for LLM orchestration with specialized agents
- **MCP Client**: Communicates with Blender via `blender-mcp` server
- **Context Management**: Tracks scene state, component progress, and execution history
- **Iterative Refinement**: Builds scenes incrementally through multiple iterations

### Agent Hierarchy

1. **Lead Agent** (`lead_agent.py`): Decomposes scene requirements into sub-tasks
2. **Blender Code Generator** (`blender_code_generator.py`): Converts natural language instructions to Python code
3. **Scene Evaluator** (`scene_evaluator.py`): Assesses scene quality and identifies missing components

### Key Workflows

```
Scene Requirement → Lead Agent → Sub-tasks → Code Generation → Blender Execution → Evaluation → Next Iteration
```

## Development Commands

### Setup
```bash
# Install dependencies
uv sync

# Set environment variables
cp .env.example .env  # Then edit with your API keys
```

### Running
```bash
# Run the simulator
uv run multi-agent-scene-simulator run "create a modern kitchen with stainless steel appliances"

# Or use direct Python
python -m multi_agent_scene_simulator.cli run "your scene requirement"
```

### Environment Variables

Required in `.env`:
- `LLM_API_KEY`: OpenRouter API key
- `LLM_BASE_URL`: Defaults to `https://openrouter.ai/api/v1`
- `LLM_MAX_TOKENS`: Defaults to 32000

### Models

- **Strong Model**: `openrouter/google/gemini-2.5-flash` (for planning/evaluation)
- **Weak Model**: `openrouter/deepseek/deepseek-chat-v3.1` (for code generation)

## Key Files

- `src/multi_agent_scene_simulator/cli.py`: Entry point with Click CLI
- `src/multi_agent_scene_simulator/services/executor.py`: Main execution loop
- `src/multi_agent_scene_simulator/services/context_manager.py`: State management
- `src/multi_agent_scene_simulator/agentic/mcp_client.py`: Blender communication
- `src/multi_agent_scene_simulator/agentic/agents/`: Agent implementations

## Debugging

- **Context Logs**: Saved to `execution_context.json` after each run
- **Checkpoints**: Created as `checkpoint_{iteration}_{timestamp}.json`
- **Scene State**: Tracked through `ContextManager` with full history

## MCP Tools

The system uses these Blender MCP tools:
- `get_scene_info`: Returns current scene metadata
- `get_viewport_screenshot`: Captures current viewport
- `execute_blender_code`: Runs Python code in Blender
- `get_polyhaven_categories`, `search_polyhaven_assets`, `download_polyhaven_asset`: Asset management