"""
Node Provisioning Algorithm

Implements Algorithm 1 from the paper: Slice node provisioning based on
network resource and topology attributes.
"""

from typing import Dict, List, Optional, Tuple
from ..graph.physical_network import PhysicalNetwork
from ..graph.slice_request import SliceRequest
from .node_ranking import NodeRanker


class NodeProvisioner:
    """
    Provisions slice nodes to physical nodes using heuristic ranking.

    Implements Algorithm 1: Slice node provisioning based on network
    resource and topology attributes.
    """

    def __init__(self, alpha: float = 0.5, beta: float = 0.5, epsilon: float = 1e-5):
        """
        Initialize the node provisioner.

        Args:
            alpha: Weight for local attributes (LR × DC)
            beta: Weight for global attributes (GR × CC)
            epsilon: Small constant to prevent division by zero
        """
        self.ranker = NodeRanker(alpha=alpha, beta=beta, epsilon=epsilon)
        self.alpha = alpha
        self.beta = beta
        self.epsilon = epsilon

    def provision(
        self,
        slice_request: SliceRequest,
        physical_network: PhysicalNetwork
    ) -> Optional[Dict[str, str]]:
        """
        Provision all slice nodes of a request to physical nodes.

        Algorithm 1: Slice node provisioning based on network resource
        and topology attributes.

        Steps:
            1. Calculate scores for all slice nodes (Equation 17)
            2. Rank slice nodes by score (descending)
            3. For each slice node (in ranked order):
                a. Get candidate physical nodes (satisfy CPU & location constraints)
                b. Get already-mapped neighbor slice nodes
                c. Calculate cooperative provisioning coefficient H for each candidate
                d. Score candidates (Equation 19)
                e. Select physical node with highest score
                f. Allocate resources

        Args:
            slice_request: The slice request to provision
            physical_network: The physical network

        Returns:
            Dictionary mapping slice_node_id -> physical_node_id if successful,
            None if provisioning fails

        Constraints enforced:
            - Equation 1: Each slice node maps to one physical node
            - Equation 2: One-to-one mapping (no co-hosting)
            - Equation 3: CPU capacity constraint
            - Equation 4-5: Location constraint
        """
        # Step 1 & 2: Rank all slice nodes by their scores
        ranked_slice_nodes = self.ranker.rank_slice_nodes(slice_request)

        # Node mapping: slice_node_id -> physical_node_id
        node_mapping = {}

        # Step 3: Provision each slice node in ranked order
        for slice_node_id, _score in ranked_slice_nodes:
            # Step 3a: Get candidate physical nodes
            candidates = self.ranker.get_candidate_physical_nodes(
                slice_node_id, slice_request, physical_network
            )

            if not candidates:
                # No feasible physical nodes, provisioning fails
                self._rollback_node_mappings(node_mapping, slice_request, physical_network)
                return None

            # Remove already-mapped physical nodes (Equation 2: one-to-one mapping)
            candidates = [node for node in candidates if node not in node_mapping.values()]

            if not candidates:
                # All candidates already used
                self._rollback_node_mappings(node_mapping, slice_request, physical_network)
                return None

            # Step 3b: Get physical nodes hosting neighbor slice nodes
            mapped_neighbors = self._get_mapped_neighbors(
                slice_node_id, slice_request, node_mapping
            )

            # Step 3c & 3d: Rank physical nodes with cooperative provisioning coefficient
            ranked_physical = self.ranker.rank_physical_nodes(
                candidates, mapped_neighbors, physical_network
            )

            if not ranked_physical:
                # No suitable physical node found
                self._rollback_node_mappings(node_mapping, slice_request, physical_network)
                return None

            # Step 3e: Select best physical node (highest score)
            best_physical_node = ranked_physical[0][0]

            # Step 3f: Allocate CPU resources
            cpu_demand = slice_request.get_node_cpu_demand(slice_node_id)
            success = physical_network.allocate_node_resources(
                best_physical_node,
                cpu_demand,
                slice_request.slice_id
            )

            if not success:
                # Allocation failed (should not happen due to constraint checking)
                self._rollback_node_mappings(node_mapping, slice_request, physical_network)
                return None

            # Record mapping
            node_mapping[slice_node_id] = best_physical_node

        return node_mapping

    def _get_mapped_neighbors(
        self,
        slice_node_id: str,
        slice_request: SliceRequest,
        node_mapping: Dict[str, str]
    ) -> List[str]:
        """
        Get physical nodes hosting neighbors of a slice node.

        Args:
            slice_node_id: Slice node identifier
            slice_request: Slice request
            node_mapping: Current slice_node -> physical_node mapping

        Returns:
            List of physical node IDs hosting neighbor slice nodes

        Notation:
            M(Adj(v^S)) in Equation 18
        """
        # Get adjacent slice nodes
        adjacent_slice_nodes = slice_request.get_adjacent_nodes(slice_node_id)

        # Get physical nodes hosting these adjacent slice nodes
        mapped_neighbors = []
        for neighbor_slice_node in adjacent_slice_nodes:
            if neighbor_slice_node in node_mapping:
                physical_node = node_mapping[neighbor_slice_node]
                mapped_neighbors.append(physical_node)

        return mapped_neighbors

    def _rollback_node_mappings(
        self,
        node_mapping: Dict[str, str],
        slice_request: SliceRequest,
        physical_network: PhysicalNetwork
    ) -> None:
        """
        Rollback (deallocate) all provisioned nodes.

        Args:
            node_mapping: slice_node_id -> physical_node_id mapping
            slice_request: Slice request
            physical_network: Physical network
        """
        for slice_node_id, physical_node_id in node_mapping.items():
            cpu_demand = slice_request.get_node_cpu_demand(slice_node_id)
            physical_network.deallocate_node_resources(
                physical_node_id,
                cpu_demand,
                slice_request.slice_id
            )

    def get_provisioning_stats(
        self,
        slice_request: SliceRequest,
        node_mapping: Dict[str, str],
        physical_network: PhysicalNetwork
    ) -> Dict:
        """
        Get statistics about a node provisioning result.

        Args:
            slice_request: Slice request
            node_mapping: slice_node -> physical_node mapping
            physical_network: Physical network

        Returns:
            Dictionary with provisioning statistics
        """
        if not node_mapping:
            return {}

        # Calculate average distance between mapped nodes and their expected locations
        total_distance = 0.0
        for slice_node_id, physical_node_id in node_mapping.items():
            expected_loc = slice_request.get_node_expected_location(slice_node_id)
            if expected_loc:
                distance = physical_network.distance_to_location(physical_node_id, expected_loc)
                total_distance += distance

        avg_distance = total_distance / len(node_mapping) if node_mapping else 0.0

        # Calculate average degree of mapped physical nodes
        total_degree = sum(
            physical_network.degree(phys_node)
            for phys_node in node_mapping.values()
        )
        avg_degree = total_degree / len(node_mapping) if node_mapping else 0.0

        # Calculate total CPU allocated
        total_cpu = sum(
            slice_request.get_node_cpu_demand(slice_node)
            for slice_node in node_mapping.keys()
        )

        return {
            'num_nodes_mapped': len(node_mapping),
            'avg_location_distance': avg_distance,
            'avg_physical_node_degree': avg_degree,
            'total_cpu_allocated': total_cpu,
            'mapping': node_mapping
        }

    def __repr__(self) -> str:
        """String representation."""
        return (f"NodeProvisioner(alpha={self.alpha}, beta={self.beta}, "
                f"epsilon={self.epsilon})")


# Utility functions

def provision_slice_nodes(
    slice_request: SliceRequest,
    physical_network: PhysicalNetwork,
    alpha: float = 0.5,
    beta: float = 0.5
) -> Optional[Dict[str, str]]:
    """
    Provision slice nodes using the default provisioner.

    Args:
        slice_request: Slice request
        physical_network: Physical network
        alpha: Weight for local attributes
        beta: Weight for global attributes

    Returns:
        Node mapping if successful, None otherwise
    """
    provisioner = NodeProvisioner(alpha=alpha, beta=beta)
    return provisioner.provision(slice_request, physical_network)


def validate_node_mapping(
    node_mapping: Dict[str, str],
    slice_request: SliceRequest,
    physical_network: PhysicalNetwork
) -> Tuple[bool, List[str]]:
    """
    Validate that a node mapping satisfies all constraints.

    Args:
        node_mapping: slice_node -> physical_node mapping
        slice_request: Slice request
        physical_network: Physical network

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check Equation 1: Each slice node mapped to one physical node
    if len(node_mapping) != slice_request.num_nodes():
        errors.append(f"Not all slice nodes are mapped: {len(node_mapping)} / {slice_request.num_nodes()}")

    # Check Equation 2: One-to-one mapping
    physical_nodes = list(node_mapping.values())
    if len(physical_nodes) != len(set(physical_nodes)):
        errors.append("One-to-one mapping violated: some physical nodes host multiple slice nodes")

    # Check Equation 3: CPU capacity
    for slice_node, physical_node in node_mapping.items():
        cpu_demand = slice_request.get_node_cpu_demand(slice_node)
        available_cpu = physical_network.get_node_cpu_available(physical_node)
        # Note: This checks current state; during provisioning it was satisfied
        if cpu_demand > physical_network.get_node_cpu_initial(physical_node):
            errors.append(f"CPU capacity violated for {physical_node}")

    # Check Equation 4-5: Location constraint
    for slice_node, physical_node in node_mapping.items():
        expected_loc = slice_request.get_node_expected_location(slice_node)
        max_dev = slice_request.get_node_max_deviation(slice_node)
        if expected_loc:
            distance = physical_network.distance_to_location(physical_node, expected_loc)
            if distance > max_dev:
                errors.append(f"Location constraint violated for {slice_node}: distance={distance:.2f} > max={max_dev:.2f}")

    return (len(errors) == 0, errors)
