"""Tests for Validation Layer - output reconciliation."""
from ncf.layers.validation import ValidationLayer, ValidationRule
from ncf.core.node import NodeInput


class TestValidationRules:
    """Test validation rule creation and execution."""

    def test_numeric_validation_pass(self):
        """Test numeric validation passes with correct value."""
        rule = ValidationRule(
            name="check_discount",
            rule_type="numeric",
            field="discount_pct",
            expected_value=25.0
        )

        layer = ValidationLayer(rules=[rule])

        result = layer.execute(NodeInput(data={
            "discount_pct": 25.0,
            "generated_text": "Get 25% off today!"
        }))

        assert "validation" in result.data
        validation = result.data["validation"]
        assert validation["all_passed"] is True
        assert validation["passed_count"] == 1
        assert validation["total_count"] == 1

    def test_numeric_validation_fail(self):
        """Test numeric validation fails with incorrect value."""
        rule = ValidationRule(
            name="check_discount",
            rule_type="numeric",
            field="discount_pct",
            expected_value=25.0
        )

        layer = ValidationLayer(rules=[rule])

        # Generated text claims 30% but actual is 25%
        result = layer.execute(NodeInput(data={
            "discount_pct": 25.0,
            "generated_text": "Get 30% off today!"  # WRONG!
        }))

        assert "validation" in result.data
        validation = result.data["validation"]
        assert validation["all_passed"] is False
        assert validation["passed_count"] == 0
        assert validation["total_count"] == 1
        assert validation["results"][0]["rule"] == "check_discount"
        assert validation["results"][0]["passed"] is False

    def test_multiple_validations(self):
        """Test multiple validation rules."""
        rules = [
            ValidationRule(
                name="check_price",
                rule_type="numeric",
                field="price",
                expected_value=99.99
            ),
            ValidationRule(
                name="check_discount",
                rule_type="numeric",
                field="discount",
                expected_value=20.0
            )
        ]

        layer = ValidationLayer(rules=rules)

        result = layer.execute(NodeInput(data={
            "price": 99.99,
            "discount": 20.0,
            "generated_text": "Price: $99.99 with 20% discount"
        }))

        assert "validation" in result.data
        validation = result.data["validation"]
        assert validation["total_count"] == 2

    def test_validation_with_missing_field(self):
        """Test validation handles missing expected field."""
        rule = ValidationRule(
            name="check_missing",
            rule_type="numeric",
            field="missing_field",
            expected_value=100
        )

        layer = ValidationLayer(rules=[rule])

        result = layer.execute(NodeInput(data={
            "other_field": 50,
            "generated_text": "Some text"
        }))

        # Should handle missing field gracefully
        assert "validation" in result.data


class TestValidationLayer:
    """Test ValidationLayer node."""

    def test_validation_layer_deterministic(self):
        """Test that validation layer is deterministic."""
        rules = [
            ValidationRule(
                name="check_value",
                rule_type="numeric",
                field="value",
                expected_value=42
            )
        ]

        layer = ValidationLayer(rules=rules)

        input_data = NodeInput(data={
            "value": 42,
            "generated_text": "The answer is 42"
        })

        # Run twice - should get same result
        result1 = layer.execute(input_data)
        result2 = layer.execute(input_data)

        assert result1.data["validation"] == result2.data["validation"]
