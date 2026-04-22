# Contributing to Narrative Compiler Framework

Thank you for your interest in contributing to NCF! This guide will help you get started.

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/Narrative-Compiler-Framework.git
cd Narrative-Compiler-Framework
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e ".[dev]"
```

This installs the package in editable mode along with development dependencies.

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src/ncf tests/

# Run specific test file
pytest tests/test_feature_layer.py

# Run with verbose output
pytest -v tests/
```

### Code Style

We use automated formatters and linters:

```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type check with mypy
mypy src/
```

### Before Submitting

1. **Write Tests**: Add tests for new features
2. **Run Tests**: Ensure all tests pass
3. **Format Code**: Run black and ruff
4. **Update Documentation**: Update README or docs if needed

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Keep changes focused and atomic
- Write clear commit messages
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
pytest tests/
```

### 4. Submit Pull Request

- Push your branch to your fork
- Open a PR against the main repository
- Describe your changes clearly
- Reference any related issues

## Code Style Guidelines

### Python Code

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for public functions and classes
- Keep functions focused and single-purpose

### Docstring Format

```python
def compute_ratio(numerator: float, denominator: float) -> Optional[float]:
    """
    Compute ratio of numerator to denominator.

    Args:
        numerator: The numerator value
        denominator: The denominator value

    Returns:
        The ratio, or None if denominator is zero
    """
    if denominator == 0:
        return None
    return numerator / denominator
```

### Test Naming

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

## Areas to Contribute

### Good First Issues

- Add more validation rules
- Improve error messages
- Add more feature computations
- Improve documentation

### Feature Areas

1. **Core Framework**
   - Enhance DAG validation
   - Improve provenance tracking
   - Add more node types

2. **Skills**
   - Create new skills
   - Improve marketing audit skill
   - Add more example data

3. **Testing**
   - Increase test coverage
   - Add integration tests
   - Add performance benchmarks

4. **Documentation**
   - Improve API documentation
   - Add tutorials
   - Create video guides

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for general questions
- Check existing issues before creating new ones

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the golden rule

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
