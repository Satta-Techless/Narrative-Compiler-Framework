"""
Narrative Compiler Framework (NCF)

A deterministic data-to-text architecture for enterprise document preparation.
Implements a 4-layer DAG to eliminate LLM hallucinations and ensure auditability.
"""

__version__ = "1.0.0"
__author__ = "Satta Abraham"
__license__ = "CC-BY-4.0"

from ncf.core.dag import NCFPipeline
from ncf.core.node import Node, NodeType
from ncf.core.orchestrator import Orchestrator
from ncf.layers.feature import FeatureLayer
from ncf.layers.semantic import SemanticLayer
from ncf.layers.llm_reader import LLMReader
from ncf.layers.llm_writer import LLMWriter
from ncf.layers.validation import ValidationLayer

__all__ = [
    "NCFPipeline",
    "Node",
    "NodeType",
    "Orchestrator",
    "FeatureLayer",
    "SemanticLayer",
    "LLMReader",
    "LLMWriter",
    "ValidationLayer",
]
