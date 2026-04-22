"""
Semantic Layer implementation.

Rule-based semantic classification using JSONLogic with hybrid extensibility.
"""
from typing import Dict, Any, Optional, List
from ncf.core.node import DeterministicNode, NodeType, NodeInput, NodeOutput
import json_logic


class SemanticRule:
    """A semantic classification rule."""

    def __init__(self, name: str, logic: Dict[str, Any], output_key: str):
        """
        Initialize a semantic rule.

        Args:
            name: Rule name
            logic: JSONLogic rule definition
            output_key: Key to store the result in output
        """
        self.name = name
        self.logic = logic
        self.output_key = output_key

    def evaluate(self, data: Dict[str, Any]) -> Any:
        """
        Evaluate the rule against data.

        Args:
            data: Data to evaluate

        Returns:
            Result of the rule evaluation
        """
        return json_logic.jsonLogic(self.logic, data)


class SemanticLayer(DeterministicNode):
    """
    Semantic Layer: Rule-based classification and tagging.

    Uses JSONLogic for deterministic semantic classification.
    Supports hybrid mode with knowledge graph integration.
    """

    def __init__(
        self,
        rules: Optional[List[SemanticRule]] = None,
        config: Optional[Dict[str, Any]] = None,
        knowledge_graph: Optional[Any] = None
    ):
        """
        Initialize the Semantic Layer.

        Args:
            rules: List of semantic rules
            config: Optional configuration
            knowledge_graph: Optional knowledge graph for hybrid mode
        """
        super().__init__(NodeType.SEMANTIC, config)
        self.rules = rules or []
        self.knowledge_graph = knowledge_graph
        self.classifications: Dict[str, Any] = {}

    def add_rule(self, rule: SemanticRule) -> None:
        """
        Add a semantic rule.

        Args:
            rule: Semantic rule to add
        """
        self.rules.append(rule)

    def add_simple_rule(
        self,
        name: str,
        condition: Dict[str, Any],
        true_value: Any,
        false_value: Any,
        output_key: str
    ) -> None:
        """
        Add a simple if-then-else rule.

        Args:
            name: Rule name
            condition: JSONLogic condition
            true_value: Value if condition is true
            false_value: Value if condition is false
            output_key: Output key for the result
        """
        logic = {
            "if": [
                condition,
                true_value,
                false_value
            ]
        }
        self.add_rule(SemanticRule(name, logic, output_key))

    def execute(self, input_data: NodeInput) -> NodeOutput:
        """
        Execute semantic classification.

        Args:
            input_data: Input data with features

        Returns:
            NodeOutput with semantic tags
        """
        data = input_data.data
        semantic_tags = {}

        # Evaluate each rule
        for rule in self.rules:
            try:
                result = rule.evaluate(data)
                semantic_tags[rule.output_key] = result

                # Track provenance
                if "provenance" not in self.metadata.provenance:
                    self.metadata.provenance = {}
                self.metadata.provenance[rule.output_key] = {
                    "rule": rule.name,
                    "logic": rule.logic
                }

            except Exception as e:
                semantic_tags[rule.output_key] = None
                self.metadata.provenance[rule.output_key] = {
                    "rule": rule.name,
                    "error": str(e)
                }

        # Query knowledge graph if available (hybrid mode)
        if self.knowledge_graph:
            kg_tags = self._query_knowledge_graph(data)
            semantic_tags.update(kg_tags)

        # Store classifications
        self.classifications = semantic_tags

        # Merge with input data
        output_data = {**data, **semantic_tags}

        return NodeOutput(
            data=output_data,
            metadata=self.metadata,
            provenance=self.metadata.provenance
        )

    def _query_knowledge_graph(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query knowledge graph for context-aware classifications.

        Args:
            data: Input data

        Returns:
            Dictionary of semantic tags from knowledge graph
        """
        # Placeholder for knowledge graph integration
        # Will be implemented in knowledge_graph/hybrid.py
        return {}

    def get_classification(self, key: str) -> Any:
        """
        Get a semantic classification.

        Args:
            key: Classification key

        Returns:
            Classification value or None
        """
        return self.classifications.get(key)


# Common semantic classification utilities

def create_threshold_rule(
    name: str,
    field: str,
    threshold: float,
    above_label: str,
    below_label: str,
    output_key: str
) -> SemanticRule:
    """
    Create a simple threshold-based rule.

    Args:
        name: Rule name
        field: Field to check
        threshold: Threshold value
        above_label: Label when value >= threshold
        below_label: Label when value < threshold
        output_key: Output key for result

    Returns:
        SemanticRule
    """
    logic = {
        "if": [
            {">=": [{"var": field}, threshold]},
            above_label,
            below_label
        ]
    }
    return SemanticRule(name, logic, output_key)


def create_range_rule(
    name: str,
    field: str,
    ranges: List[tuple],  # [(min, max, label), ...]
    output_key: str
) -> SemanticRule:
    """
    Create a multi-range classification rule.

    Args:
        name: Rule name
        field: Field to check
        ranges: List of (min, max, label) tuples
        output_key: Output key for result

    Returns:
        SemanticRule
    """
    # Build nested if-then-else logic
    conditions = []
    for min_val, max_val, label in ranges:
        condition = {
            "and": [
                {">=": [{"var": field}, min_val]},
                {"<": [{"var": field}, max_val]}
            ]
        }
        conditions.extend([condition, label])

    # Add default case
    conditions.append("unknown")

    logic = {"if": conditions}
    return SemanticRule(name, logic, output_key)


def create_composite_rule(
    name: str,
    conditions: List[Dict[str, Any]],
    operator: str,  # "and" or "or"
    true_value: Any,
    false_value: Any,
    output_key: str
) -> SemanticRule:
    """
    Create a composite rule combining multiple conditions.

    Args:
        name: Rule name
        conditions: List of JSONLogic conditions
        operator: "and" or "or"
        true_value: Value when conditions are met
        false_value: Value when conditions are not met
        output_key: Output key for result

    Returns:
        SemanticRule
    """
    logic = {
        "if": [
            {operator: conditions},
            true_value,
            false_value
        ]
    }
    return SemanticRule(name, logic, output_key)
