"""
Semantic rules for Marketing Audit Report.

JSONLogic rules for classification and tagging.
"""
from typing import Dict, Any, List
from ncf.layers.semantic import SemanticRule, create_threshold_rule, create_range_rule


def create_marketing_audit_rules() -> List[SemanticRule]:
    """Create all semantic rules for marketing audit."""

    rules = []

    # Health Score based on LTV:CAC ratio
    rules.append(SemanticRule(
        name="ltv_cac_health",
        logic={
            "if": [
                {">=": [{"var": "ltv_cac_ratio"}, 3.0]},
                "green",
                {"if": [
                    {">=": [{"var": "ltv_cac_ratio"}, 1.5]},
                    "yellow",
                    "red"
                ]}
            ]
        },
        output_key="ltv_cac_health"
    ))

    # MER Health Score
    rules.append(SemanticRule(
        name="mer_health",
        logic={
            "if": [
                {">=": [{"var": "mer"}, 4.0]},
                "excellent",
                {"if": [
                    {">=": [{"var": "mer"}, 2.0]},
                    "good",
                    {"if": [
                        {">=": [{"var": "mer"}, 1.0]},
                        "poor",
                        "critical"
                    ]}
                ]}
            ]
        },
        output_key="mer_health"
    ))

    # Overall Financial Health
    rules.append(SemanticRule(
        name="financial_verdict",
        logic={
            "if": [
                {"and": [
                    {">=": [{"var": "ltv_cac_ratio"}, 3.0]},
                    {">=": [{"var": "mer"}, 2.0]}
                ]},
                "pass",
                "fail"
            ]
        },
        output_key="financial_verdict"
    ))

    # Payback Period Assessment
    rules.append(SemanticRule(
        name="payback_assessment",
        logic={
            "if": [
                {"<": [{"var": "payback_period_months"}, 12]},
                "healthy",
                {"if": [
                    {"<": [{"var": "payback_period_months"}, 24]},
                    "acceptable",
                    "concerning"
                ]}
            ]
        },
        output_key="payback_assessment"
    ))

    # Revenue Growth Classification
    rules.append(SemanticRule(
        name="revenue_growth_classification",
        logic={
            "if": [
                {">=": [{"var": "revenue_growth_pct"}, 20]},
                "high",
                {"if": [
                    {">=": [{"var": "revenue_growth_pct"}, 10]},
                    "moderate",
                    {"if": [
                        {">=": [{"var": "revenue_growth_pct"}, 0]},
                        "low",
                        "negative"
                    ]}
                ]}
            ]
        },
        output_key="revenue_growth_classification"
    ))

    # Funnel Health - Top of Funnel
    rules.append(SemanticRule(
        name="top_funnel_health",
        logic={
            "if": [
                {">": [{"var": "traffic_growth_pct"}, 0]},
                "growing",
                "declining"
            ]
        },
        output_key="top_funnel_health"
    ))

    # Budget Utilization
    rules.append(SemanticRule(
        name="budget_utilization_status",
        logic={
            "if": [
                {"and": [
                    {">=": [{"var": "budget_utilization_pct"}, 90]},
                    {"<=": [{"var": "budget_utilization_pct"}, 110]}
                ]},
                "on_track",
                {"if": [
                    {"<": [{"var": "budget_utilization_pct"}, 90]},
                    "underspending",
                    "overspending"
                ]}
            ]
        },
        output_key="budget_utilization_status"
    ))

    # Churn Risk (based on NPS if available)
    rules.append(SemanticRule(
        name="churn_risk",
        logic={
            "if": [
                {"!": [{"var": "brand.nps"}]},
                "unknown",
                {"if": [
                    {">=": [{"var": "brand.nps"}, 50]},
                    "low",
                    {"if": [
                        {">=": [{"var": "brand.nps"}, 0]},
                        "moderate",
                        "high"
                    ]}
                ]}
            ]
        },
        output_key="churn_risk"
    ))

    # CAC Trend (comparing actual to reported)
    rules.append(SemanticRule(
        name="cac_efficiency",
        logic={
            "if": [
                {"and": [
                    {"var": "actual_cpa"},
                    {"<": [{"var": "actual_cpa"}, {"var": "financial.cac"}]}
                ]},
                "improving",
                {"if": [
                    {"==": [{"var": "actual_cpa"}, {"var": "financial.cac"}]},
                    "stable",
                    "worsening"
                ]}
            ]
        },
        output_key="cac_efficiency"
    ))

    # Shelfware Assessment
    rules.append(SemanticRule(
        name="shelfware_severity",
        logic={
            "if": [
                {">": [{"var": "shelfware_monthly_cost"}, 5000]},
                "high",
                {"if": [
                    {">": [{"var": "shelfware_monthly_cost"}, 1000]},
                    "moderate",
                    "low"
                ]}
            ]
        },
        output_key="shelfware_severity"
    ))

    # Conversion Rate Health
    rules.append(SemanticRule(
        name="conversion_rate_health",
        logic={
            "if": [
                {">=": [{"var": "web_traffic.conversion_rate"}, 3.0]},
                "strong",
                {"if": [
                    {">=": [{"var": "web_traffic.conversion_rate"}, 1.5]},
                    "average",
                    "weak"
                ]}
            ]
        },
        output_key="conversion_rate_health"
    ))

    # Bounce Rate Assessment
    rules.append(SemanticRule(
        name="bounce_rate_assessment",
        logic={
            "if": [
                {"<": [{"var": "web_traffic.bounce_rate"}, 40]},
                "excellent",
                {"if": [
                    {"<": [{"var": "web_traffic.bounce_rate"}, 55]},
                    "good",
                    {"if": [
                        {"<": [{"var": "web_traffic.bounce_rate"}, 70]},
                        "poor",
                        "critical"
                    ]}
                ]}
            ]
        },
        output_key="bounce_rate_assessment"
    ))

    return rules


# Helper function to get computed semantic tags

def get_all_semantics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute all semantic classifications.

    Args:
        data: Data with computed features

    Returns:
        Dictionary of semantic tags
    """
    from ncf.layers.semantic import SemanticLayer

    semantic_layer = SemanticLayer(rules=create_marketing_audit_rules())
    from ncf.core.node import NodeInput

    result = semantic_layer.execute(NodeInput(data=data))
    return result.data
