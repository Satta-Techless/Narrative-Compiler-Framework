"""
Pipeline orchestrator for executing NCF workflows.

Manages the execution of nodes in the correct order with data flow and provenance tracking.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from ncf.core.dag import NCFPipeline
from ncf.core.node import NodeInput, NodeOutput, NodeStatus
from ncf.core.provenance import ProvenanceTracker


class PipelineResult(BaseModel):
    """Result of a pipeline execution."""
    success: bool
    output: Optional[Dict[str, Any]] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float
    node_results: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)


class Orchestrator:
    """
    Orchestrates the execution of an NCF pipeline.

    Responsibilities:
    - Execute nodes in topological order
    - Pass data between nodes
    - Track provenance
    - Handle errors gracefully
    - Collect execution metrics
    """

    def __init__(self, pipeline: NCFPipeline, enable_provenance: bool = True):
        """
        Initialize the orchestrator.

        Args:
            pipeline: The NCF pipeline to execute
            enable_provenance: Whether to track provenance (default True)
        """
        self.pipeline = pipeline
        self.enable_provenance = enable_provenance
        self.provenance_tracker = ProvenanceTracker() if enable_provenance else None

    def execute(
        self,
        input_data: Dict[str, Any],
        start_node: Optional[str] = None,
        end_node: Optional[str] = None
    ) -> PipelineResult:
        """
        Execute the pipeline.

        Args:
            input_data: Input data to start the pipeline
            start_node: Optional node to start from (default: first node)
            end_node: Optional node to end at (default: last node)

        Returns:
            PipelineResult with output and metadata
        """
        start_time = datetime.utcnow()
        errors = []
        node_results = {}
        node_outputs: Dict[str, NodeOutput] = {}

        try:
            # Validate pipeline
            is_valid, validation_errors = self.pipeline.validate()
            if not is_valid:
                return PipelineResult(
                    success=False,
                    execution_time_ms=0,
                    errors=validation_errors
                )

            # Get execution order
            execution_order = self.pipeline.get_execution_order()

            # Filter to subset if start/end specified
            if start_node or end_node:
                start_idx = execution_order.index(start_node) if start_node else 0
                end_idx = execution_order.index(end_node) + 1 if end_node else len(execution_order)
                execution_order = execution_order[start_idx:end_idx]

            # Execute each node
            for node_id in execution_order:
                node = self.pipeline.nodes[node_id]

                # Gather inputs from predecessors
                predecessors = self.pipeline.get_predecessors(node_id)
                if not predecessors:
                    # First node: use provided input data
                    node_input = NodeInput(data=input_data)
                else:
                    # Merge outputs from all predecessors
                    merged_data = {}
                    merged_metadata = {}

                    for pred_id in predecessors:
                        if pred_id in node_outputs:
                            pred_output = node_outputs[pred_id]
                            merged_data.update(pred_output.data)
                            merged_metadata[pred_id] = pred_output.metadata.dict()

                    node_input = NodeInput(data=merged_data, metadata=merged_metadata)

                # Execute node
                try:
                    output = node.run(node_input)
                    node_outputs[node_id] = output

                    # Track provenance
                    if self.provenance_tracker:
                        self.provenance_tracker.record_execution(
                            node_id=node_id,
                            node_type=node.node_type,
                            input_data=node_input.data,
                            output_data=output.data,
                            metadata=output.metadata.dict()
                        )

                    # Store result summary
                    node_results[node_id] = {
                        "status": "completed",
                        "execution_time_ms": output.metadata.execution_time_ms,
                        "data_keys": list(output.data.keys())
                    }

                except Exception as e:
                    error_msg = f"Node {node_id} failed: {str(e)}"
                    errors.append(error_msg)
                    node_results[node_id] = {
                        "status": "failed",
                        "error": str(e)
                    }
                    # Depending on error handling policy, could continue or stop
                    raise

            # Get final output (from last node or specified end node)
            final_node_id = execution_order[-1]
            final_output = node_outputs.get(final_node_id)

            # Calculate total execution time
            end_time = datetime.utcnow()
            execution_time_ms = (end_time - start_time).total_seconds() * 1000

            return PipelineResult(
                success=len(errors) == 0,
                output=final_output.data if final_output else None,
                provenance=self.provenance_tracker.get_full_trace() if self.provenance_tracker else {},
                execution_time_ms=execution_time_ms,
                node_results=node_results,
                errors=errors
            )

        except Exception as e:
            end_time = datetime.utcnow()
            execution_time_ms = (end_time - start_time).total_seconds() * 1000

            errors.append(f"Pipeline execution failed: {str(e)}")
            return PipelineResult(
                success=False,
                execution_time_ms=execution_time_ms,
                node_results=node_results,
                errors=errors
            )

    def execute_node(
        self,
        node_id: str,
        input_data: Dict[str, Any]
    ) -> NodeOutput:
        """
        Execute a single node in isolation.

        Args:
            node_id: The node to execute
            input_data: Input data for the node

        Returns:
            NodeOutput from the execution
        """
        if node_id not in self.pipeline.nodes:
            raise ValueError(f"Node {node_id} not found in pipeline")

        node = self.pipeline.nodes[node_id]
        node_input = NodeInput(data=input_data)

        return node.run(node_input)

    def dry_run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a dry run to validate the pipeline without executing expensive operations.

        Args:
            input_data: Sample input data

        Returns:
            Dictionary with execution plan and validation results
        """
        execution_order = self.pipeline.get_execution_order()
        is_valid, validation_errors = self.pipeline.validate()

        return {
            "valid": is_valid,
            "errors": validation_errors,
            "execution_order": execution_order,
            "node_count": len(self.pipeline.nodes),
            "edge_count": self.pipeline.graph.number_of_edges(),
            "pipeline_visualization": self.pipeline.visualize()
        }
