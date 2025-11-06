"""
Node Ranking Algorithm

Implements node scoring and ranking based on resource and topology attributes.
Includes cooperative provisioning coefficient for physical node selection.
Based on Equations 16-19 from the paper.
"""

from typing import Dict, List, Tuple, Optional
from ..graph.network_graph import NetworkGraph
from ..graph.physical_network import PhysicalNetwork
from ..graph.slice_request import SliceRequest
from ..metrics.resource_attributes import local_resource, global_resource
from ..metrics.topology_attributes import degree_centrality, closeness_centrality


class NodeRanker:
    """
    Ranks nodes based on combined resource and topology attributes.

    Implements:
        - Slice node ranking (Equation 17)
        - Physical node ranking with cooperative provisioning (Equations 18-19)
    """

    def __init__(self, alpha: float = 0.5, beta: float = 0.5, epsilon: float = 1e-5):
        """
        Initialize the node ranker.

        Args:
            alpha: Weight for local attributes (LR × DC)
            beta: Weight for global attributes (GR × CC)
            epsilon: Small constant to prevent division by zero
        """
        self.alpha = alpha
        self.beta = beta
        self.epsilon = epsilon

        # Cache for computed metrics
        self._metric_cache = {}

    def compute_node_score(
        self,
        node_id: str,
        graph: NetworkGraph,
        use_cache: bool = True
    ) -> float:
        """
        Compute the combined score for a node.

        Equation 16:
            S(vᵢ) = α × LR(vᵢ) × DC(vᵢ) + β × GR(vᵢ) × CC(vᵢ)

        Args:
            node_id: Node identifier
            graph: Network graph
            use_cache: Whether to use cached metric values

        Returns:
            Combined node score
        """
        cache_key = (id(graph), node_id)

        if use_cache and cache_key in self._metric_cache:
            metrics = self._metric_cache[cache_key]
        else:
            # Compute all metrics
            lr = local_resource(node_id, graph)
            dc = degree_centrality(node_id, graph)
            gr = global_resource(node_id, graph)
            cc = closeness_centrality(node_id, graph)

            metrics = {'lr': lr, 'dc': dc, 'gr': gr, 'cc': cc}

            if use_cache:
                self._metric_cache[cache_key] = metrics

        # Combined score
        score = (self.alpha * metrics['lr'] * metrics['dc'] +
                 self.beta * metrics['gr'] * metrics['cc'])

        return score

    def rank_slice_nodes(
        self,
        slice_request: SliceRequest
    ) -> List[Tuple[str, float]]:
        """
        Rank slice nodes by their importance for provisioning order.

        Equation 17:
            S(v^S_i) = α × LR(v^S_i) × DC(v^S_i) + β × GR(v^S_i) × CC(v^S_i)

        Args:
            slice_request: The slice request

        Returns:
            List of (node_id, score) tuples, sorted by score (descending)

        Usage:
            Higher-scoring nodes are provisioned first.
        """
        scores = {}

        for node_id in slice_request.get_all_nodes():
            score = self.compute_node_score(node_id, slice_request, use_cache=False)
            scores[node_id] = score

        # Sort by score (descending)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return ranked

    def cooperative_provisioning_coefficient(
        self,
        candidate_node: str,
        mapped_neighbors: List[str],
        physical_network: PhysicalNetwork
    ) -> int:
        """
        Calculate the cooperative provisioning coefficient.

        Equation 18:
            H(v^I_i) = ∑ h(v^I_i, v^I_j)
                      v^I_j ∈ M(Adj(v^S))

        Where h(v^I_i, v^I_j) is the hop count of shortest path.

        Args:
            candidate_node: Candidate physical node ID
            mapped_neighbors: List of physical nodes already hosting neighbor slice nodes
            physical_network: Physical network graph

        Returns:
            Sum of hop counts (cooperative provisioning coefficient)

        Rationale:
            Candidate physical nodes with smaller H values (closer to mapped neighbors)
            receive higher scores, improving link provisioning success.
        """
        if not mapped_neighbors:
            return 0

        total_hops = 0

        for neighbor_node in mapped_neighbors:
            # Get shortest path
            path = physical_network.shortest_path(candidate_node, neighbor_node)

            if path:
                # Hop count is number of links (len(path) - 1)
                hops = len(path) - 1
                total_hops += hops
            else:
                # No path exists, use large penalty
                total_hops += 1000

        return total_hops

    def rank_physical_nodes(
        self,
        candidate_nodes: List[str],
        mapped_neighbors: List[str],
        physical_network: PhysicalNetwork
    ) -> List[Tuple[str, float]]:
        """
        Rank candidate physical nodes with cooperative provisioning coefficient.

        Equation 19:
            S(v^I_i) = [α × LR(v^I_i) × DC(v^I_i) + β × GR(v^I_i) × CC(v^I_i)] / [H(v^I_i) + ε]

        Args:
            candidate_nodes: List of candidate physical node IDs
            mapped_neighbors: List of physical nodes hosting neighbor slice nodes
            physical_network: Physical network graph

        Returns:
            List of (node_id, score) tuples, sorted by score (descending)

        Selection:
            Physical node with highest score is selected for provisioning.
        """
        scores = {}

        for node_id in candidate_nodes:
            # Compute base score (numerator)
            base_score = self.compute_node_score(node_id, physical_network, use_cache=True)

            # Compute cooperative provisioning coefficient
            h_coeff = self.cooperative_provisioning_coefficient(
                node_id, mapped_neighbors, physical_network
            )

            # Final score with cooperative coefficient in denominator
            score = base_score / (h_coeff + self.epsilon)

            scores[node_id] = score

        # Sort by score (descending)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return ranked

    def get_candidate_physical_nodes(
        self,
        slice_node_id: str,
        slice_request: SliceRequest,
        physical_network: PhysicalNetwork
    ) -> List[str]:
        """
        Get candidate physical nodes that satisfy constraints for a slice node.

        Constraints checked:
            - CPU capacity (Equation 3)
            - Location constraint (Equations 4-5)

        Args:
            slice_node_id: Slice node identifier
            slice_request: Slice request
            physical_network: Physical network

        Returns:
            List of candidate physical node IDs
        """
        cpu_demand = slice_request.get_node_cpu_demand(slice_node_id)
        expected_location = slice_request.get_node_expected_location(slice_node_id)
        max_deviation = slice_request.get_node_max_deviation(slice_node_id)

        candidates = []

        for physical_node in physical_network.get_all_nodes():
            # Check CPU constraint (Equation 3)
            available_cpu = physical_network.get_node_cpu_available(physical_node)
            if available_cpu < cpu_demand:
                continue

            # Check location constraint (Equations 4-5)
            if expected_location is not None:
                distance = physical_network.distance_to_location(
                    physical_node, expected_location
                )
                if distance > max_deviation:
                    continue

            candidates.append(physical_node)

        return candidates

    def clear_cache(self) -> None:
        """Clear the metric cache."""
        self._metric_cache.clear()

    def get_metrics_for_node(
        self,
        node_id: str,
        graph: NetworkGraph
    ) -> Dict[str, float]:
        """
        Get all metric values for a node.

        Args:
            node_id: Node identifier
            graph: Network graph

        Returns:
            Dictionary with LR, GR, DC, CC values
        """
        lr = local_resource(node_id, graph)
        dc = degree_centrality(node_id, graph)
        gr = global_resource(node_id, graph)
        cc = closeness_centrality(node_id, graph)

        return {
            'local_resource': lr,
            'degree_centrality': dc,
            'global_resource': gr,
            'closeness_centrality': cc,
            'combined_score': self.alpha * lr * dc + self.beta * gr * cc
        }

    def __repr__(self) -> str:
        """String representation."""
        return (f"NodeRanker(alpha={self.alpha}, beta={self.beta}, "
                f"epsilon={self.epsilon})")


# Utility functions

def rank_all_nodes(
    graph: NetworkGraph,
    alpha: float = 0.5,
    beta: float = 0.5
) -> List[Tuple[str, float]]:
    """
    Rank all nodes in a graph by their combined score.

    Args:
        graph: Network graph
        alpha: Weight for local attributes
        beta: Weight for global attributes

    Returns:
        List of (node_id, score) tuples, sorted descending
    """
    ranker = NodeRanker(alpha=alpha, beta=beta)
    scores = {}

    for node_id in graph.get_all_nodes():
        score = ranker.compute_node_score(node_id, graph, use_cache=False)
        scores[node_id] = score

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def select_best_physical_node(
    candidate_nodes: List[str],
    mapped_neighbors: List[str],
    physical_network: PhysicalNetwork,
    alpha: float = 0.5,
    beta: float = 0.5,
    epsilon: float = 1e-5
) -> Optional[str]:
    """
    Select the best physical node from candidates.

    Args:
        candidate_nodes: List of candidate node IDs
        mapped_neighbors: List of already-mapped neighbor nodes
        physical_network: Physical network
        alpha: Weight for local attributes
        beta: Weight for global attributes
        epsilon: Division safety constant

    Returns:
        Best physical node ID, or None if no candidates
    """
    if not candidate_nodes:
        return None

    ranker = NodeRanker(alpha=alpha, beta=beta, epsilon=epsilon)
    ranked = ranker.rank_physical_nodes(
        candidate_nodes, mapped_neighbors, physical_network
    )

    if ranked:
        return ranked[0][0]  # Return node ID with highest score
    return None
