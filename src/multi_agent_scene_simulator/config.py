from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    LLM_API_KEY: str
    LLM_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_MAX_TOKENS: int = 32000
    DSPY_EXAMPLE_FP: str = "examples/scene_description.json"

    WEAK_MODEL: str = "openrouter/deepseek/deepseek-chat-v3.1"
    STRONG_MODEL: str = "openrouter/google/gemini-2.5-flash"
    BLENDER_MCP_CONFIG: dict = {
        "mcpServers": {
            "blender-mcp": {"command": "uvx", "args": ["blender-mcp"]}
        }
    }

settings = Settings()
