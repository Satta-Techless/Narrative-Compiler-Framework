"""
LLM Provider abstraction for NCF.

Supports multiple LLM providers (OpenAI, Anthropic, Gemini) with a unified interface.
"""
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class StructuredOutputFormat(str, Enum):
    """Supported structured output formats."""
    JSON = "json"
    JSON_SCHEMA = "json_schema"


class LLMMessage(BaseModel):
    """A message in the LLM conversation."""
    role: str  # "system", "user", "assistant"
    content: str


class LLMRequest(BaseModel):
    """Request to an LLM."""
    messages: List[LLMMessage]
    temperature: float = 0.0  # Default to deterministic
    max_tokens: Optional[int] = None
    response_format: Optional[Dict[str, Any]] = None  # For structured outputs
    model: Optional[str] = None


class LLMResponse(BaseModel):
    """Response from an LLM."""
    content: str
    model: str
    usage: Dict[str, int] = Field(default_factory=dict)
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the provider.

        Args:
            api_key: API key for the provider
            model: Default model to use
        """
        self.api_key = api_key
        self.default_model = model

    @abstractmethod
    def complete(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a completion.

        Args:
            request: The LLM request

        Returns:
            LLMResponse with the generated content
        """
        pass

    @abstractmethod
    def complete_structured(
        self,
        request: LLMRequest,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a structured output conforming to a JSON schema.

        Args:
            request: The LLM request
            schema: JSON schema for the output

        Returns:
            Parsed JSON object matching the schema
        """
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Model to use (default: gpt-4o)
        """
        super().__init__(api_key, model)
        import openai
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = openai.OpenAI()  # Uses OPENAI_API_KEY env var

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Generate a completion using OpenAI."""
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        model = request.model or self.default_model

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            finish_reason=response.choices[0].finish_reason,
            raw_response=response.model_dump()
        )

    def complete_structured(
        self,
        request: LLMRequest,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate structured output using OpenAI's structured outputs."""
        import json

        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        model = request.model or self.default_model

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "schema": schema,
                    "strict": True
                }
            }
        )

        content = response.choices[0].message.content
        return json.loads(content)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic (Claude) LLM provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Model to use (default: claude-3-5-sonnet-20241022)
        """
        super().__init__(api_key, model)
        import anthropic
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Generate a completion using Anthropic."""
        # Separate system messages from user/assistant messages
        system_messages = [msg.content for msg in request.messages if msg.role == "system"]
        conversation_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages if msg.role != "system"
        ]

        system = "\n\n".join(system_messages) if system_messages else None

        model = request.model or self.default_model

        response = self.client.messages.create(
            model=model,
            max_tokens=request.max_tokens or 4096,
            temperature=request.temperature,
            system=system,
            messages=conversation_messages
        )

        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            finish_reason=response.stop_reason,
            raw_response={"id": response.id, "type": response.type}
        )

    def complete_structured(
        self,
        request: LLMRequest,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate structured output using prompt engineering."""
        import json

        # Add schema to the last user message
        schema_prompt = f"\n\nYou must respond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"

        # Clone messages and append schema instruction
        enhanced_messages = [LLMMessage(**msg.dict()) for msg in request.messages]
        if enhanced_messages and enhanced_messages[-1].role == "user":
            enhanced_messages[-1].content += schema_prompt
        else:
            enhanced_messages.append(LLMMessage(role="user", content=schema_prompt))

        enhanced_request = LLMRequest(
            messages=enhanced_messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        response = self.complete(enhanced_request)

        # Parse JSON from response
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            raise ValueError(f"Could not parse JSON from response: {response.content}")


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""

    DEFAULT_MODEL = "gemini-2.5-pro"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Gemini provider.

        Args:
            api_key: Google AI API key (or set GOOGLE_API_KEY env var)
            model: Model to use (default: gemini-2.5-pro)
        """
        super().__init__(api_key, model or self.DEFAULT_MODEL)
        import google.genai as genai
        kwargs: Dict[str, Any] = {}
        if api_key:
            kwargs["api_key"] = api_key
        self.client = genai.Client(**kwargs)
        self._genai = genai

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Generate a completion using Gemini."""
        import google.genai.types as genai_types

        model_name = request.model or self.default_model

        # Separate system messages from conversation messages
        system_parts = [msg.content for msg in request.messages if msg.role == "system"]
        conversation = [msg for msg in request.messages if msg.role != "system"]

        # Build contents list (role: "user" or "model")
        contents = []
        for msg in conversation:
            role = "model" if msg.role == "assistant" else "user"
            contents.append(genai_types.Content(
                role=role,
                parts=[genai_types.Part(text=msg.content)],
            ))

        config_kwargs: Dict[str, Any] = {
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            config_kwargs["max_output_tokens"] = request.max_tokens
        if system_parts:
            config_kwargs["system_instruction"] = "\n\n".join(system_parts)

        config = genai_types.GenerateContentConfig(**config_kwargs)

        response = self.client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config,
        )

        text = response.text

        usage_metadata = getattr(response, "usage_metadata", None)
        usage: Dict[str, int] = {}
        if usage_metadata:
            usage = {
                "prompt_tokens": getattr(usage_metadata, "prompt_token_count", 0) or 0,
                "completion_tokens": getattr(usage_metadata, "candidates_token_count", 0) or 0,
                "total_tokens": getattr(usage_metadata, "total_token_count", 0) or 0,
            }

        candidate = response.candidates[0] if response.candidates else None
        finish_reason = str(candidate.finish_reason) if candidate and candidate.finish_reason else None

        return LLMResponse(
            content=text,
            model=model_name,
            usage=usage,
            finish_reason=finish_reason,
            raw_response={"candidates_count": len(response.candidates) if response.candidates else 0},
        )

    def complete_structured(
        self,
        request: LLMRequest,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate structured output using prompt engineering."""
        import json
        import re

        schema_prompt = (
            f"\n\nYou must respond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        )

        enhanced_messages = [LLMMessage(**msg.model_dump()) for msg in request.messages]
        if enhanced_messages and enhanced_messages[-1].role == "user":
            enhanced_messages[-1].content += schema_prompt
        else:
            enhanced_messages.append(LLMMessage(role="user", content=schema_prompt))

        enhanced_request = LLMRequest(
            messages=enhanced_messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        response = self.complete(enhanced_request)

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            raise ValueError(f"Could not parse JSON from response: {response.content}")


def create_provider(
    provider: Union[LLMProvider, str],
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> BaseLLMProvider:
    """
    Factory function to create an LLM provider.

    Args:
        provider: Provider type
        api_key: Optional API key
        model: Optional model name

    Returns:
        Instantiated provider
    """
    if isinstance(provider, str):
        provider = LLMProvider(provider)

    kwargs: Dict[str, Any] = {"api_key": api_key}
    if model is not None:
        kwargs["model"] = model

    if provider == LLMProvider.OPENAI:
        return OpenAIProvider(**kwargs)
    elif provider == LLMProvider.ANTHROPIC:
        return AnthropicProvider(**kwargs)
    elif provider == LLMProvider.GEMINI:
        return GeminiProvider(**kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}")
