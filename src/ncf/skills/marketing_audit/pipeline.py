"""
Complete Marketing Audit Report Skill pipeline builder.

Assembles all components into a working NCF pipeline.
"""
from typing import Dict, Any, Optional
from ncf.core.dag import NCFPipeline
from ncf.core.node import Node, NodeType, NodeInput, NodeOutput
from ncf.core.orchestrator import Orchestrator
from ncf.layers.feature import FeatureLayer
from ncf.layers.semantic import SemanticLayer
from ncf.layers.llm_writer import MultiSectionWriter
from ncf.layers.validation import ValidationLayer
from ncf.utils.llm_provider import BaseLLMProvider, create_provider, LLMProvider

from ncf.skills.marketing_audit.features import MARKETING_AUDIT_FEATURES
from ncf.skills.marketing_audit.semantics import create_marketing_audit_rules
from ncf.skills.marketing_audit.prompts import MARKETING_AUDIT_SECTIONS
from ncf.skills.marketing_audit.validation import create_marketing_audit_validation_rules


class MarketingAuditPipeline:
    """
    Complete pipeline for generating Marketing Audit Reports.

    Demonstrates the full NCF architecture with all layers.
    """

    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        provider_type: str = "openai",
        api_key: Optional[str] = None
    ):
        """
        Initialize the Marketing Audit pipeline.

        Args:
            llm_provider: Pre-configured LLM provider (optional)
            provider_type: Type of provider if creating new ("openai" or "anthropic")
            api_key: API key for the provider
        """
        # Create or use provided LLM provider
        if llm_provider is None:
            llm_provider = create_provider(provider_type, api_key=api_key)

        self.llm_provider = llm_provider
        self.pipeline = self._build_pipeline()
        self.orchestrator = Orchestrator(self.pipeline, enable_provenance=True)

    def _build_pipeline(self) -> NCFPipeline:
        """Build the complete NCF pipeline for marketing audit."""

        pipeline = NCFPipeline(name="Marketing Audit Report Generator")

        # 1. Input Node
        input_node = InputNode()
        pipeline.add_node("input", input_node)

        # 2. Feature Layer - Deterministic computations
        feature_layer = FeatureLayer(features=MARKETING_AUDIT_FEATURES)
        pipeline.add_node("features", feature_layer)
        pipeline.add_edge("input", "features")

        # 3. Semantic Layer - Rule-based classification
        semantic_layer = SemanticLayer(rules=create_marketing_audit_rules())
        pipeline.add_node("semantics", semantic_layer)
        pipeline.add_edge("features", "semantics")

        # 4. LLM-Writer - Constrained text generation
        writer = MultiSectionWriter(
            provider=self.llm_provider,
            sections=MARKETING_AUDIT_SECTIONS
        )
        pipeline.add_node("writer", writer)
        pipeline.add_edge("semantics", "writer")

        # 5. Validation Layer - Reconciliation
        validation_layer = ValidationLayer(
            rules=create_marketing_audit_validation_rules(),
            config={"auto_validate_numbers": True, "strict_mode": False}
        )
        pipeline.add_node("validation", validation_layer)
        pipeline.add_edge("writer", "validation")

        # 6. Output Node
        output_node = OutputNode()
        pipeline.add_node("output", output_node)
        pipeline.add_edge("validation", "output")

        return pipeline

    def generate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a Marketing Audit Report.

        Args:
            input_data: Marketing data (matches MarketingAuditInput schema)

        Returns:
            Complete report with all sections and validation results
        """
        result = self.orchestrator.execute(input_data)

        if not result.success:
            raise Exception(f"Pipeline execution failed: {result.errors}")

        return result.output

    def dry_run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a dry run without LLM calls.

        Args:
            input_data: Sample marketing data

        Returns:
            Execution plan and validation info
        """
        return self.orchestrator.dry_run(input_data)

    def get_provenance(self) -> Dict[str, Any]:
        """Get full provenance trace from last execution."""
        if self.orchestrator.provenance_tracker:
            return self.orchestrator.provenance_tracker.get_full_trace()
        return {}

    def visualize(self) -> str:
        """Get a text visualization of the pipeline."""
        return self.pipeline.visualize()


class InputNode(Node):
    """Input node for the pipeline."""

    def __init__(self):
        super().__init__(NodeType.INPUT)
        self.is_deterministic = True

    def execute(self, input_data: NodeInput) -> NodeOutput:
        """Pass through input data."""
        return NodeOutput(
            data=input_data.data,
            metadata=self.metadata,
            provenance={"source": "user_input"}
        )


class OutputNode(Node):
    """Output node for the pipeline."""

    def __init__(self):
        super().__init__(NodeType.OUTPUT)
        self.is_deterministic = True

    def execute(self, input_data: NodeInput) -> NodeOutput:
        """Pass through final data."""
        return NodeOutput(
            data=input_data.data,
            metadata=self.metadata,
            provenance={"output": "final_report"}
        )


# Convenience function

def create_marketing_audit_pipeline(
    provider: str = "openai",
    api_key: Optional[str] = None
) -> MarketingAuditPipeline:
    """
    Create a ready-to-use Marketing Audit pipeline.

    Args:
        provider: "openai" or "anthropic"
        api_key: Optional API key (or use environment variable)

    Returns:
        MarketingAuditPipeline instance
    """
    return MarketingAuditPipeline(provider_type=provider, api_key=api_key)
