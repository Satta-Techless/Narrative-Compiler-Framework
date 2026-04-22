#!/usr/bin/env python
"""
Verification script for NCF installation.

Quick smoke test to verify that NCF is installed correctly
and basic functionality works.
"""
import sys
import os


def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def test_imports():
    """Test that NCF modules can be imported."""
    print_section("Testing Imports")

    try:
        import ncf
        print("✓ ncf package imported")
    except ImportError as e:
        print(f"✗ Failed to import ncf: {e}")
        return False

    try:
        from ncf.core.dag import NCFPipeline
        print("✓ NCFPipeline imported")
    except ImportError as e:
        print(f"✗ Failed to import NCFPipeline: {e}")
        return False

    try:
        from ncf.layers.feature import FeatureLayer
        print("✓ FeatureLayer imported")
    except ImportError as e:
        print(f"✗ Failed to import FeatureLayer: {e}")
        return False

    try:
        from ncf.layers.semantic import SemanticLayer
        print("✓ SemanticLayer imported")
    except ImportError as e:
        print(f"✗ Failed to import SemanticLayer: {e}")
        return False

    try:
        from ncf.layers.validation import ValidationLayer
        print("✓ ValidationLayer imported")
    except ImportError as e:
        print(f"✗ Failed to import ValidationLayer: {e}")
        return False

    return True


def test_feature_computation():
    """Test basic feature computation."""
    print_section("Testing Feature Computation")

    try:
        from ncf.layers.feature import compute_growth_rate, compute_ratio

        # Test growth rate
        growth = compute_growth_rate(120, 100)
        if growth == 20.0:
            print("✓ Growth rate computation works")
        else:
            print(f"✗ Growth rate incorrect: expected 20.0, got {growth}")
            return False

        # Test ratio
        ratio = compute_ratio(100, 25)
        if ratio == 4.0:
            print("✓ Ratio computation works")
        else:
            print(f"✗ Ratio incorrect: expected 4.0, got {ratio}")
            return False

        return True
    except Exception as e:
        print(f"✗ Feature computation failed: {e}")
        return False


def test_semantic_rules():
    """Test semantic rule evaluation."""
    print_section("Testing Semantic Rules")

    try:
        from ncf.layers.semantic import SemanticLayer, create_threshold_rule
        from ncf.core.node import NodeInput

        rule = create_threshold_rule(
            name="test",
            field="score",
            threshold=80,
            above_label="high",
            below_label="low",
            output_key="level"
        )

        layer = SemanticLayer()
        layer.add_rule(rule)

        result = layer.execute(NodeInput(data={"score": 90}))

        if result.data.get("level") == "high":
            print("✓ Semantic rule evaluation works")
            return True
        else:
            print(f"✗ Semantic rule failed: expected 'high', got {result.data.get('level')}")
            return False

    except Exception as e:
        print(f"✗ Semantic rule test failed: {e}")
        return False


def test_marketing_audit_skill():
    """Test marketing audit skill structure."""
    print_section("Testing Marketing Audit Skill")

    try:
        from ncf.skills.marketing_audit.features import MARKETING_AUDIT_FEATURES
        from ncf.skills.marketing_audit.sample_data import SAMPLE_MARKETING_DATA

        print(f"✓ Marketing audit has {len(MARKETING_AUDIT_FEATURES)} features")

        # Test one feature
        feature_name = list(MARKETING_AUDIT_FEATURES.keys())[0]
        feature_func = MARKETING_AUDIT_FEATURES[feature_name]
        result = feature_func(SAMPLE_MARKETING_DATA)

        print(f"✓ Feature '{feature_name}' executes successfully")
        return True

    except Exception as e:
        print(f"✗ Marketing audit test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pipeline_creation():
    """Test pipeline creation."""
    print_section("Testing Pipeline Creation")

    try:
        from ncf.core.dag import NCFPipeline
        from ncf.layers.feature import FeatureLayer

        pipeline = NCFPipeline(name="Test Pipeline")

        features = {
            "test_feature": lambda data: data.get("value", 0) * 2
        }

        layer = FeatureLayer(features=features)
        pipeline.add_node("test", layer)

        print("✓ Pipeline created successfully")
        return True

    except Exception as e:
        print(f"✗ Pipeline creation failed: {e}")
        return False


def check_api_keys():
    """Check for API keys (optional)."""
    print_section("Checking API Keys (Optional)")

    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if openai_key:
        print("✓ OPENAI_API_KEY found")
    else:
        print("ℹ OPENAI_API_KEY not set (optional)")

    if anthropic_key:
        print("✓ ANTHROPIC_API_KEY found")
    else:
        print("ℹ ANTHROPIC_API_KEY not set (optional)")

    if openai_key or anthropic_key:
        print("\n  You can run full demos with LLM generation!")
    else:
        print("\n  Set API keys to run full demos with LLM generation")
        print("  Dry-run mode works without API keys")


def main():
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("  NCF Installation Verification")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Feature Computation", test_feature_computation),
        ("Semantic Rules", test_semantic_rules),
        ("Marketing Audit Skill", test_marketing_audit_skill),
        ("Pipeline Creation", test_pipeline_creation),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Check API keys (informational only)
    check_api_keys()

    # Print summary
    print_section("Summary")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\n  Total: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n  🎉 All tests passed! NCF is ready to use.")
        print("\n  Next steps:")
        print("  - Run: python examples/marketing_audit_demo.py")
        print("  - Run tests: pytest tests/")
        print("  - Read: docs/README.md")
        return 0
    else:
        print("\n  ⚠️  Some tests failed. Please check the output above.")
        print("\n  Troubleshooting:")
        print("  - Ensure all dependencies are installed: pip install -e .")
        print("  - Check for import errors above")
        print("  - See CONTRIBUTING.md for setup instructions")
        return 1


if __name__ == "__main__":
    sys.exit(main())
