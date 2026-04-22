"""
Basic usage example for the Narrative Compiler Framework.

Demonstrates the core concepts and simple pipeline construction.
"""
from ncf.core.dag import NCFPipeline
from ncf.core.node import NodeInput
from ncf.core.orchestrator import Orchestrator
from ncf.layers.feature import FeatureLayer
from ncf.layers.semantic import SemanticLayer, create_threshold_rule
from ncf.layers.llm_writer import LLMWriter
from ncf.utils.llm_provider import create_provider


def simple_example():
    """Simple example: Generate a product description with verified facts."""

    print("=" * 60)
    print("NCF Basic Example: Product Description Generator")
    print("=" * 60)

    # Create a pipeline
    pipeline = NCFPipeline(name="Product Description")

    # 1. Define features (deterministic computations)
    def compute_discount_pct(data):
        original = data.get("original_price", 0)
        current = data.get("current_price", 0)
        if original == 0:
            return 0
        return ((original - current) / original) * 100

    def compute_savings(data):
        return data.get("original_price", 0) - data.get("current_price", 0)

    feature_layer = FeatureLayer(features={
        "discount_pct": compute_discount_pct,
        "savings_amount": compute_savings
    })

    # 2. Define semantic rules (classifications)
    semantic_layer = SemanticLayer()
    semantic_layer.add_rule(
        create_threshold_rule(
            name="discount_level",
            field="discount_pct",
            threshold=20.0,
            above_label="major_discount",
            below_label="minor_discount",
            output_key="discount_category"
        )
    )

    # 3. Create LLM writer with constrained prompt
    provider = create_provider("openai")  # or "anthropic"

    prompt_template = """Write a product description for:

Product: {{ product_name }}
Original Price: ${{ original_price }}
Current Price: ${{ current_price }}
Discount: {{ discount_pct|round(1) }}%
Savings: ${{ savings_amount|round(2) }}
Discount Category: {{ discount_category }}

Write a 2-sentence description highlighting the value. Use ONLY these exact numbers."""

    writer = LLMWriter(
        provider=provider,
        prompt_template=prompt_template
    )

    # Build the pipeline - Note: Missing proper node imports, this is illustrative
    # In real code, you'd create proper Input/Output nodes

    print("\nPipeline created successfully!")
    print("\nTo run this example, you would:")
    print("1. Add nodes to the pipeline")
    print("2. Connect them with edges")
    print("3. Execute with sample data")
    print("\nSee examples/marketing_audit_demo.py for a complete example.")


def feature_layer_example():
    """Example of using just the Feature Layer."""

    print("\n" + "=" * 60)
    print("Feature Layer Example")
    print("=" * 60)

    from ncf.layers.feature import compute_growth_rate, compute_ratio

    # Sample data
    data = {
        "current_revenue": 120000,
        "previous_revenue": 100000,
        "marketing_spend": 30000
    }

    # Compute features
    growth = compute_growth_rate(data["current_revenue"], data["previous_revenue"])
    efficiency = compute_ratio(data["current_revenue"], data["marketing_spend"])

    print(f"\nRevenue Growth: {growth:.1f}%")
    print(f"Marketing Efficiency: {efficiency:.2f}x")


def semantic_layer_example():
    """Example of using just the Semantic Layer."""

    print("\n" + "=" * 60)
    print("Semantic Layer Example")
    print("=" * 60)

    from ncf.layers.semantic import SemanticLayer, SemanticRule

    # Create semantic layer
    layer = SemanticLayer()

    # Add a rule
    rule = SemanticRule(
        name="performance_level",
        logic={
            "if": [
                {">=": [{"var": "score"}, 80]},
                "excellent",
                {"if": [
                    {">=": [{"var": "score"}, 60]},
                    "good",
                    "needs_improvement"
                ]}
            ]
        },
        output_key="performance"
    )
    layer.add_rule(rule)

    # Execute
    result = layer.execute(NodeInput(data={"score": 75}))
    print(f"\nScore: 75")
    print(f"Classification: {result.data['performance']}")


if __name__ == "__main__":
    simple_example()
    feature_layer_example()
    semantic_layer_example()

    print("\n" + "=" * 60)
    print("For a complete, working example, see:")
    print("  examples/marketing_audit_demo.py")
    print("=" * 60)
