"""
Node definitions for the NCF pipeline.

Defines the base node contracts and types used in the DAG architecture.
"""
from enum import Enum
from typing import Any, Dict, Optional, List
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class NodeType(str, Enum):
    """Types of nodes in the NCF pipeline."""
    INPUT = "input"
    FEATURE = "feature"
    SEMANTIC = "semantic"
    LLM_READER = "llm_reader"
    LLM_WRITER = "llm_writer"
    VALIDATION = "validation"
    OUTPUT = "output"


class NodeStatus(str, Enum):
    """Execution status of a node."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class NodeMetadata(BaseModel):
    """Metadata about a node's execution."""
    node_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    node_type: NodeType
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: NodeStatus = NodeStatus.PENDING
    execution_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)


class NodeInput(BaseModel):
    """Input data for a node."""
    data: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NodeOutput(BaseModel):
    """Output data from a node."""
    data: Dict[str, Any]
    metadata: NodeMetadata
    provenance: Dict[str, Any] = Field(default_factory=dict)


class Node(ABC):
    """
    Base class for all NCF pipeline nodes.

    Enforces the contract that all nodes must implement:
    - Deterministic computation (no LLM output flows back to deterministic nodes)
    - Provenance tracking
    - Metadata collection
    """

    def __init__(self, node_type: NodeType, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a node.

        Args:
            node_type: The type of this node
            config: Optional configuration dictionary
        """
        self.node_type = node_type
        self.config = config or {}
        self.metadata = NodeMetadata(node_type=node_type)

    @abstractmethod
    def execute(self, input_data: NodeInput) -> NodeOutput:
        """
        Execute this node's logic.

        Args:
            input_data: Input data with metadata

        Returns:
            NodeOutput with results and updated metadata
        """
        pass

    def validate_input(self, input_data: NodeInput) -> bool:
        """
        Validate input data before execution.

        Args:
            input_data: Input data to validate

        Returns:
            True if valid, False otherwise
        """
        return True

    def _start_execution(self):
        """Mark the start of execution."""
        self.metadata.started_at = datetime.utcnow()
        self.metadata.status = NodeStatus.RUNNING

    def _complete_execution(self, success: bool = True, error: Optional[str] = None):
        """Mark the completion of execution."""
        self.metadata.completed_at = datetime.utcnow()
        if self.metadata.started_at:
            delta = (self.metadata.completed_at - self.metadata.started_at).total_seconds() * 1000
            self.metadata.execution_time_ms = delta

        if success:
            self.metadata.status = NodeStatus.COMPLETED
        else:
            self.metadata.status = NodeStatus.FAILED
            self.metadata.error_message = error

    def run(self, input_data: NodeInput) -> NodeOutput:
        """
        Execute the node with error handling and metadata tracking.

        Args:
            input_data: Input data for the node

        Returns:
            NodeOutput with results

        Raises:
            Exception: If node execution fails
        """
        try:
            # Validate input
            if not self.validate_input(input_data):
                raise ValueError(f"Invalid input for {self.node_type} node")

            # Execute
            self._start_execution()
            output = self.execute(input_data)
            self._complete_execution(success=True)

            # Attach metadata
            output.metadata = self.metadata

            return output

        except Exception as e:
            self._complete_execution(success=False, error=str(e))
            raise


class DeterministicNode(Node):
    """
    Base class for deterministic nodes (Feature, Semantic).

    These nodes must NOT accept LLM-generated content as input.
    All computation must be reproducible.
    """

    def __init__(self, node_type: NodeType, config: Optional[Dict[str, Any]] = None):
        super().__init__(node_type, config)
        self.is_deterministic = True


class LLMNode(Node):
    """
    Base class for LLM-based nodes (LLM-Reader, LLM-Writer).

    These nodes interact with language models.
    """

    def __init__(self, node_type: NodeType, config: Optional[Dict[str, Any]] = None):
        super().__init__(node_type, config)
        self.is_deterministic = False
        self.model_provider: Optional[str] = None
        self.model_name: Optional[str] = None
