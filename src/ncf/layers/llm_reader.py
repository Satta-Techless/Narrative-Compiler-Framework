"""
LLM-Reader Layer implementation.

Extracts structured facts from unstructured text input.
"""
from typing import Dict, Any, Optional
from ncf.core.node import LLMNode, NodeType, NodeInput, NodeOutput
from ncf.utils.llm_provider import BaseLLMProvider, LLMRequest, LLMMessage


class LLMReader(LLMNode):
    """
    LLM-Reader: Extract structured data from unstructured text.

    Uses an LLM to parse unstructured input (transcripts, documents, etc.)
    into a strict JSON schema. Forbidden from inference or creative generation.
    """

    def __init__(
        self,
        provider: BaseLLMProvider,
        schema: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the LLM-Reader.

        Args:
            provider: LLM provider instance
            schema: JSON schema for extraction
            config: Optional configuration
        """
        super().__init__(NodeType.LLM_READER, config)
        self.provider = provider
        self.schema = schema
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build the system prompt for extraction."""
        return """You are a precise data extraction assistant.

Your ONLY job is to extract facts from the provided text into the specified JSON schema.

RULES:
1. Extract ONLY facts explicitly stated in the text
2. Do NOT infer, guess, or add information
3. Do NOT categorize or classify
4. Do NOT generate creative content
5. If a field cannot be found in the text, use null
6. Be exact with numbers, dates, and names

You are a fact extractor, not a creative writer or analyst."""

    def execute(self, input_data: NodeInput) -> NodeOutput:
        """
        Execute extraction from unstructured text.

        Args:
            input_data: Input containing unstructured text

        Returns:
            NodeOutput with extracted structured data
        """
        # Get the text to extract from
        text_field = self.config.get("text_field", "text")
        if text_field not in input_data.data:
            raise ValueError(f"Text field '{text_field}' not found in input data")

        text = input_data.data[text_field]

        # Create extraction prompt
        user_prompt = f"""Extract data from the following text:\n\n{text}"""

        # Build request
        request = LLMRequest(
            messages=[
                LLMMessage(role="system", content=self.system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ],
            temperature=0.0,  # Deterministic
            max_tokens=self.config.get("max_tokens", 2000)
        )

        # Get structured output
        extracted_data = self.provider.complete_structured(request, self.schema)

        # Track usage
        self.metadata.provenance["extraction"] = {
            "provider": self.provider.__class__.__name__,
            "model": self.provider.default_model,
            "schema_keys": list(self.schema.get("properties", {}).keys())
        }

        # Merge extracted data with original input
        output_data = {**input_data.data, **extracted_data}

        return NodeOutput(
            data=output_data,
            metadata=self.metadata,
            provenance=self.metadata.provenance
        )

    def validate_input(self, input_data: NodeInput) -> bool:
        """Validate that input contains text field."""
        text_field = self.config.get("text_field", "text")
        return text_field in input_data.data
