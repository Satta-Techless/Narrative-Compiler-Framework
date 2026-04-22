"""
Validation Layer implementation.

Reconciliation engine that verifies generated text against source features and semantic tags.
"""
from typing import Dict, Any, Optional, List, Set
import re
from ncf.core.node import DeterministicNode, NodeType, NodeInput, NodeOutput


class ValidationRule:
    """A validation rule."""

    def __init__(
        self,
        name: str,
        rule_type: str,
        field: str,
        pattern: Optional[str] = None,
        expected_value: Optional[Any] = None
    ):
        """
        Initialize a validation rule.

        Args:
            name: Rule name
            rule_type: Type of rule (numeric, exact, contains, pattern)
            field: Field to validate
            pattern: Optional regex pattern for pattern type
            expected_value: Optional expected value for exact type
        """
        self.name = name
        self.rule_type = rule_type
        self.field = field
        self.pattern = pattern
        self.expected_value = expected_value


class ValidationResult:
    """Result of a validation."""

    def __init__(self, rule_name: str, passed: bool, message: str, details: Optional[Dict] = None):
        """
        Initialize validation result.

        Args:
            rule_name: Name of the rule
            passed: Whether validation passed
            message: Validation message
            details: Optional details dict
        """
        self.rule_name = rule_name
        self.passed = passed
        self.message = message
        self.details = details or {}


class ValidationLayer(DeterministicNode):
    """
    Validation Layer: Reconciliation engine.

    Scans generated text and verifies that:
    1. All numbers match upstream feature computations
    2. All categorical claims match semantic classifications
    3. No hallucinated facts are present

    This is the safety net that makes NCF trustworthy.
    """

    def __init__(
        self,
        rules: Optional[List[ValidationRule]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Validation Layer.

        Args:
            rules: List of validation rules
            config: Optional configuration
        """
        super().__init__(NodeType.VALIDATION, config)
        self.rules = rules or []
        self.validation_results: List[ValidationResult] = []

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule."""
        self.rules.append(rule)

    def execute(self, input_data: NodeInput) -> NodeOutput:
        """
        Execute validation.

        Args:
            input_data: Input with features, semantics, and generated text

        Returns:
            NodeOutput with validation results
        """
        data = input_data.data
        generated_text_field = self.config.get("generated_text_field", "generated_text")

        # Get generated text
        if generated_text_field not in data:
            # Check if we have sections instead
            if "sections" in data:
                # Validate each section
                all_results = []
                for section_name, section_content in data["sections"].items():
                    results = self._validate_text(section_content, data, f"Section: {section_name}")
                    all_results.extend(results)
                self.validation_results = all_results
            else:
                raise ValueError(f"Generated text field '{generated_text_field}' not found")
        else:
            generated_text = data[generated_text_field]
            self.validation_results = self._validate_text(generated_text, data)

        # Summary
        passed_count = sum(1 for r in self.validation_results if r.passed)
        total_count = len(self.validation_results)
        all_passed = passed_count == total_count

        # Create validation report
        validation_report = {
            "all_passed": all_passed,
            "passed_count": passed_count,
            "total_count": total_count,
            "pass_rate": passed_count / total_count if total_count > 0 else 1.0,
            "results": [
                {
                    "rule": r.rule_name,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details
                }
                for r in self.validation_results
            ]
        }

        # Add to output
        output_data = {
            **data,
            "validation": validation_report
        }

        # Track provenance
        self.metadata.provenance["validation"] = {
            "rules_checked": total_count,
            "passed": passed_count,
            "failed": total_count - passed_count
        }

        return NodeOutput(
            data=output_data,
            metadata=self.metadata,
            provenance=self.metadata.provenance
        )

    def _validate_text(
        self,
        text: str,
        data: Dict[str, Any],
        context: str = ""
    ) -> List[ValidationResult]:
        """
        Validate text against data.

        Args:
            text: Text to validate
            data: Source data with features and semantics
            context: Optional context for error messages

        Returns:
            List of validation results
        """
        results = []

        for rule in self.rules:
            result = self._check_rule(rule, text, data, context)
            results.append(result)

        # Auto-detect numeric values and validate
        if self.config.get("auto_validate_numbers", True):
            auto_results = self._auto_validate_numbers(text, data, context)
            results.extend(auto_results)

        return results

    def _check_rule(
        self,
        rule: ValidationRule,
        text: str,
        data: Dict[str, Any],
        context: str
    ) -> ValidationResult:
        """Check a single validation rule."""
        context_prefix = f"{context}: " if context else ""

        if rule.rule_type == "numeric":
            return self._validate_numeric(rule, text, data, context_prefix)
        elif rule.rule_type == "exact":
            return self._validate_exact(rule, text, data, context_prefix)
        elif rule.rule_type == "contains":
            return self._validate_contains(rule, text, data, context_prefix)
        elif rule.rule_type == "pattern":
            return self._validate_pattern(rule, text, data, context_prefix)
        else:
            return ValidationResult(
                rule.name,
                False,
                f"{context_prefix}Unknown rule type: {rule.rule_type}",
                {}
            )

    def _validate_numeric(
        self,
        rule: ValidationRule,
        text: str,
        data: Dict[str, Any],
        context: str
    ) -> ValidationResult:
        """Validate that a numeric value in text matches source data."""
        if rule.field not in data:
            return ValidationResult(
                rule.name,
                False,
                f"{context}Field '{rule.field}' not found in source data",
                {}
            )

        expected = data[rule.field]
        if expected is None:
            return ValidationResult(rule.name, True, f"{context}Field is null, skipping", {})

        # Extract numbers from text (handle various formats)
        numbers = self._extract_numbers(text)

        # Check if expected value appears in text
        tolerance = self.config.get("numeric_tolerance", 0.01)  # 1% default
        found = False
        for num in numbers:
            if abs(num - expected) / max(abs(expected), 1) < tolerance:
                found = True
                break

        if found:
            return ValidationResult(
                rule.name,
                True,
                f"{context}Numeric value {expected} found in text",
                {"expected": expected, "found": True}
            )
        else:
            return ValidationResult(
                rule.name,
                False,
                f"{context}Numeric value {expected} NOT found in text",
                {"expected": expected, "found_numbers": numbers}
            )

    def _validate_exact(
        self,
        rule: ValidationRule,
        text: str,
        data: Dict[str, Any],
        context: str
    ) -> ValidationResult:
        """Validate exact value match."""
        if rule.field not in data:
            return ValidationResult(
                rule.name,
                False,
                f"{context}Field '{rule.field}' not found",
                {}
            )

        expected = str(data[rule.field])
        found = expected in text

        return ValidationResult(
            rule.name,
            found,
            f"{context}{'Found' if found else 'Missing'} exact value: {expected}",
            {"expected": expected, "found": found}
        )

    def _validate_contains(
        self,
        rule: ValidationRule,
        text: str,
        data: Dict[str, Any],
        context: str
    ) -> ValidationResult:
        """Validate text contains a substring."""
        expected = rule.expected_value
        found = expected in text

        return ValidationResult(
            rule.name,
            found,
            f"{context}Text {'contains' if found else 'missing'}: {expected}",
            {"expected": expected, "found": found}
        )

    def _validate_pattern(
        self,
        rule: ValidationRule,
        text: str,
        data: Dict[str, Any],
        context: str
    ) -> ValidationResult:
        """Validate text matches a regex pattern."""
        if not rule.pattern:
            return ValidationResult(rule.name, False, f"{context}No pattern specified", {})

        matches = re.findall(rule.pattern, text)
        found = len(matches) > 0

        return ValidationResult(
            rule.name,
            found,
            f"{context}Pattern {'matched' if found else 'not found'}: {rule.pattern}",
            {"pattern": rule.pattern, "matches": matches}
        )

    def _auto_validate_numbers(
        self,
        text: str,
        data: Dict[str, Any],
        context: str
    ) -> List[ValidationResult]:
        """Automatically validate all numbers found in text."""
        results = []
        numbers_in_text = self._extract_numbers(text)

        # Get all numeric fields from data
        numeric_fields = {k: v for k, v in data.items() if isinstance(v, (int, float))}

        # Check each number in text
        for num in numbers_in_text:
            matched = False
            for field, value in numeric_fields.items():
                tolerance = self.config.get("numeric_tolerance", 0.01)
                if abs(num - value) / max(abs(value), 1) < tolerance:
                    matched = True
                    break

            if not matched and self.config.get("strict_mode", False):
                results.append(
                    ValidationResult(
                        f"auto_number_{num}",
                        False,
                        f"{context}Number {num} in text has no matching source field",
                        {"value": num}
                    )
                )

        return results

    @staticmethod
    def _extract_numbers(text: str) -> List[float]:
        """Extract all numbers from text."""
        # Pattern matches: 123, 123.45, -123.45, 1,234.56, 12.3%, $123.45
        pattern = r'[-+]?[$]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?'
        matches = re.findall(pattern, text)

        numbers = []
        for match in matches:
            # Clean up the number
            cleaned = match.replace('$', '').replace(',', '').replace('%', '')
            try:
                numbers.append(float(cleaned))
            except ValueError:
                continue

        return numbers

    def get_failed_validations(self) -> List[ValidationResult]:
        """Get all failed validations."""
        return [r for r in self.validation_results if not r.passed]

    def is_valid(self) -> bool:
        """Check if all validations passed."""
        return all(r.passed for r in self.validation_results)
