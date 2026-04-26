"""Tests for GeminiProvider."""
import json
import pytest
from unittest.mock import MagicMock, patch


def _import_llm_provider():
    """Import llm_provider directly, bypassing the ncf package __init__.py."""
    import importlib.util
    import os
    spec = importlib.util.spec_from_file_location(
        "ncf.utils.llm_provider",
        os.path.join(
            os.path.dirname(__file__),
            "../src/ncf/utils/llm_provider.py",
        ),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_llm = _import_llm_provider()
GeminiProvider = _llm.GeminiProvider
LLMProvider = _llm.LLMProvider
LLMMessage = _llm.LLMMessage
LLMRequest = _llm.LLMRequest
LLMResponse = _llm.LLMResponse
create_provider = _llm.create_provider


class TestLLMProviderEnum:
    """Test that the GEMINI value is present in the enum."""

    def test_gemini_in_enum(self):
        assert LLMProvider.GEMINI == "gemini"

    def test_gemini_from_string(self):
        assert LLMProvider("gemini") == LLMProvider.GEMINI


class TestCreateProviderFactory:
    """Test create_provider factory for Gemini."""

    def test_create_gemini_provider_by_enum(self):
        with patch("google.genai.Client"):
            provider = create_provider(LLMProvider.GEMINI, api_key="test-key")
        assert isinstance(provider, GeminiProvider)

    def test_create_gemini_provider_by_string(self):
        with patch("google.genai.Client"):
            provider = create_provider("gemini", api_key="test-key")
        assert isinstance(provider, GeminiProvider)

    def test_create_gemini_provider_default_model(self):
        with patch("google.genai.Client"):
            provider = create_provider("gemini", api_key="test-key")
        assert provider.default_model == GeminiProvider.DEFAULT_MODEL

    def test_create_gemini_provider_custom_model(self):
        with patch("google.genai.Client"):
            provider = create_provider("gemini", api_key="test-key", model="gemini-1.5-flash")
        assert provider.default_model == "gemini-1.5-flash"


class TestGeminiProviderInit:
    """Test GeminiProvider initialization."""

    def test_init_with_api_key(self):
        with patch("google.genai.Client") as mock_client_cls:
            provider = GeminiProvider(api_key="my-key")
        mock_client_cls.assert_called_once_with(api_key="my-key")
        assert provider.api_key == "my-key"
        assert provider.default_model == GeminiProvider.DEFAULT_MODEL

    def test_init_without_api_key(self):
        with patch("google.genai.Client") as mock_client_cls:
            GeminiProvider()
        mock_client_cls.assert_called_once_with()

    def test_init_custom_model(self):
        with patch("google.genai.Client"):
            provider = GeminiProvider(model="gemini-1.5-flash")
        assert provider.default_model == "gemini-1.5-flash"


class TestGeminiProviderComplete:
    """Test GeminiProvider.complete()."""

    def _make_provider(self):
        with patch("google.genai.Client"):
            provider = GeminiProvider(api_key="test-key")
        return provider

    def _make_mock_response(self, text: str):
        response = MagicMock()
        response.text = text
        candidate = MagicMock()
        candidate.finish_reason = "STOP"
        response.candidates = [candidate]
        usage = MagicMock()
        usage.prompt_token_count = 10
        usage.candidates_token_count = 20
        usage.total_token_count = 30
        response.usage_metadata = usage
        return response

    def test_complete_returns_llm_response(self):
        provider = self._make_provider()
        mock_response = self._make_mock_response("Hello from Gemini!")
        provider.client.models.generate_content.return_value = mock_response

        result = provider.complete(LLMRequest(
            messages=[LLMMessage(role="user", content="Hi")]
        ))

        assert isinstance(result, LLMResponse)
        assert result.content == "Hello from Gemini!"
        assert result.model == GeminiProvider.DEFAULT_MODEL
        assert result.usage["prompt_tokens"] == 10
        assert result.usage["completion_tokens"] == 20
        assert result.usage["total_tokens"] == 30

    def test_complete_uses_request_model(self):
        provider = self._make_provider()
        mock_response = self._make_mock_response("ok")
        provider.client.models.generate_content.return_value = mock_response

        provider.complete(LLMRequest(
            messages=[LLMMessage(role="user", content="Hi")],
            model="gemini-1.5-flash"
        ))

        call_kwargs = provider.client.models.generate_content.call_args[1]
        assert call_kwargs["model"] == "gemini-1.5-flash"

    def test_system_message_passed_as_system_instruction(self):
        provider = self._make_provider()
        mock_response = self._make_mock_response("ok")
        provider.client.models.generate_content.return_value = mock_response

        provider.complete(LLMRequest(messages=[
            LLMMessage(role="system", content="You are helpful."),
            LLMMessage(role="user", content="Hello"),
        ]))

        call_kwargs = provider.client.models.generate_content.call_args[1]
        config = call_kwargs["config"]
        assert config.system_instruction == "You are helpful."

    def test_multi_turn_contents_built_correctly(self):
        provider = self._make_provider()
        mock_response = self._make_mock_response("ok")
        provider.client.models.generate_content.return_value = mock_response

        provider.complete(LLMRequest(messages=[
            LLMMessage(role="user", content="Turn 1"),
            LLMMessage(role="assistant", content="Response 1"),
            LLMMessage(role="user", content="Turn 2"),
        ]))

        call_kwargs = provider.client.models.generate_content.call_args[1]
        contents = call_kwargs["contents"]
        assert len(contents) == 3
        assert contents[0].role == "user"
        assert contents[1].role == "model"
        assert contents[2].role == "user"

    def test_no_system_instruction_when_no_system_messages(self):
        provider = self._make_provider()
        mock_response = self._make_mock_response("ok")
        provider.client.models.generate_content.return_value = mock_response

        provider.complete(LLMRequest(messages=[
            LLMMessage(role="user", content="Hello"),
        ]))

        call_kwargs = provider.client.models.generate_content.call_args[1]
        config = call_kwargs["config"]
        assert not hasattr(config, "system_instruction") or config.system_instruction is None


class TestGeminiProviderCompleteStructured:
    """Test GeminiProvider.complete_structured()."""

    def _make_provider(self):
        with patch("google.genai.Client"):
            provider = GeminiProvider(api_key="test-key")
        return provider

    def test_complete_structured_parses_json(self):
        provider = self._make_provider()
        schema = {"type": "object", "properties": {"answer": {"type": "string"}}}
        expected = {"answer": "42"}

        with patch.object(provider, "complete") as mock_complete:
            mock_complete.return_value = LLMResponse(
                content=json.dumps(expected),
                model=GeminiProvider.DEFAULT_MODEL,
                usage={},
            )
            result = provider.complete_structured(
                LLMRequest(messages=[LLMMessage(role="user", content="What is 6x7?")]),
                schema=schema,
            )

        assert result == expected

    def test_complete_structured_parses_markdown_json(self):
        provider = self._make_provider()
        schema = {"type": "object"}
        expected = {"key": "value"}

        with patch.object(provider, "complete") as mock_complete:
            mock_complete.return_value = LLMResponse(
                content=f'```json\n{json.dumps(expected)}\n```',
                model=GeminiProvider.DEFAULT_MODEL,
                usage={},
            )
            result = provider.complete_structured(
                LLMRequest(messages=[LLMMessage(role="user", content="q")]),
                schema=schema,
            )

        assert result == expected

    def test_complete_structured_raises_on_invalid_json(self):
        provider = self._make_provider()
        with patch.object(provider, "complete") as mock_complete:
            mock_complete.return_value = LLMResponse(
                content="this is not json at all",
                model=GeminiProvider.DEFAULT_MODEL,
                usage={},
            )
            with pytest.raises(ValueError, match="Could not parse JSON"):
                provider.complete_structured(
                    LLMRequest(messages=[LLMMessage(role="user", content="q")]),
                    schema={},
                )

    def test_complete_structured_appends_schema_to_last_user_message(self):
        provider = self._make_provider()
        schema = {"type": "object"}
        captured_request = {}

        def fake_complete(req):
            captured_request["req"] = req
            return LLMResponse(content='{"ok": true}', model=GeminiProvider.DEFAULT_MODEL, usage={})

        with patch.object(provider, "complete", side_effect=fake_complete):
            provider.complete_structured(
                LLMRequest(messages=[LLMMessage(role="user", content="Tell me something.")]),
                schema=schema,
            )

        last_msg = captured_request["req"].messages[-1]
        assert "json" in last_msg.content.lower()
        assert "Tell me something." in last_msg.content

