"""AI provider configurations."""

AI_PROVIDERS = {
    "local": {
        "ollama": {
            "name": "Ollama",
            "type": "local",
            "default_model": "gemma3:4b",
            "base_url": "http://localhost:11434",
            "models": ["gemma3:4b", "llama3.2", "llama3.1", "mistral", "codellama"]
        },
        "lmstudio": {
            "name": "LM Studio",
            "type": "local",
            "default_model": "local-model",
            "base_url": "http://localhost:1234/v1",
            "models": []
        },
        "gpt4all": {
            "name": "GPT4All",
            "type": "local",
            "default_model": "mistral-7b-instruct",
            "base_url": "http://localhost:4891/v1",
            "models": []
        }
    },
    "cloud": {
        "openai": {
            "name": "OpenAI",
            "type": "cloud",
            "default_model": "gpt-4o",
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
        },
        "anthropic": {
            "name": "Anthropic",
            "type": "cloud",
            "default_model": "claude-sonnet-4-20250514",
            "models": ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022", "claude-opus-4-20250514"]
        },
        "google": {
            "name": "Google AI",
            "type": "cloud",
            "default_model": "gemini-1.5-pro",
            "models": ["gemini-1.5-pro", "gemini-1.5-flash"]
        }
    }
}

DEFAULT_PROVIDER = "ollama"
DEFAULT_PROVIDER_TYPE = "local"
