"""
LLM-Writer Layer implementation.

Constrained surface realization for fluent text generation.
"""
from typing import Dict, Any, Optional, List
from ncf.core.node import LLMNode, NodeType, NodeInput, NodeOutput
from ncf.utils.llm_provider import BaseLLMProvider, LLMRequest, LLMMessage
from jinja2 import Template


class LLMWriter(LLMNode):
    """
    LLM-Writer: Constrained surface realization.

    The ONLY LLM call in the generation pipeline. Receives pre-computed features
    and semantic tags, then generates fluent prose. Strictly forbidden from:
    - Computing any derived values
    - Making inferences
    - Adding facts not in the input

    The model's ONLY job is surface realization: turning locked facts into fluent text.
    """

    def __init__(
        self,
        provider: BaseLLMProvider,
        prompt_template: str,
        output_schema: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the LLM-Writer.

        Args:
            provider: LLM provider instance
            prompt_template: Jinja2 template for the prompt
            output_schema: Optional JSON schema for structured output
            config: Optional configuration
        """
        super().__init__(NodeType.LLM_WRITER, config)
        self.provider = provider
        self.prompt_template = Template(prompt_template)
        self.output_schema = output_schema
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build the system prompt for constrained generation."""
        return """You are a professional document writer with strict constraints.

Your ONLY job is to write fluent, clear prose using EXACTLY the facts provided.

STRICT RULES:
1. Use ONLY the facts and data provided - do not add, infer, or compute anything
2. Do NOT perform calculations - all numbers are pre-computed
3. Do NOT make inferences or draw conclusions beyond what's stated
4. Do NOT add creative embellishments
5. Match the exact numbers provided - no rounding unless specified
6. Maintain a professional, objective tone
7. Focus on surface realization: turn the structured facts into readable text

You are a compiler, not a creative writer. Your job is deterministic text generation."""

    def execute(self, input_data: NodeInput) -> NodeOutput:
        """
        Execute constrained text generation.

        Args:
            input_data: Input with features and semantic tags

        Returns:
            NodeOutput with generated text
        """
        # Render the prompt template with input data
        user_prompt = self.prompt_template.render(**input_data.data)

        # Build request
        request = LLMRequest(
            messages=[
                LLMMessage(role="system", content=self.system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ],
            temperature=self.config.get("temperature", 0.1),  # Low but not zero for naturalness
            max_tokens=self.config.get("max_tokens", 4000)
        )

        # Generate text
        if self.output_schema:
            # Structured output
            generated = self.provider.complete_structured(request, self.output_schema)
            output_data = {**input_data.data, **generated}
        else:
            # Free text
            response = self.provider.complete(request)
            output_data = {
                **input_data.data,
                "generated_text": response.content
            }

            # Track usage
            self.metadata.provenance["generation"] = {
                "provider": self.provider.__class__.__name__,
                "model": response.model,
                "usage": response.usage,
                "finish_reason": response.finish_reason
            }

        return NodeOutput(
            data=output_data,
            metadata=self.metadata,
            provenance=self.metadata.provenance
        )


class MultiSectionWriter(LLMWriter):
    """
    LLM-Writer for multi-section documents.

    Generates multiple sections with individual prompts and schemas.
    """

    def __init__(
        self,
        provider: BaseLLMProvider,
        sections: List[Dict[str, Any]],  # List of {name, prompt_template, schema}
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize multi-section writer.

        Args:
            provider: LLM provider instance
            sections: List of section configurations
            config: Optional configuration
        """
        # Initialize with dummy template (we'll override execute)
        super().__init__(provider, "", None, config)
        self.sections = sections

    def execute(self, input_data: NodeInput) -> NodeOutput:
        """
        Execute generation for all sections.

        Args:
            input_data: Input with features and semantic tags

        Returns:
            NodeOutput with all generated sections
        """
        generated_sections = {}
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        for section_config in self.sections:
            section_name = section_config["name"]
            template = Template(section_config["prompt_template"])
            schema = section_config.get("schema")

            # Render prompt
            user_prompt = template.render(**input_data.data)

            # Build request
            request = LLMRequest(
                messages=[
                    LLMMessage(role="system", content=self.system_prompt),
                    LLMMessage(role="user", content=user_prompt)
                ],
                temperature=section_config.get("temperature", self.config.get("temperature", 0.1)),
                max_tokens=section_config.get("max_tokens", self.config.get("max_tokens", 2000))
            )

            # Generate
            if schema:
                generated = self.provider.complete_structured(request, schema)
                generated_sections[section_name] = generated
            else:
                response = self.provider.complete(request)
                generated_sections[section_name] = response.content

                # Accumulate usage
                for key in total_usage:
                    total_usage[key] += response.usage.get(key, 0)

        # Combine all sections
        output_data = {
            **input_data.data,
            "sections": generated_sections
        }

        # Track usage
        self.metadata.provenance["generation"] = {
            "provider": self.provider.__class__.__name__,
            "model": self.provider.default_model,
            "sections_generated": len(generated_sections),
            "total_usage": total_usage
        }

        return NodeOutput(
            data=output_data,
            metadata=self.metadata,
            provenance=self.metadata.provenance
        )
