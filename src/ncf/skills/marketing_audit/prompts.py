"""
Prompt templates for Marketing Audit Report sections.

Each section has a Jinja2 template for constrained generation.
"""

# Section 1: Executive Summary
EXECUTIVE_SUMMARY_PROMPT = """You are writing the Executive Summary section of a Marketing Audit Report.

INPUT DATA (use ONLY these facts):
- Report Period: {{ report_period }}
- LTV:CAC Ratio: {{ ltv_cac_ratio|round(2) }}
- LTV:CAC Health: {{ ltv_cac_health }}
- Marketing Efficiency Ratio (MER): {{ mer|round(2) }}
- MER Health: {{ mer_health }}
- Financial Verdict: {{ financial_verdict }}
- Revenue Growth: {{ revenue_growth_pct|round(1) if revenue_growth_pct else "N/A" }}%

Write a concise executive summary (3-4 paragraphs) that includes:
1. Overall verdict (Pass/Fail or Red/Yellow/Green based on financial_verdict)
2. The MER value and what it means
3. Critical findings (risks and wins)

Use ONLY the numbers provided. Do NOT calculate or infer anything."""

# Section 2: Macro Environment
MACRO_ENVIRONMENT_PROMPT = """You are writing the Macro Environment section of a Marketing Audit Report.

INPUT DATA:
{% if competitors %}
Competitors:
{% for comp in competitors %}
- {{ comp.competitor_name }}: {{ comp.pricing_tier }} tier{% if comp.sov %}, SOV: {{ comp.sov }}%{% endif %}
{% endfor %}
{% endif %}

{% if market_conditions %}
Market Conditions: {{ market_conditions }}
{% endif %}

Write a 2-3 paragraph analysis covering:
1. Market trends
2. Competitive positioning
3. Share of voice summary (if data available)

Use ONLY the data provided."""

# Section 3: Strategy & Brand Health
STRATEGY_BRAND_PROMPT = """You are writing the Strategy & Brand Health section.

INPUT DATA:
- Budget Utilization: {{ budget_utilization_pct|round(1) if budget_utilization_pct else "N/A" }}%
- Budget Status: {{ budget_utilization_status }}
{% if brand and brand.nps %}
- NPS: {{ brand.nps }}
- Churn Risk: {{ churn_risk }}
{% endif %}

Write 2-3 paragraphs covering:
1. The "Say/Do Gap" (based on budget utilization)
2. Brand consistency assessment
3. Customer sentiment (if NPS available)

Use ONLY the numbers provided."""

# Section 4: Financial Performance
FINANCIAL_PERFORMANCE_PROMPT = """You are writing the Financial Performance section.

INPUT DATA:
- LTV:CAC Ratio: {{ ltv_cac_ratio|round(2) }}
- Assessment: {{ ltv_cac_health }} (Goal: >3:1)
- Payback Period: {{ payback_period_months|round(1) }} months
- Payback Assessment: {{ payback_assessment }} (Goal: <12 months)
- Budget Utilization: {{ budget_utilization_pct|round(1) if budget_utilization_pct else "N/A" }}%
- Marketing Spend: ${{ "%.2f"|format(financial.marketing_spend) }}
- Revenue: ${{ "%.2f"|format(financial.revenue) }}

Write 3-4 paragraphs covering:
1. Unit economics (LTV:CAC with the exact ratio)
2. Payback period analysis
3. Budget utilization

Use EXACTLY these numbers. Do NOT recalculate."""

# Section 5: Funnel Analysis
FUNNEL_ANALYSIS_PROMPT = """You are writing the Funnel Analysis section.

INPUT DATA:
- Top of Funnel Traffic: {{ funnel.top_funnel_traffic|int }}
- Top Funnel Health: {{ top_funnel_health }}
- Traffic Growth: {{ traffic_growth_pct|round(1) if traffic_growth_pct else "N/A" }}%

- Mid-Funnel Leads: {{ funnel.mid_funnel_leads|int }}
- Conversion Rate: {{ web_traffic.conversion_rate }}%
- Conversion Health: {{ conversion_rate_health }}

- Bottom-Funnel SQLs: {{ funnel.bottom_funnel_sqls|int }}
- SQL-to-Close Rate: {{ funnel.sql_to_close_rate }}%
- Avg Sales Cycle: {{ funnel.avg_sales_cycle_days|round(0) }} days

Write 3 paragraphs covering:
1. Top of funnel (awareness) - traffic trends
2. Middle of funnel (engagement) - conversion performance
3. Bottom of funnel (conversion) - sales efficiency

Use EXACTLY these numbers."""

# Section 6: Channel Deep Dive
CHANNEL_DEEP_DIVE_PROMPT = """You are writing the Channel Deep Dive section.

INPUT DATA:
Channels Ranked by ROAS:
{% for channel in channel_roas_ranked %}
{{ loop.index }}. {{ channel.channel_name }}: ROAS {{ channel.roas|round(2) if channel.roas else "N/A" }}, Spend ${{ "%.2f"|format(channel.spend) }}, Revenue ${{ "%.2f"|format(channel.revenue) }}
{% endfor %}

Blended ROAS: {{ blended_roas|round(2) if blended_roas else "N/A" }}

Write 3-4 paragraphs analyzing:
1. Top performing channels
2. Underperforming channels
3. Overall channel efficiency
4. Recommendations for reallocation

Use ONLY the numbers provided."""

# Section 7: Operations & Tech Stack
OPERATIONS_TECH_PROMPT = """You are writing the Operations & Tech Stack section.

INPUT DATA:
{% if operations %}
- Total Tools: {{ operations.tools_count }}
- Tools Spend: ${{ "%.2f"|format(operations.tools_spend) }}
- Team Size: {{ operations.team_size }}
{% endif %}
- Shelfware Monthly Cost: ${{ "%.2f"|format(shelfware_monthly_cost) }}
- Shelfware Severity: {{ shelfware_severity }}

{% if operations.underutilized_tools %}
Underutilized Tools:
{% for tool in operations.underutilized_tools %}
- {{ tool.tool_name }}: ${{ tool.monthly_cost }}/mo, {{ tool.utilization_pct }}% utilized
{% endfor %}
{% endif %}

Write 2-3 paragraphs covering:
1. Tool utilization and shelfware report
2. Data hygiene assessment
3. Team structure efficiency

Use EXACTLY these numbers."""

# Section 8: SWOT Synthesis
SWOT_SYNTHESIS_PROMPT = """You are writing the SWOT Synthesis section.

Based on all the analysis, identify:

STRENGTHS (internal positives):
- From LTV:CAC: {{ ltv_cac_health }}
- From MER: {{ mer_health }}
- From conversion: {{ conversion_rate_health }}

WEAKNESSES (internal negatives):
- Budget status: {{ budget_utilization_status }}
- Churn risk: {{ churn_risk }}
- Bounce rate: {{ bounce_rate_assessment }}

OPPORTUNITIES (external positives):
- Revenue growth trend: {{ revenue_growth_classification }}

THREATS (external negatives):
- Market conditions

Write a structured SWOT analysis with 2-3 items in each quadrant.
Use ONLY the classifications provided."""

# Section 9: Roadmap
ROADMAP_PROMPT = """You are writing the Action Roadmap section.

Based on the key findings:
- Financial verdict: {{ financial_verdict }}
- Shelfware severity: {{ shelfware_severity }}
- Top funnel health: {{ top_funnel_health }}
- MER health: {{ mer_health }}

Create a prioritized roadmap with:

IMMEDIATE (0-30 days): Quick wins and stop-the-bleeding actions
STRATEGIC (1-6 months): Process and platform improvements
LONG-TERM (6-12 months): Structural transformations

Resource requirements: Budget and headcount needed

Write 4-5 paragraphs with specific, actionable recommendations."""


# Complete section configuration for MultiSectionWriter

MARKETING_AUDIT_SECTIONS = [
    {
        "name": "executive_summary",
        "prompt_template": EXECUTIVE_SUMMARY_PROMPT,
        "temperature": 0.1,
        "max_tokens": 800
    },
    {
        "name": "macro_environment",
        "prompt_template": MACRO_ENVIRONMENT_PROMPT,
        "temperature": 0.1,
        "max_tokens": 600
    },
    {
        "name": "strategy_brand",
        "prompt_template": STRATEGY_BRAND_PROMPT,
        "temperature": 0.1,
        "max_tokens": 600
    },
    {
        "name": "financial_performance",
        "prompt_template": FINANCIAL_PERFORMANCE_PROMPT,
        "temperature": 0.1,
        "max_tokens": 800
    },
    {
        "name": "funnel_analysis",
        "prompt_template": FUNNEL_ANALYSIS_PROMPT,
        "temperature": 0.1,
        "max_tokens": 700
    },
    {
        "name": "channel_deep_dive",
        "prompt_template": CHANNEL_DEEP_DIVE_PROMPT,
        "temperature": 0.1,
        "max_tokens": 800
    },
    {
        "name": "operations_tech",
        "prompt_template": OPERATIONS_TECH_PROMPT,
        "temperature": 0.1,
        "max_tokens": 600
    },
    {
        "name": "swot_synthesis",
        "prompt_template": SWOT_SYNTHESIS_PROMPT,
        "temperature": 0.1,
        "max_tokens": 700
    },
    {
        "name": "roadmap",
        "prompt_template": ROADMAP_PROMPT,
        "temperature": 0.2,  # Slightly higher for creative recommendations
        "max_tokens": 900
    }
]
