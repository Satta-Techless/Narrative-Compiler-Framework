"""
Sample data for Marketing Audit Report demonstration.
"""

SAMPLE_MARKETING_DATA = {
    "report_period": "Q1 2024",

    "financial": {
        "cac": 250.00,
        "ltv": 1200.00,
        "marketing_spend": 150000.00,
        "revenue": 500000.00,
        "previous_period_revenue": 425000.00,
        "planned_budget": 160000.00
    },

    "web_traffic": {
        "sessions": 50000,
        "bounce_rate": 45.5,
        "avg_session_duration": 180.0,
        "conversions": 1500,
        "conversion_rate": 3.0,
        "previous_period_sessions": 45000
    },

    "funnel": {
        "top_funnel_traffic": 50000,
        "mid_funnel_leads": 5000,
        "bottom_funnel_sqls": 750,
        "sql_to_close_rate": 25.0,
        "avg_sales_cycle_days": 45.0
    },

    "channels": [
        {
            "channel_name": "Google Ads",
            "spend": 45000.00,
            "impressions": 2000000,
            "clicks": 50000,
            "conversions": 600,
            "revenue": 180000.00
        },
        {
            "channel_name": "Facebook Ads",
            "spend": 30000.00,
            "impressions": 1500000,
            "clicks": 30000,
            "conversions": 400,
            "revenue": 120000.00
        },
        {
            "channel_name": "LinkedIn Ads",
            "spend": 25000.00,
            "impressions": 500000,
            "clicks": 15000,
            "conversions": 300,
            "revenue": 150000.00
        },
        {
            "channel_name": "SEO/Content",
            "spend": 20000.00,
            "impressions": None,
            "clicks": None,
            "conversions": 200,
            "revenue": 50000.00
        }
    ],

    "competitors": [
        {
            "competitor_name": "CompetitorA",
            "pricing_tier": "premium",
            "estimated_market_share": 25.0,
            "sov": 35.0
        },
        {
            "competitor_name": "CompetitorB",
            "pricing_tier": "mid-market",
            "estimated_market_share": 20.0,
            "sov": 25.0
        },
        {
            "competitor_name": "Our Company",
            "pricing_tier": "mid-market",
            "estimated_market_share": 15.0,
            "sov": 20.0
        }
    ],

    "brand": {
        "nps": 45.0,
        "support_tickets": 350,
        "avg_ticket_resolution_days": 2.5
    },

    "operations": {
        "tools_count": 25,
        "tools_spend": 15000.00,
        "team_size": 12,
        "underutilized_tools": [
            {
                "tool_name": "HubSpot Marketing Pro",
                "monthly_cost": 3200.00,
                "utilization_pct": 35.0
            },
            {
                "tool_name": "Adobe Analytics",
                "monthly_cost": 2500.00,
                "utilization_pct": 15.0
            },
            {
                "tool_name": "Salesforce Pardot",
                "monthly_cost": 1800.00,
                "utilization_pct": 25.0
            }
        ]
    },

    "business_goals": "Achieve 50% revenue growth while maintaining LTV:CAC ratio above 3:1",
    "market_conditions": "Increased competition in mid-market segment, rising ad costs, privacy regulations impacting tracking"
}


# Alternative scenario: Struggling company
SAMPLE_STRUGGLING_DATA = {
    "report_period": "Q2 2024",

    "financial": {
        "cac": 450.00,
        "ltv": 900.00,
        "marketing_spend": 200000.00,
        "revenue": 350000.00,
        "previous_period_revenue": 380000.00,
        "planned_budget": 180000.00
    },

    "web_traffic": {
        "sessions": 35000,
        "bounce_rate": 68.5,
        "avg_session_duration": 85.0,
        "conversions": 500,
        "conversion_rate": 1.4,
        "previous_period_sessions": 42000
    },

    "funnel": {
        "top_funnel_traffic": 35000,
        "mid_funnel_leads": 2000,
        "bottom_funnel_sqls": 250,
        "sql_to_close_rate": 15.0,
        "avg_sales_cycle_days": 65.0
    },

    "channels": [
        {
            "channel_name": "Google Ads",
            "spend": 80000.00,
            "conversions": 200,
            "revenue": 120000.00
        },
        {
            "channel_name": "Facebook Ads",
            "spend": 50000.00,
            "conversions": 150,
            "revenue": 80000.00
        },
        {
            "channel_name": "LinkedIn Ads",
            "spend": 40000.00,
            "conversions": 100,
            "revenue": 100000.00
        },
        {
            "channel_name": "SEO/Content",
            "spend": 30000.00,
            "conversions": 50,
            "revenue": 50000.00
        }
    ],

    "competitors": [
        {
            "competitor_name": "MarketLeader",
            "pricing_tier": "premium",
            "sov": 45.0
        }
    ],

    "brand": {
        "nps": 15.0,
        "support_tickets": 580,
        "avg_ticket_resolution_days": 5.5
    },

    "operations": {
        "tools_count": 32,
        "tools_spend": 22000.00,
        "team_size": 8,
        "underutilized_tools": [
            {
                "tool_name": "Marketo",
                "monthly_cost": 5000.00,
                "utilization_pct": 20.0
            },
            {
                "tool_name": "Drift",
                "monthly_cost": 2000.00,
                "utilization_pct": 10.0
            },
            {
                "tool_name": "Optimizely",
                "monthly_cost": 3500.00,
                "utilization_pct": 5.0
            }
        ]
    },

    "business_goals": "Stop revenue decline and improve unit economics",
    "market_conditions": "Economic headwinds, increased price sensitivity, new entrants disrupting market"
}
