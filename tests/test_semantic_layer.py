"""Tests for Semantic Layer - rule evaluation."""
from ncf.layers.semantic import SemanticLayer, SemanticRule, create_threshold_rule
from ncf.core.node import NodeInput


class TestSemanticRules:
    """Test semantic rule evaluation."""

    def test_threshold_rule_above(self):
        """Test threshold rule when value is above threshold."""
        rule = create_threshold_rule(
            name="performance",
            field="score",
            threshold=80,
            above_label="excellent",
            below_label="needs_improvement",
            output_key="performance_level"
        )

        layer = SemanticLayer()
        layer.add_rule(rule)

        result = layer.execute(NodeInput(data={"score": 90}))

        assert result.data["performance_level"] == "excellent"

    def test_threshold_rule_below(self):
        """Test threshold rule when value is below threshold."""
        rule = create_threshold_rule(
            name="performance",
            field="score",
            threshold=80,
            above_label="excellent",
            below_label="needs_improvement",
            output_key="performance_level"
        )

        layer = SemanticLayer()
        layer.add_rule(rule)

        result = layer.execute(NodeInput(data={"score": 60}))

        assert result.data["performance_level"] == "needs_improvement"

    def test_threshold_rule_equal(self):
        """Test threshold rule when value equals threshold."""
        rule = create_threshold_rule(
            name="performance",
            field="score",
            threshold=80,
            above_label="excellent",
            below_label="needs_improvement",
            output_key="performance_level"
        )

        layer = SemanticLayer()
        layer.add_rule(rule)

        result = layer.execute(NodeInput(data={"score": 80}))

        # At threshold should be above (>=)
        assert result.data["performance_level"] == "excellent"

    def test_multiple_rules(self):
        """Test multiple rules in semantic layer."""
        rule1 = create_threshold_rule(
            name="score_level",
            field="score",
            threshold=70,
            above_label="high",
            below_label="low",
            output_key="score_category"
        )

        rule2 = create_threshold_rule(
            name="revenue_level",
            field="revenue",
            threshold=100000,
            above_label="high_revenue",
            below_label="low_revenue",
            output_key="revenue_category"
        )

        layer = SemanticLayer()
        layer.add_rule(rule1)
        layer.add_rule(rule2)

        result = layer.execute(NodeInput(data={
            "score": 85,
            "revenue": 150000
        }))

        assert result.data["score_category"] == "high"
        assert result.data["revenue_category"] == "high_revenue"

    def test_jsonlogic_rule(self):
        """Test custom JSONLogic rule."""
        rule = SemanticRule(
            name="discount_tier",
            logic={
                "if": [
                    {">=": [{"var": "discount_pct"}, 30]},
                    "premium",
                    {"if": [
                        {">=": [{"var": "discount_pct"}, 15]},
                        "standard",
                        "basic"
                    ]}
                ]
            },
            output_key="tier"
        )

        layer = SemanticLayer()
        layer.add_rule(rule)

        # Test premium tier
        result = layer.execute(NodeInput(data={"discount_pct": 35}))
        assert result.data["tier"] == "premium"

        # Test standard tier
        result = layer.execute(NodeInput(data={"discount_pct": 20}))
        assert result.data["tier"] == "standard"

        # Test basic tier
        result = layer.execute(NodeInput(data={"discount_pct": 10}))
        assert result.data["tier"] == "basic"
