"""Tests for Feature Layer - deterministic computations."""
from ncf.layers.feature import (
    compute_growth_rate,
    compute_ratio,
    compute_percentage,
    FeatureLayer
)


class TestFeatureComputations:
    """Test individual feature computation functions."""

    def test_compute_growth_rate_positive(self):
        """Test growth rate calculation with increase."""
        result = compute_growth_rate(120, 100)
        assert result == 20.0

    def test_compute_growth_rate_negative(self):
        """Test growth rate calculation with decrease."""
        result = compute_growth_rate(80, 100)
        assert result == -20.0

    def test_compute_growth_rate_zero_baseline(self):
        """Test growth rate with zero baseline."""
        result = compute_growth_rate(100, 0)
        assert result is None

    def test_compute_growth_rate_none_values(self):
        """Test growth rate with None values."""
        result = compute_growth_rate(None, 100)
        assert result is None

    def test_compute_ratio_valid(self):
        """Test ratio calculation."""
        result = compute_ratio(100, 25)
        assert result == 4.0

    def test_compute_ratio_zero_denominator(self):
        """Test ratio with zero denominator."""
        result = compute_ratio(100, 0)
        assert result is None

    def test_compute_percentage_valid(self):
        """Test percentage calculation."""
        result = compute_percentage(25, 100)
        assert result == 25.0

    def test_compute_percentage_zero_total(self):
        """Test percentage with zero total."""
        result = compute_percentage(25, 0)
        assert result is None


class TestFeatureLayer:
    """Test Feature Layer node."""

    def test_feature_layer_execution(self):
        """Test feature layer executes features correctly."""
        features = {
            "discount_pct": lambda data: ((data["original"] - data["current"]) / data["original"]) * 100,
            "savings": lambda data: data["original"] - data["current"]
        }

        layer = FeatureLayer(features=features)

        from ncf.core.node import NodeInput
        input_data = NodeInput(data={
            "original": 100,
            "current": 75
        })

        result = layer.execute(input_data)

        assert result.data["discount_pct"] == 25.0
        assert result.data["savings"] == 25
        assert result.data["original"] == 100  # Original data preserved
        assert result.data["current"] == 75

    def test_feature_layer_handles_errors(self):
        """Test feature layer handles computation errors gracefully."""
        features = {
            "will_error": lambda data: data["missing_key"]
        }

        layer = FeatureLayer(features=features)

        from ncf.core.node import NodeInput
        input_data = NodeInput(data={"valid": 123})

        # Should handle error gracefully
        result = layer.execute(input_data)
        assert "will_error" in result.data
        assert result.data["will_error"] is None
