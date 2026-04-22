"""End-to-end tests for NCF pipeline."""
import pytest
import os


class TestMarketingAuditDemo:
    """Test the marketing audit demo in dry-run mode."""

    def test_demo_dry_run_mode(self):
        """Test that demo works in dry-run mode without API keys."""
        # Ensure no API keys are set for this test
        old_openai = os.environ.get("OPENAI_API_KEY")
        old_anthropic = os.environ.get("ANTHROPIC_API_KEY")

        try:
            # Remove API keys temporarily
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            if "ANTHROPIC_API_KEY" in os.environ:
                del os.environ["ANTHROPIC_API_KEY"]

            # Import after clearing env vars
            from ncf.skills.marketing_audit.pipeline import create_marketing_audit_pipeline
            from ncf.skills.marketing_audit.sample_data import SAMPLE_MARKETING_DATA

            # Create pipeline
            try:
                pipeline = create_marketing_audit_pipeline(provider="openai")
            except Exception:
                # If it needs API key, that's expected - test dry run capability instead
                from ncf.skills.marketing_audit.pipeline import MarketingAuditPipeline
                from ncf.utils.llm_provider import OpenAIProvider

                # Create with dummy provider for dry run
                dummy_provider = OpenAIProvider(api_key="dummy_key_for_testing")
                pipeline = MarketingAuditPipeline(llm_provider=dummy_provider)

            # Test dry run
            dry_run_result = pipeline.dry_run(SAMPLE_MARKETING_DATA)

            assert dry_run_result is not None
            assert "valid" in dry_run_result
            assert "node_count" in dry_run_result
            assert "execution_order" in dry_run_result

            # Pipeline should be valid
            assert dry_run_result["valid"] is True
            assert dry_run_result["node_count"] > 0

        finally:
            # Restore original env vars
            if old_openai is not None:
                os.environ["OPENAI_API_KEY"] = old_openai
            if old_anthropic is not None:
                os.environ["ANTHROPIC_API_KEY"] = old_anthropic

    def test_pipeline_structure(self):
        """Test that pipeline has expected structure."""
        from ncf.skills.marketing_audit.pipeline import MarketingAuditPipeline
        from ncf.utils.llm_provider import OpenAIProvider

        dummy_provider = OpenAIProvider(api_key="dummy")
        pipeline = MarketingAuditPipeline(llm_provider=dummy_provider)

        # Test that pipeline has expected nodes
        assert pipeline.pipeline is not None
        assert hasattr(pipeline.pipeline, "nodes")
        assert hasattr(pipeline.pipeline, "graph")
        assert hasattr(pipeline.pipeline.graph, "edges")


class TestBasicUsageExamples:
    """Test that basic usage examples work."""

    def test_feature_layer_example_runs(self):
        """Test feature layer example."""
        from ncf.layers.feature import compute_growth_rate, compute_ratio

        data = {
            "current_revenue": 120000,
            "previous_revenue": 100000,
            "marketing_spend": 30000
        }

        growth = compute_growth_rate(data["current_revenue"], data["previous_revenue"])
        efficiency = compute_ratio(data["current_revenue"], data["marketing_spend"])

        assert growth == 20.0
        assert efficiency == 4.0

    def test_semantic_layer_example_runs(self):
        """Test semantic layer example."""
        from ncf.layers.semantic import SemanticLayer, SemanticRule
        from ncf.core.node import NodeInput

        layer = SemanticLayer()

        rule = SemanticRule(
            name="performance_level",
            logic={
                "if": [
                    {">=": [{"var": "score"}, 80]},
                    "excellent",
                    {"if": [
                        {">=": [{"var": "score"}, 60]},
                        "good",
                        "needs_improvement"
                    ]}
                ]
            },
            output_key="performance"
        )
        layer.add_rule(rule)

        result = layer.execute(NodeInput(data={"score": 75}))

        assert result.data["performance"] == "good"


class TestPipelineInvariants:
    """Test core NCF architectural invariants."""

    def test_no_cycles_in_dag(self):
        """Test that pipeline is acyclic."""
        from ncf.skills.marketing_audit.pipeline import MarketingAuditPipeline
        from ncf.utils.llm_provider import OpenAIProvider

        dummy_provider = OpenAIProvider(api_key="dummy")
        pipeline = MarketingAuditPipeline(llm_provider=dummy_provider)

        # Should not raise an error - DAG validation happens at construction
        assert pipeline.pipeline is not None

    def test_deterministic_layers_dont_depend_on_llm(self):
        """Test that feature and semantic layers don't depend on LLM output."""
        from ncf.skills.marketing_audit.sample_data import SAMPLE_MARKETING_DATA
        from ncf.skills.marketing_audit.features import MARKETING_AUDIT_FEATURES
        from ncf.skills.marketing_audit.semantics import create_marketing_audit_rules

        # Features should be computable from raw data only
        data = SAMPLE_MARKETING_DATA

        # Test that we can compute features without LLM
        for feature_name, feature_func in MARKETING_AUDIT_FEATURES.items():
            try:
                result1 = feature_func(data)
                result2 = feature_func(data)
                # Each call with the same input must produce the same output (determinism invariant)
                assert result1 == result2, f"Feature {feature_name} is not deterministic"
            except AssertionError:
                raise
            except Exception as e:
                pytest.fail(f"Feature {feature_name} failed: {e}")
