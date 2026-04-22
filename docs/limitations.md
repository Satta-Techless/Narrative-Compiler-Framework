# NCF Limitations

This document describes the known limitations and constraints of the Narrative Compiler Framework.

## Scope Limitations

### Best Use Cases

NCF is optimized for:
- **Structured reports** with clear data sources
- **Data-driven documents** with numeric facts
- **Automated audits** and summaries
- **Templated content** with variable data

### Not Ideal For

NCF is **not** well-suited for:
- Creative writing or storytelling
- Open-ended content generation
- Documents without clear data sources
- Highly variable document structures

## Technical Limitations

### 1. Validation Coverage

**Limitation**: Validation is only as good as the rules you define.

- Validation rules must be explicitly written
- Unchecked facts may still be inaccurate
- Text patterns can be brittle
- New data types require new validation rules

**Mitigation**:
- Start with comprehensive validation rules
- Test validation with incorrect data
- Gradually expand rule coverage
- Use domain experts to define rules

### 2. Schema Definition Required

**Limitation**: Requires upfront schema and feature definition.

- Cannot handle arbitrary input structures
- Schema changes require code updates
- Feature functions must be pre-written
- Not suitable for ad-hoc document generation

**Mitigation**:
- Use flexible schemas where possible
- Build reusable feature libraries
- Plan schema changes carefully
- Consider meta-NCF for dynamic skills

### 3. LLM Quality Dependency

**Limitation**: Output fluency depends on underlying LLM.

- Poor LLM = poor output quality
- Constraints don't fix grammar issues
- Coherence is not guaranteed
- Style consistency varies by LLM

**Mitigation**:
- Use high-quality LLMs (GPT-4, Claude)
- Provide clear, detailed prompts
- Test with multiple providers
- Use few-shot examples in prompts

### 4. Deterministic Computation Overhead

**Limitation**: Requires writing deterministic feature functions.

- More upfront development work
- Functions must handle edge cases
- Complex computations need testing
- Maintenance overhead for features

**Mitigation**:
- Build reusable feature libraries
- Use comprehensive unit tests
- Document feature assumptions
- Share features across skills

### 5. Not a Formal Compiler

**Limitation**: Despite the name, NCF is not a formal compiler.

- No formal correctness proofs
- No guaranteed output properties
- Validation can have false positives/negatives
- LLM behavior is non-deterministic

**Reality Check**:
- NCF reduces risk, doesn't eliminate it
- Validation improves accuracy, doesn't perfect it
- Human review may still be needed
- Best viewed as "constrained generation"

## Performance Limitations

### 1. Token Usage

**Limitation**: Complex documents require many tokens.

- Longer prompts = higher costs
- Multiple sections = multiple calls
- Rich context = more tokens
- Validation text increases cost

**Mitigation**:
- Cache deterministic computations
- Use efficient prompt templates
- Batch similar sections
- Monitor token usage

### 2. Latency

**Limitation**: Sequential LLM calls add latency.

- Each section requires API call
- Network latency multiplies
- No true parallelization of LLM calls
- Validation adds processing time

**Mitigation**:
- Parallelize where possible
- Use faster models for simple sections
- Consider async API calls
- Cache common outputs

## Data Quality Dependencies

### 1. Garbage In, Garbage Out

**Limitation**: Output quality depends on input data quality.

- Bad data = bad outputs
- Missing data causes errors
- Incorrect data passes validation
- Data freshness affects accuracy

**Mitigation**:
- Validate input data
- Check data sources
- Handle missing values gracefully
- Document data assumptions

### 2. Data Source Integration

**Limitation**: Requires reliable data sources.

- API failures affect generation
- Data format changes break pipelines
- Authentication issues block execution
- Rate limits constrain throughput

**Mitigation**:
- Use robust adapters
- Implement retry logic
- Cache data where appropriate
- Monitor data source health

## Scalability Limitations

### 1. Not Real-Time

**Limitation**: Not suitable for real-time generation.

- LLM calls take seconds
- Complex documents take minutes
- No streaming support
- Not interactive

**Use Cases**:
- Batch report generation ✓
- Scheduled document updates ✓
- Real-time chat ✗
- Interactive editing ✗

### 2. Cost at Scale

**Limitation**: Costs scale with document complexity and volume.

- Each document costs tokens
- Complex documents cost more
- High volume = high costs
- No built-in cost optimization

**Mitigation**:
- Use caching aggressively
- Choose appropriate LLM tiers
- Batch similar documents
- Monitor and optimize costs

## What NCF is NOT

To set proper expectations:

### NOT a General-Purpose LLM

NCF is **not**:
- A replacement for ChatGPT/Claude
- A general question-answering system
- A conversational agent
- A creative writing tool

### NOT Hallucination-Proof

NCF **reduces** hallucination risk but doesn't **eliminate** it:
- LLM can still generate incorrect text
- Validation catches known patterns, not all errors
- Novel content can't be validated
- Human review may still be needed

### NOT Zero-Configuration

NCF **requires**:
- Schema definition
- Feature function writing
- Semantic rule creation
- Validation rule implementation
- Testing and iteration

### NOT Production-Ready Out-of-the-Box

To use in production:
- Add comprehensive tests
- Implement error handling
- Set up monitoring
- Plan for failures
- Build operational runbooks

## Future Improvements

Areas we're working to improve:

1. **Better Validation**: More sophisticated validation techniques
2. **Easier Setup**: Tools to generate schemas and features
3. **Performance**: Caching and parallelization improvements
4. **Documentation**: More examples and guides
5. **Testing**: Better testing utilities and fixtures

## Questions?

If you encounter limitations not listed here, please:
- Open an issue
- Start a discussion
- Contribute documentation

We're continuously working to improve NCF and appreciate feedback on real-world usage.
