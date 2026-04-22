# Sample Outputs

This directory contains example outputs from the NCF Marketing Audit skill.

## Files

### `sample_healthy_company.json`

Example output for a company with strong metrics:
- LTV:CAC ratio: 3.0 (healthy)
- MER: 5.0 (excellent)
- Revenue growth: 20% (strong)
- **Validation: ✓ All passed**

This demonstrates successful end-to-end generation with all validation checks passing.

### `sample_struggling_company.json`

Example output for a company facing challenges:
- LTV:CAC ratio: 0.8 (critical)
- MER: 1.2 (poor)
- Revenue growth: -15% (declining)
- **Validation: ✓ All passed**

Even negative metrics are accurately reported and validated.

### `sample_validation_failure.json`

**Critical example**: Demonstrates validation catching LLM errors:
- LLM generated: LTV:CAC = 4.0
- Actual computed: LTV:CAC = 3.0
- **Validation: ✗ Failed (3/15 checks)**

This shows NCF's validation layer working as designed:
1. Features are computed deterministically (3.0)
2. LLM generates text with incorrect number (4.0)
3. Validation catches the discrepancy
4. User is alerted to review the output

## What These Examples Show

### Transparency

All three examples include:
- Computed features (deterministic)
- Semantic classifications (rule-based)
- Generated text sections (LLM output)
- Validation results (automated checks)
- Provenance (available separately via `pipeline.get_provenance()`, not embedded in the report JSON)

### Validation Works

The `sample_validation_failure.json` file is particularly important:
- **Proves validation is real**: Not just a checkbox
- **Shows error detection**: Catches hallucinations
- **Demonstrates auditability**: Clear what went wrong

### Honest Representation

We include both:
- ✓ Successful generation (most common case)
- ✗ Failed validation (catches errors)

This honesty builds trust in the framework.

## Generating Your Own

To generate real outputs:

```bash
# Set API key
export OPENAI_API_KEY="your-key"

# Run demo
python examples/marketing_audit_demo.py

# Output saved to: marketing_audit_Q4_2025.json
```

## Understanding the Structure

Each output file contains:

1. **sections**: Generated narrative text
2. **validation**: Automated validation results
3. **features**: Computed numeric values
4. **semantic_tags**: Rule-based classifications
5. **provenance**: Execution trace
6. **metadata**: Generation details

This structure ensures:
- Full transparency
- Easy debugging
- Clear audit trail
- Reproducibility

## Questions?

See the main [README](../../README.md) for more information about NCF's architecture and validation approach.
