"""
Feature Layer implementation.

Deterministic computation of derived features from input data.
"""
from typing import Dict, Any, Callable, List, Optional
from ncf.core.node import DeterministicNode, NodeType, NodeInput, NodeOutput
import pandas as pd


class FeatureComputation(Callable):
    """A feature computation function."""
    pass


class FeatureLayer(DeterministicNode):
    """
    Feature Layer: Deterministic feature computation.

    Computes derived quantities like growth rates, ratios, flags, etc.
    All computations are pure functions - same input always produces same output.
    Results are cached for efficiency.
    """

    def __init__(self, features: Optional[Dict[str, Callable]] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Feature Layer.

        Args:
            features: Dictionary of feature_name -> computation_function
            config: Optional configuration
        """
        super().__init__(NodeType.FEATURE, config)
        self.features = features or {}
        self.cache: Dict[str, Any] = {}

    def add_feature(self, name: str, computation: Callable[[Dict[str, Any]], Any]) -> None:
        """
        Add a feature computation.

        Args:
            name: Feature name
            computation: Function that takes input data and returns computed value
        """
        self.features[name] = computation

    def execute(self, input_data: NodeInput) -> NodeOutput:
        """
        Execute feature computations.

        Args:
            input_data: Input data

        Returns:
            NodeOutput with computed features
        """
        data = input_data.data
        computed_features = {}

        # Compute each feature
        for feature_name, computation in self.features.items():
            try:
                value = computation(data)
                computed_features[feature_name] = value

                # Track provenance
                if "provenance" not in self.metadata.provenance:
                    self.metadata.provenance = {}
                self.metadata.provenance[feature_name] = {
                    "source": "computed",
                    "function": computation.__name__ if hasattr(computation, "__name__") else str(computation)
                }

            except Exception as e:
                # Log error but continue with other features
                computed_features[feature_name] = None
                self.metadata.provenance[feature_name] = {
                    "error": str(e)
                }

        # Merge with input data
        output_data = {**data, **computed_features}

        # Cache results
        self.cache = computed_features

        return NodeOutput(
            data=output_data,
            metadata=self.metadata,
            provenance=self.metadata.provenance
        )

    def get_feature(self, name: str) -> Any:
        """
        Get a computed feature from cache.

        Args:
            name: Feature name

        Returns:
            Feature value or None if not found
        """
        return self.cache.get(name)


# Common feature computation utilities

def compute_growth_rate(current: float, previous: float) -> Optional[float]:
    """Compute percentage growth rate."""
    if previous == 0 or previous is None or current is None:
        return None
    return ((current - previous) / previous) * 100


def compute_ratio(numerator: float, denominator: float) -> Optional[float]:
    """Compute a ratio safely."""
    if denominator == 0 or denominator is None or numerator is None:
        return None
    return numerator / denominator


def compute_percentage(part: float, whole: float) -> Optional[float]:
    """Compute percentage."""
    if whole == 0 or whole is None or part is None:
        return None
    return (part / whole) * 100


def categorize_value(
    value: float,
    thresholds: Dict[str, float],
    ascending: bool = True
) -> Optional[str]:
    """
    Categorize a numeric value based on thresholds.

    Args:
        value: Value to categorize
        thresholds: Dict of category_name -> threshold_value
        ascending: If True, higher values get higher categories

    Returns:
        Category name or None
    """
    if value is None:
        return None

    sorted_thresholds = sorted(thresholds.items(), key=lambda x: x[1], reverse=not ascending)

    for category, threshold in sorted_thresholds:
        if ascending and value >= threshold:
            return category
        elif not ascending and value <= threshold:
            return category

    # Return first category if no threshold matched
    return sorted_thresholds[-1][0] if sorted_thresholds else None


def aggregate_series(
    data: List[float],
    aggregation: str = "mean"
) -> Optional[float]:
    """
    Aggregate a series of values.

    Args:
        data: List of values
        aggregation: Type of aggregation (mean, sum, min, max, median)

    Returns:
        Aggregated value
    """
    if not data:
        return None

    clean_data = [x for x in data if x is not None]
    if not clean_data:
        return None

    if aggregation == "mean":
        return sum(clean_data) / len(clean_data)
    elif aggregation == "sum":
        return sum(clean_data)
    elif aggregation == "min":
        return min(clean_data)
    elif aggregation == "max":
        return max(clean_data)
    elif aggregation == "median":
        sorted_data = sorted(clean_data)
        n = len(sorted_data)
        if n % 2 == 0:
            return (sorted_data[n//2-1] + sorted_data[n//2]) / 2
        else:
            return sorted_data[n//2]
    else:
        raise ValueError(f"Unknown aggregation: {aggregation}")
