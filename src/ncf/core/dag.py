"""
DAG (Directed Acyclic Graph) pipeline implementation.

Manages the flow of data through the NCF architecture ensuring:
1. Acyclicity - No feedback loops
2. No LLM output flows back to deterministic nodes
3. Full provenance tracking
"""
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
import networkx as nx
from ncf.core.node import Node, NodeType, NodeInput, NodeOutput, DeterministicNode


class Edge(BaseModel):
    """Represents a directed edge in the DAG."""
    from_node: str
    to_node: str
    label: Optional[str] = None


class NCFPipeline:
    """
    The core NCF pipeline implemented as a DAG.

    Enforces architectural invariants:
    - Acyclic graph structure
    - Type-safe edges (LLM output cannot flow to deterministic nodes)
    - Provenance tracking through all nodes
    """

    def __init__(self, name: str = "NCF Pipeline"):
        """
        Initialize the pipeline.

        Args:
            name: Pipeline name for identification
        """
        self.name = name
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, Node] = {}
        self.execution_history: List[Dict[str, Any]] = []

    def add_node(self, node_id: str, node: Node) -> None:
        """
        Add a node to the pipeline.

        Args:
            node_id: Unique identifier for the node
            node: The node instance to add
        """
        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already exists in pipeline")

        self.nodes[node_id] = node
        self.graph.add_node(node_id, node_type=node.node_type)

    def add_edge(self, from_node: str, to_node: str, label: Optional[str] = None) -> None:
        """
        Add an edge between two nodes.

        Args:
            from_node: Source node ID
            to_node: Destination node ID
            label: Optional edge label

        Raises:
            ValueError: If edge would violate architectural constraints
        """
        if from_node not in self.nodes:
            raise ValueError(f"Source node {from_node} not found")
        if to_node not in self.nodes:
            raise ValueError(f"Destination node {to_node} not found")

        # Check for cycles
        self.graph.add_edge(from_node, to_node, label=label)
        if not nx.is_directed_acyclic_graph(self.graph):
            self.graph.remove_edge(from_node, to_node)
            raise ValueError(f"Adding edge {from_node} -> {to_node} would create a cycle")

        # Enforce: LLM output cannot flow to deterministic nodes
        from_node_obj = self.nodes[from_node]
        to_node_obj = self.nodes[to_node]

        if not from_node_obj.is_deterministic and isinstance(to_node_obj, DeterministicNode):
            self.graph.remove_edge(from_node, to_node)
            raise ValueError(
                f"Cannot connect LLM node {from_node} to deterministic node {to_node}. "
                "This would violate the no-contamination invariant."
            )

    def get_execution_order(self) -> List[str]:
        """
        Get the topological execution order of nodes.

        Returns:
            List of node IDs in execution order

        Raises:
            ValueError: If graph contains cycles
        """
        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Pipeline graph contains cycles")

        return list(nx.topological_sort(self.graph))

    def get_predecessors(self, node_id: str) -> List[str]:
        """
        Get all predecessor nodes for a given node.

        Args:
            node_id: Node to find predecessors for

        Returns:
            List of predecessor node IDs
        """
        return list(self.graph.predecessors(node_id))

    def get_successors(self, node_id: str) -> List[str]:
        """
        Get all successor nodes for a given node.

        Args:
            node_id: Node to find successors for

        Returns:
            List of successor node IDs
        """
        return list(self.graph.successors(node_id))

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate the pipeline structure.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check for cycles
        if not nx.is_directed_acyclic_graph(self.graph):
            errors.append("Pipeline contains cycles")

        # Check for isolated nodes
        isolated = list(nx.isolates(self.graph))
        if isolated:
            errors.append(f"Pipeline contains isolated nodes: {isolated}")

        # Check for required node types
        node_types = {node.node_type for node in self.nodes.values()}
        if NodeType.INPUT not in node_types:
            errors.append("Pipeline missing INPUT node")
        if NodeType.OUTPUT not in node_types:
            errors.append("Pipeline missing OUTPUT node")

        # Validate edge constraints
        for from_node, to_node in self.graph.edges():
            from_obj = self.nodes[from_node]
            to_obj = self.nodes[to_node]

            if not from_obj.is_deterministic and isinstance(to_obj, DeterministicNode):
                errors.append(
                    f"Invalid edge: LLM node {from_node} -> deterministic node {to_node}"
                )

        return len(errors) == 0, errors

    def visualize(self) -> str:
        """
        Create a text representation of the pipeline.

        Returns:
            String representation of the DAG
        """
        lines = [f"NCF Pipeline: {self.name}", "=" * 50]

        for node_id in self.get_execution_order():
            node = self.nodes[node_id]
            predecessors = self.get_predecessors(node_id)
            successors = self.get_successors(node_id)

            lines.append(f"\n[{node_id}] ({node.node_type.value})")
            if predecessors:
                lines.append(f"  <- from: {', '.join(predecessors)}")
            if successors:
                lines.append(f"  -> to: {', '.join(successors)}")

        return "\n".join(lines)

    def get_provenance_chain(self, node_id: str) -> List[str]:
        """
        Get the full provenance chain for a node.

        Args:
            node_id: Node to trace provenance for

        Returns:
            List of node IDs in the provenance chain
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")

        # Get all ancestors using BFS
        ancestors = list(nx.ancestors(self.graph, node_id))
        # Add the node itself
        ancestors.append(node_id)

        # Sort in topological order
        subgraph = self.graph.subgraph(ancestors)
        return list(nx.topological_sort(subgraph))
