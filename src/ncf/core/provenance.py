"""
Provenance tracking for NCF pipelines.

Tracks the full lineage of data through the pipeline to ensure auditability.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from ncf.core.node import NodeType


class ProvenanceRecord(BaseModel):
    """A single provenance record for a node execution."""
    node_id: str
    node_type: NodeType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    input_keys: List[str]
    output_keys: List[str]
    input_hash: Optional[str] = None
    output_hash: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProvenanceTracker:
    """
    Tracks provenance through the NCF pipeline.

    Maintains a complete audit trail of:
    - What data entered each node
    - What data was produced by each node
    - When each node executed
    - Lineage chains showing data flow
    """

    def __init__(self):
        """Initialize the provenance tracker."""
        self.records: List[ProvenanceRecord] = []
        self.lineage: Dict[str, List[str]] = {}  # node_id -> list of source node_ids

    def record_execution(
        self,
        node_id: str,
        node_type: NodeType,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record the execution of a node.

        Args:
            node_id: Identifier of the node
            node_type: Type of the node
            input_data: Input data dictionary
            output_data: Output data dictionary
            metadata: Optional metadata about the execution
        """
        record = ProvenanceRecord(
            node_id=node_id,
            node_type=node_type,
            input_keys=list(input_data.keys()),
            output_keys=list(output_data.keys()),
            input_hash=self._hash_dict(input_data),
            output_hash=self._hash_dict(output_data),
            metadata=metadata or {}
        )

        self.records.append(record)

    def add_lineage(self, node_id: str, source_nodes: List[str]) -> None:
        """
        Record the lineage relationship.

        Args:
            node_id: The node
            source_nodes: List of nodes that provided input to this node
        """
        self.lineage[node_id] = source_nodes

    def get_lineage_chain(self, node_id: str) -> List[str]:
        """
        Get the full lineage chain for a node.

        Args:
            node_id: Node to get lineage for

        Returns:
            List of node IDs in lineage order
        """
        chain = []
        self._build_lineage_chain(node_id, chain, set())
        return list(reversed(chain))

    def _build_lineage_chain(
        self,
        node_id: str,
        chain: List[str],
        visited: set
    ) -> None:
        """Recursively build lineage chain."""
        if node_id in visited:
            return

        visited.add(node_id)
        chain.append(node_id)

        if node_id in self.lineage:
            for source in self.lineage[node_id]:
                self._build_lineage_chain(source, chain, visited)

    def get_record(self, node_id: str) -> Optional[ProvenanceRecord]:
        """
        Get the provenance record for a specific node.

        Args:
            node_id: Node to get record for

        Returns:
            ProvenanceRecord if found, None otherwise
        """
        for record in self.records:
            if record.node_id == node_id:
                return record
        return None

    def get_full_trace(self) -> Dict[str, Any]:
        """
        Get the complete provenance trace.

        Returns:
            Dictionary containing all provenance information
        """
        return {
            "records": [record.dict() for record in self.records],
            "lineage": self.lineage,
            "total_nodes_executed": len(self.records),
            "execution_sequence": [record.node_id for record in self.records]
        }

    def export_to_json(self) -> str:
        """
        Export provenance to JSON format.

        Returns:
            JSON string representation
        """
        import json
        return json.dumps(self.get_full_trace(), indent=2, default=str)

    def verify_chain(self, node_id: str) -> bool:
        """
        Verify that a complete provenance chain exists for a node.

        Args:
            node_id: Node to verify

        Returns:
            True if chain is complete, False otherwise
        """
        record = self.get_record(node_id)
        if not record:
            return False

        # Check that all upstream nodes have records
        chain = self.get_lineage_chain(node_id)
        for upstream_node in chain:
            if not self.get_record(upstream_node):
                return False

        return True

    @staticmethod
    def _hash_dict(data: Dict[str, Any]) -> str:
        """
        Create a hash of a dictionary for provenance tracking.

        Args:
            data: Dictionary to hash

        Returns:
            Hash string
        """
        import hashlib
        import json

        # Create a stable JSON representation
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]
