"""
Schema definitions for Marketing Audit Report.

Defines the input and output data structures for the marketing audit skill.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


# Input Schemas

class FinancialMetrics(BaseModel):
    """Financial performance metrics."""
    cac: float = Field(description="Customer Acquisition Cost")
    ltv: float = Field(description="Lifetime Value")
    marketing_spend: float
    revenue: float
    previous_period_revenue: Optional[float] = None
    planned_budget: Optional[float] = None


class WebTrafficMetrics(BaseModel):
    """Website traffic and behavior metrics."""
    sessions: int
    bounce_rate: float
    avg_session_duration: float  # in seconds
    conversions: int
    conversion_rate: float
    previous_period_sessions: Optional[int] = None


class FunnelMetrics(BaseModel):
    """Marketing funnel metrics."""
    top_funnel_traffic: int
    mid_funnel_leads: int
    bottom_funnel_sqls: int
    sql_to_close_rate: float
    avg_sales_cycle_days: float


class ChannelMetrics(BaseModel):
    """Individual channel performance."""
    channel_name: str
    spend: float
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    conversions: int
    revenue: float
    roas: Optional[float] = None  # Return on Ad Spend


class CompetitorData(BaseModel):
    """Competitor information."""
    competitor_name: str
    pricing_tier: str  # "budget", "mid-market", "premium"
    estimated_market_share: Optional[float] = None
    sov: Optional[float] = None  # Share of Voice


class BrandMetrics(BaseModel):
    """Brand health metrics."""
    nps: Optional[float] = Field(None, description="Net Promoter Score")
    support_tickets: Optional[int] = None
    avg_ticket_resolution_days: Optional[float] = None


class OperationsMetrics(BaseModel):
    """Operations and tech stack metrics."""
    tools_count: int
    tools_spend: float
    underutilized_tools: List[Dict[str, Any]] = Field(default_factory=list)
    team_size: int


class MarketingAuditInput(BaseModel):
    """Complete input for Marketing Audit Report."""

    # Time period
    report_period: str = Field(description="e.g., 'Q1 2024'")
    report_date: datetime = Field(default_factory=datetime.utcnow)

    # Core metrics
    financial: FinancialMetrics
    web_traffic: WebTrafficMetrics
    funnel: FunnelMetrics
    channels: List[ChannelMetrics]

    # Context
    competitors: List[CompetitorData] = Field(default_factory=list)
    brand: Optional[BrandMetrics] = None
    operations: Optional[OperationsMetrics] = None

    # Strategic context
    business_goals: Optional[str] = None
    market_conditions: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "report_period": "Q1 2024",
                "financial": {
                    "cac": 250,
                    "ltv": 1200,
                    "marketing_spend": 150000,
                    "revenue": 500000,
                    "previous_period_revenue": 450000
                },
                "web_traffic": {
                    "sessions": 50000,
                    "bounce_rate": 45.5,
                    "avg_session_duration": 180,
                    "conversions": 1500,
                    "conversion_rate": 3.0
                }
            }
        }


# Output Schemas

class ExecutiveSummary(BaseModel):
    """Executive summary section."""
    verdict: str = Field(description="Red/Yellow/Green or Pass/Fail")
    mer: float = Field(description="Marketing Efficiency Ratio")
    top_risks: List[str] = Field(max_length=3)
    top_wins: List[str] = Field(max_length=3)
    narrative: str


class MacroEnvironment(BaseModel):
    """Macro environment analysis section."""
    market_trends: str
    competitor_analysis: str
    share_of_voice_summary: str
    narrative: str


class StrategyBrandHealth(BaseModel):
    """Strategy and brand health section."""
    say_do_gap: str
    consistency_score: Optional[str] = None
    segmentation_validation: str
    narrative: str


class FinancialPerformance(BaseModel):
    """Financial performance section."""
    ltv_cac_ratio: float
    ltv_cac_assessment: str
    payback_period_months: float
    budget_utilization_pct: float
    narrative: str


class FunnelAnalysis(BaseModel):
    """Funnel analysis section."""
    top_funnel_health: str
    mid_funnel_health: str
    bottom_funnel_health: str
    narrative: str


class ChannelDeepDive(BaseModel):
    """Channel analysis section."""
    channel_summaries: List[Dict[str, Any]]
    top_performing_channel: str
    underperforming_channels: List[str]
    narrative: str


class OperationsTechStack(BaseModel):
    """Operations and tech stack section."""
    shelfware_report: List[Dict[str, Any]]
    data_hygiene_score: Optional[str] = None
    team_assessment: str
    narrative: str


class SWOTSynthesis(BaseModel):
    """SWOT synthesis section."""
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    narrative: str


class Roadmap(BaseModel):
    """Action roadmap section."""
    immediate_0_30_days: List[str]
    strategic_1_6_months: List[str]
    long_term_6_12_months: List[str]
    resource_requirements: str
    narrative: str


class MarketingAuditOutput(BaseModel):
    """Complete Marketing Audit Report output."""

    # Metadata
    report_title: str = "Marketing Audit Report"
    report_period: str
    generated_date: datetime = Field(default_factory=datetime.utcnow)

    # Sections
    executive_summary: ExecutiveSummary
    macro_environment: MacroEnvironment
    strategy_brand: StrategyBrandHealth
    financial_performance: FinancialPerformance
    funnel_analysis: FunnelAnalysis
    channel_deep_dive: ChannelDeepDive
    operations_tech: OperationsTechStack
    swot_synthesis: SWOTSynthesis
    roadmap: Roadmap

    # Validation
    validation_passed: bool = True
    validation_details: Optional[Dict[str, Any]] = None
