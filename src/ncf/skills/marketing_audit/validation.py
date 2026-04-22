"""
Validation rules for Marketing Audit Report.
"""
from typing import List
from ncf.layers.validation import ValidationRule


def create_marketing_audit_validation_rules() -> List[ValidationRule]:
    """Create validation rules for the marketing audit report."""

    rules = []

    # Validate key financial numbers
    rules.append(ValidationRule(
        name="ltv_cac_ratio_present",
        rule_type="numeric",
        field="ltv_cac_ratio"
    ))

    rules.append(ValidationRule(
        name="mer_present",
        rule_type="numeric",
        field="mer"
    ))

    rules.append(ValidationRule(
        name="payback_period_present",
        rule_type="numeric",
        field="payback_period_months"
    ))

    rules.append(ValidationRule(
        name="marketing_spend_present",
        rule_type="numeric",
        field="financial.marketing_spend"
    ))

    rules.append(ValidationRule(
        name="revenue_present",
        rule_type="numeric",
        field="financial.revenue"
    ))

    # Validate traffic numbers
    rules.append(ValidationRule(
        name="sessions_present",
        rule_type="numeric",
        field="web_traffic.sessions"
    ))

    rules.append(ValidationRule(
        name="conversion_rate_present",
        rule_type="numeric",
        field="web_traffic.conversion_rate"
    ))

    # Validate funnel numbers
    rules.append(ValidationRule(
        name="top_funnel_traffic_present",
        rule_type="numeric",
        field="funnel.top_funnel_traffic"
    ))

    rules.append(ValidationRule(
        name="mid_funnel_leads_present",
        rule_type="numeric",
        field="funnel.mid_funnel_leads"
    ))

    rules.append(ValidationRule(
        name="bottom_funnel_sqls_present",
        rule_type="numeric",
        field="funnel.bottom_funnel_sqls"
    ))

    # Validate semantic classifications appear in text
    rules.append(ValidationRule(
        name="ltv_cac_health_mentioned",
        rule_type="exact",
        field="ltv_cac_health"
    ))

    rules.append(ValidationRule(
        name="financial_verdict_mentioned",
        rule_type="exact",
        field="financial_verdict"
    ))

    # Validate report period is mentioned
    rules.append(ValidationRule(
        name="report_period_mentioned",
        rule_type="exact",
        field="report_period"
    ))

    return rules
