"""
Marketing Audit Report Demo

Complete end-to-end demonstration of the NCF Marketing Audit skill.
"""
import os
import json
from ncf.skills.marketing_audit.pipeline import create_marketing_audit_pipeline
from ncf.skills.marketing_audit.sample_data import SAMPLE_MARKETING_DATA, SAMPLE_STRUGGLING_DATA


def main():
    """Run the marketing audit demo."""

    print("=" * 70)
    print("NCF Marketing Audit Report Generator - Demo")
    print("=" * 70)

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: No API key found!")
        print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        print("\nRunning dry-run mode (no LLM calls)...\n")
        run_dry_run()
        return

    # Choose provider
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "anthropic"
    print(f"\n📊 Using provider: {provider}")

    # Create pipeline
    print("\n🏗️  Building NCF pipeline...")
    pipeline = create_marketing_audit_pipeline(provider=provider)

    # Visualize pipeline
    print("\n📈 Pipeline Architecture:")
    print(pipeline.visualize())

    # Choose scenario
    print("\n\n" + "=" * 70)
    print("Choose scenario:")
    print("  1. Healthy Company (strong metrics)")
    print("  2. Struggling Company (needs improvement)")
    choice = input("\nEnter choice (1 or 2, default=1): ").strip() or "1"

    data = SAMPLE_MARKETING_DATA if choice == "1" else SAMPLE_STRUGGLING_DATA

    # Show input summary
    print("\n📥 Input Data Summary:")
    print(f"  Report Period: {data['report_period']}")
    print(f"  Marketing Spend: ${data['financial']['marketing_spend']:,.2f}")
    print(f"  Revenue: ${data['financial']['revenue']:,.2f}")
    print(f"  LTV: ${data['financial']['ltv']}")
    print(f"  CAC: ${data['financial']['cac']}")
    print(f"  Channels: {len(data['channels'])}")

    # Generate report
    print("\n🔄 Generating report (this may take 30-60 seconds)...")
    try:
        result = pipeline.generate(data)

        print("\n✅ Report generated successfully!")

        # Show sections
        if "sections" in result:
            print("\n📝 Generated Sections:")
            for section_name, section_content in result["sections"].items():
                print(f"\n  [{section_name.upper()}]")
                # Show first 200 characters
                preview = section_content[:200] + "..." if len(section_content) > 200 else section_content
                print(f"  {preview}\n")

        # Show validation results
        if "validation" in result:
            validation = result["validation"]
            print("\n🔍 Validation Results:")
            print(f"  Total Checks: {validation['total_count']}")
            print(f"  Passed: {validation['passed_count']}")
            print(f"  Pass Rate: {validation['pass_rate']*100:.1f}%")
            print(f"  All Passed: {'✅ YES' if validation['all_passed'] else '❌ NO'}")

            if not validation['all_passed']:
                print("\n  Failed Validations:")
                for r in validation['results']:
                    if not r['passed']:
                        print(f"    - {r['rule']}: {r['message']}")

        # Save to file
        output_file = f"marketing_audit_{data['report_period'].replace(' ', '_')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        print(f"\n💾 Full report saved to: {output_file}")

        # Show provenance
        provenance = pipeline.get_provenance()
        print(f"\n🔗 Provenance: {provenance['total_nodes_executed']} nodes executed")
        print(f"   Execution sequence: {' → '.join(provenance['execution_sequence'])}")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)


def run_dry_run():
    """Run a dry run without LLM calls."""

    print("\n🔍 Dry Run Mode - Pipeline Structure Only\n")

    # Create pipeline without LLM provider (will fail on actual generation)
    try:
        pipeline = create_marketing_audit_pipeline(provider="openai")
    except:
        # If it fails due to no API key, that's expected in dry run
        from ncf.skills.marketing_audit.pipeline import MarketingAuditPipeline
        from ncf.utils.llm_provider import OpenAIProvider

        # Create with dummy provider
        dummy_provider = OpenAIProvider(api_key="dummy")
        pipeline = MarketingAuditPipeline(llm_provider=dummy_provider)

    # Visualize
    print(pipeline.visualize())

    # Show dry run results
    dry_run_result = pipeline.dry_run(SAMPLE_MARKETING_DATA)

    print("\n📊 Dry Run Results:")
    print(f"  Valid: {dry_run_result['valid']}")
    print(f"  Nodes: {dry_run_result['node_count']}")
    print(f"  Edges: {dry_run_result['edge_count']}")
    print(f"  Execution Order: {' → '.join(dry_run_result['execution_order'])}")

    if dry_run_result['errors']:
        print(f"\n  Errors: {dry_run_result['errors']}")

    print("\n💡 To run actual generation, set OPENAI_API_KEY or ANTHROPIC_API_KEY")


if __name__ == "__main__":
    main()
