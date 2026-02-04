"""AI provider management and communication."""

import asyncio
import json
from typing import AsyncGenerator, Optional
import aiohttp

from config.ai_providers import AI_PROVIDERS
from prompts.system_prompts import MAIN_SYSTEM_PROMPT, CONSULTATION_TYPES


class AIManager:
    """Manage AI provider connections and message generation."""

    def __init__(self):
        self.provider_type = "local"  # local or cloud
        self.provider = "ollama"
        self.model = "gemma3:4b"
        self.api_key = None
        self.base_url = "http://localhost:11434"
        self.conversation_history = []
        self.consultation_type = "custom"

    def configure(self, provider_type: str, provider: str, model: str = None,
                  api_key: str = None, base_url: str = None):
        """Configure the AI provider."""
        self.provider_type = provider_type
        self.provider = provider

        if provider_type == "local":
            config = AI_PROVIDERS["local"].get(provider, {})
            self.model = model or config.get("default_model", "llama3.2")
            self.base_url = base_url or config.get("base_url", "http://localhost:11434")
        else:
            config = AI_PROVIDERS["cloud"].get(provider, {})
            self.model = model or config.get("default_model", "gpt-4o")
            self.api_key = api_key

    def set_consultation_type(self, consultation_type: str):
        """Set the type of consultation for system prompt customization."""
        self.consultation_type = consultation_type

    def get_system_prompt(self) -> str:
        """Get the full system prompt including consultation type."""
        base_prompt = MAIN_SYSTEM_PROMPT
        type_config = CONSULTATION_TYPES.get(self.consultation_type, CONSULTATION_TYPES["custom"])
        return f"{base_prompt}\n\n{type_config['prompt']}"

    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []

    def add_to_history(self, role: str, content: str):
        """Add a message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    async def test_connection(self) -> tuple[bool, str]:
        """Test connection to the AI provider."""
        try:
            if self.provider_type == "local":
                return await self._test_local_connection()
            else:
                return await self._test_cloud_connection()
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    async def _test_local_connection(self) -> tuple[bool, str]:
        """Test connection to local AI provider."""
        if self.provider == "ollama":
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [m["name"] for m in data.get("models", [])]
                        return True, f"Connected. Available models: {', '.join(models[:5])}"
                    return False, f"Server returned status {response.status}"
        else:
            # LM Studio / GPT4All use OpenAI-compatible API
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/models", timeout=5) as response:
                    if response.status == 200:
                        return True, "Connected to local server"
                    return False, f"Server returned status {response.status}"

    async def _test_cloud_connection(self) -> tuple[bool, str]:
        """Test connection to cloud AI provider."""
        if not self.api_key:
            return False, "API key is required for cloud providers"

        if self.provider == "openai":
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                async with session.get("https://api.openai.com/v1/models",
                                       headers=headers, timeout=10) as response:
                    if response.status == 200:
                        return True, "Connected to OpenAI"
                    return False, f"API returned status {response.status}"

        elif self.provider == "anthropic":
            async with aiohttp.ClientSession() as session:
                headers = {
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01"
                }
                # Simple test - just check if key format is valid
                if self.api_key.startswith("sk-ant-"):
                    return True, "API key format valid for Anthropic"
                return False, "Invalid API key format"

        return False, f"Provider {self.provider} not fully implemented"

    async def generate_response(self, user_message: str,
                                phase_context: dict = None) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the AI."""
        self.add_to_history("user", user_message)

        if self.provider_type == "local":
            async for chunk in self._generate_local(user_message, phase_context):
                yield chunk
        else:
            async for chunk in self._generate_cloud(user_message, phase_context):
                yield chunk

    async def _generate_local(self, user_message: str,
                              phase_context: dict = None) -> AsyncGenerator[str, None]:
        """Generate response from local AI provider."""
        if self.provider == "ollama":
            async for chunk in self._generate_ollama(user_message, phase_context):
                yield chunk
        else:
            # OpenAI-compatible API for LM Studio / GPT4All
            async for chunk in self._generate_openai_compatible(user_message, phase_context):
                yield chunk

    async def _generate_ollama(self, user_message: str,
                               phase_context: dict = None) -> AsyncGenerator[str, None]:
        """Generate response using Ollama."""
        messages = [{"role": "system", "content": self.get_system_prompt()}]

        if phase_context:
            context_msg = f"\n\nCurrent Phase: {phase_context.get('phase_name', 'Unknown')}\n"
            context_msg += f"Framework: {phase_context.get('framework', 'UDL/WCAG')}\n"
            context_msg += f"Focus: {phase_context.get('why', '')}"
            messages[0]["content"] += context_msg

        messages.extend(self.conversation_history)

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        full_response = ""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        yield f"Error: {error_text}"
                        return

                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                if "message" in data and "content" in data["message"]:
                                    chunk = data["message"]["content"]
                                    full_response += chunk
                                    yield chunk
                            except json.JSONDecodeError:
                                continue

            self.add_to_history("assistant", full_response)

        except asyncio.TimeoutError:
            yield "\n\n[Response timed out. Please try again.]"
        except aiohttp.ClientError as e:
            yield f"\n\n[Connection error: {str(e)}]"

    async def _generate_openai_compatible(self, user_message: str,
                                          phase_context: dict = None) -> AsyncGenerator[str, None]:
        """Generate response using OpenAI-compatible API (LM Studio, GPT4All)."""
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        messages.extend(self.conversation_history)

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        full_response = ""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status != 200:
                        yield f"Error: Server returned status {response.status}"
                        return

                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data_str = line_str[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        chunk = delta["content"]
                                        full_response += chunk
                                        yield chunk
                            except json.JSONDecodeError:
                                continue

            self.add_to_history("assistant", full_response)

        except Exception as e:
            yield f"\n\n[Error: {str(e)}]"

    async def _generate_cloud(self, user_message: str,
                              phase_context: dict = None) -> AsyncGenerator[str, None]:
        """Generate response from cloud AI provider."""
        if self.provider == "openai":
            async for chunk in self._generate_openai(user_message, phase_context):
                yield chunk
        elif self.provider == "anthropic":
            async for chunk in self._generate_anthropic(user_message, phase_context):
                yield chunk
        else:
            yield "Provider not implemented yet."

    async def _generate_openai(self, user_message: str,
                               phase_context: dict = None) -> AsyncGenerator[str, None]:
        """Generate response using OpenAI API."""
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        messages.extend(self.conversation_history)

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        full_response = ""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        yield f"Error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                        return

                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data_str = line_str[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        chunk = delta["content"]
                                        full_response += chunk
                                        yield chunk
                            except json.JSONDecodeError:
                                continue

            self.add_to_history("assistant", full_response)

        except Exception as e:
            yield f"\n\n[Error: {str(e)}]"

    async def _generate_anthropic(self, user_message: str,
                                  phase_context: dict = None) -> AsyncGenerator[str, None]:
        """Generate response using Anthropic API."""
        messages = []
        for msg in self.conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "system": self.get_system_prompt(),
            "messages": messages,
            "stream": True
        }

        full_response = ""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        yield f"Error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                        return

                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data_str = line_str[6:]
                            try:
                                data = json.loads(data_str)
                                if data.get("type") == "content_block_delta":
                                    delta = data.get("delta", {})
                                    if delta.get("type") == "text_delta":
                                        chunk = delta.get("text", "")
                                        full_response += chunk
                                        yield chunk
                            except json.JSONDecodeError:
                                continue

            self.add_to_history("assistant", full_response)

        except Exception as e:
            yield f"\n\n[Error: {str(e)}]"

    def get_available_models(self) -> list:
        """Get available models for current provider."""
        if self.provider_type == "local":
            return AI_PROVIDERS["local"].get(self.provider, {}).get("models", [])
        else:
            return AI_PROVIDERS["cloud"].get(self.provider, {}).get("models", [])
