"""
Feature computations for Marketing Audit Report.

All deterministic calculations for the marketing audit.
"""
from typing import Dict, Any, Optional, List
from ncf.layers.feature import (
    compute_growth_rate,
    compute_ratio,
    compute_percentage,
    categorize_value
)


def compute_ltv_cac_ratio(data: Dict[str, Any]) -> Optional[float]:
    """Compute LTV:CAC ratio."""
    ltv = data.get("financial", {}).get("ltv")
    cac = data.get("financial", {}).get("cac")
    return compute_ratio(ltv, cac)


def compute_mer(data: Dict[str, Any]) -> Optional[float]:
    """
    Compute Marketing Efficiency Ratio (MER).
    MER = Revenue / Marketing Spend
    """
    revenue = data.get("financial", {}).get("revenue")
    spend = data.get("financial", {}).get("marketing_spend")
    return compute_ratio(revenue, spend)


def compute_payback_period(data: Dict[str, Any]) -> Optional[float]:
    """
    Compute CAC Payback Period in months.
    Simplified: CAC / (LTV / Expected Customer Lifetime in months)
    For this example: CAC / (Monthly Revenue per Customer)
    """
    cac = data.get("financial", {}).get("cac")
    ltv = data.get("financial", {}).get("ltv")

    if not cac or not ltv:
        return None

    # Assume average customer lifetime of 24 months
    monthly_value = ltv / 24
    if monthly_value == 0:
        return None

    return cac / monthly_value


def compute_revenue_growth(data: Dict[str, Any]) -> Optional[float]:
    """Compute revenue growth rate."""
    current = data.get("financial", {}).get("revenue")
    previous = data.get("financial", {}).get("previous_period_revenue")
    return compute_growth_rate(current, previous)


def compute_budget_utilization(data: Dict[str, Any]) -> Optional[float]:
    """Compute budget utilization percentage."""
    actual = data.get("financial", {}).get("marketing_spend")
    planned = data.get("financial", {}).get("planned_budget")
    return compute_percentage(actual, planned)


def compute_funnel_conversion_rates(data: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """Compute conversion rates through the funnel."""
    funnel = data.get("funnel", {})

    top = funnel.get("top_funnel_traffic", 0)
    mid = funnel.get("mid_funnel_leads", 0)
    bottom = funnel.get("bottom_funnel_sqls", 0)

    return {
        "top_to_mid_rate": compute_percentage(mid, top) if top > 0 else None,
        "mid_to_bottom_rate": compute_percentage(bottom, mid) if mid > 0 else None,
        "top_to_bottom_rate": compute_percentage(bottom, top) if top > 0 else None,
    }


def compute_channel_roas(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compute ROAS for each channel."""
    channels = data.get("channels", [])
    channel_roas = []

    for channel in channels:
        revenue = channel.get("revenue", 0)
        spend = channel.get("spend", 1)  # Avoid division by zero

        roas = revenue / spend if spend > 0 else None

        channel_roas.append({
            "channel_name": channel.get("channel_name"),
            "roas": roas,
            "spend": spend,
            "revenue": revenue
        })

    return sorted(channel_roas, key=lambda x: x.get("roas") or 0, reverse=True)


def compute_traffic_growth(data: Dict[str, Any]) -> Optional[float]:
    """Compute traffic growth rate."""
    current = data.get("web_traffic", {}).get("sessions")
    previous = data.get("web_traffic", {}).get("previous_period_sessions")
    return compute_growth_rate(current, previous)


def compute_shelfware_cost(data: Dict[str, Any]) -> float:
    """Compute cost of underutilized tools."""
    operations = data.get("operations", {})
    underutilized = operations.get("underutilized_tools", [])

    total_waste = sum(tool.get("monthly_cost", 0) for tool in underutilized)
    return total_waste


def compute_cost_per_acquisition(data: Dict[str, Any]) -> Optional[float]:
    """Compute actual cost per acquisition from web traffic."""
    spend = data.get("financial", {}).get("marketing_spend")
    conversions = data.get("web_traffic", {}).get("conversions")
    return compute_ratio(spend, conversions)


def aggregate_channel_spend(data: Dict[str, Any]) -> float:
    """Total spend across all channels."""
    channels = data.get("channels", [])
    return sum(channel.get("spend", 0) for channel in channels)


def compute_blended_roas(data: Dict[str, Any]) -> Optional[float]:
    """Compute blended ROAS across all channels."""
    total_revenue = sum(ch.get("revenue", 0) for ch in data.get("channels", []))
    total_spend = aggregate_channel_spend(data)
    return compute_ratio(total_revenue, total_spend)


# Feature computation registry for the Marketing Audit skill

MARKETING_AUDIT_FEATURES = {
    # Financial metrics
    "ltv_cac_ratio": compute_ltv_cac_ratio,
    "mer": compute_mer,
    "payback_period_months": compute_payback_period,
    "revenue_growth_pct": compute_revenue_growth,
    "budget_utilization_pct": compute_budget_utilization,

    # Funnel metrics
    "funnel_conversion_rates": compute_funnel_conversion_rates,

    # Channel metrics
    "channel_roas_ranked": compute_channel_roas,
    "blended_roas": compute_blended_roas,
    "total_channel_spend": aggregate_channel_spend,

    # Traffic metrics
    "traffic_growth_pct": compute_traffic_growth,

    # Operations metrics
    "shelfware_monthly_cost": compute_shelfware_cost,
    "actual_cpa": compute_cost_per_acquisition,
}


def get_all_features(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute all features for the marketing audit.

    Args:
        data: Input data

    Returns:
        Dictionary of all computed features
    """
    features = {}

    for feature_name, computation_func in MARKETING_AUDIT_FEATURES.items():
        try:
            features[feature_name] = computation_func(data)
        except Exception as e:
            features[feature_name] = None
            features[f"{feature_name}_error"] = str(e)

    return features
