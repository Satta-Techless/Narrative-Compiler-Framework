"""Tests for Marketing Audit feature computations."""
from ncf.skills.marketing_audit.features import (
    compute_ltv_cac_ratio,
    compute_mer,
    compute_payback_period,
    compute_revenue_growth
)


class TestMarketingAuditFeatures:
    """Test marketing audit specific features."""

    def test_ltv_cac_ratio(self):
        """Test LTV:CAC ratio calculation."""
        data = {
            "financial": {
                "ltv": 3000,
                "cac": 1000
            }
        }

        result = compute_ltv_cac_ratio(data)
        assert result == 3.0

    def test_ltv_cac_ratio_zero_cac(self):
        """Test LTV:CAC with zero CAC."""
        data = {
            "financial": {
                "ltv": 3000,
                "cac": 0
            }
        }

        result = compute_ltv_cac_ratio(data)
        assert result is None

    def test_mer_calculation(self):
        """Test Marketing Efficiency Ratio."""
        data = {
            "financial": {
                "revenue": 500000,
                "marketing_spend": 100000
            }
        }

        result = compute_mer(data)
        assert result == 5.0

    def test_mer_zero_spend(self):
        """Test MER with zero marketing spend."""
        data = {
            "financial": {
                "revenue": 500000,
                "marketing_spend": 0
            }
        }

        result = compute_mer(data)
        assert result is None

    def test_payback_period(self):
        """Test CAC payback period calculation."""
        data = {
            "financial": {
                "ltv": 2400,  # $2400 lifetime value
                "cac": 200    # $200 acquisition cost
            }
        }

        result = compute_payback_period(data)
        # 2400/24 = 100 per month, 200/100 = 2 months
        assert result == 2.0

    def test_revenue_growth(self):
        """Test revenue growth calculation."""
        data = {
            "financial": {
                "revenue": 120000,
                "previous_period_revenue": 100000
            }
        }

        result = compute_revenue_growth(data)
        assert result == 20.0

    def test_revenue_growth_decline(self):
        """Test revenue growth with decline."""
        data = {
            "financial": {
                "revenue": 80000,
                "previous_period_revenue": 100000
            }
        }

        result = compute_revenue_growth(data)
        assert result == -20.0


class TestFeatureDeterminism:
    """Test that feature computations are deterministic."""

    def test_features_are_deterministic(self):
        """Test that same input always produces same output."""
        data = {
            "financial": {
                "ltv": 3000,
                "cac": 1000,
                "revenue": 500000,
                "marketing_spend": 100000
            }
        }

        # Run multiple times
        results = [compute_ltv_cac_ratio(data) for _ in range(3)]

        # All results should be identical
        assert all(r == results[0] for r in results)
        assert results[0] == 3.0
