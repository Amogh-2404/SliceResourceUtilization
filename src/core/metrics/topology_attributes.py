"""
Topology Attributes Module

Implements degree centrality and closeness centrality for node ranking.
Based on Equations 14-15 from the paper.
"""

from typing import Dict, List, Tuple
from ..graph.network_graph import NetworkGraph
import networkx as nx


def degree_centrality(node_id: str, graph: NetworkGraph) -> float:
    """
    Calculate the Degree Centrality (DC) of a node.

    Equation 14:
        DC(vᵢ) = ∑ aᵢⱼ / (|V| - 1)
                 vⱼ

    Where aᵢⱼ = 1 if nodes vᵢ and vⱼ are connected, 0 otherwise.

    This is the normalized degree centrality.

    Args:
        node_id: Node identifier
        graph: Network graph

    Returns:
        Normalized degree centrality in [0, 1]

    Rationale:
        Degree centrality measures the local topological importance of the node.
        The greater it is, the more connected the node is and the more likely
        it is to be selected.
    """
    num_nodes = graph.num_nodes()

    if num_nodes <= 1:
        return 0.0

    # Get the degree of the node
    degree = graph.degree(node_id)

    # Normalize by (|V| - 1)
    normalized_degree = degree / (num_nodes - 1)

    return normalized_degree


def closeness_centrality(node_id: str, graph: NetworkGraph) -> float:
    """
    Calculate the Closeness Centrality (CC) of a node.

    Equation 15:
        CC(vᵢ) = (|V| - 1) / ∑ d(vᵢ, vⱼ)
                            i≠j

    Where d(vᵢ, vⱼ) is the length (hop count) of the shortest path
    between nodes vᵢ and vⱼ.

    Args:
        node_id: Node identifier
        graph: Network graph

    Returns:
        Closeness centrality value

    Rationale:
        Closeness centrality is a method of measuring the importance of a node
        from a global topological perspective. Nodes near the geometric center
        of the graph have higher closeness centrality.
    """
    num_nodes = graph.num_nodes()

    if num_nodes <= 1:
        return 0.0

    # Calculate shortest path distances to all other nodes
    total_distance = 0.0
    reachable_nodes = 0

    for target_node in graph.get_all_nodes():
        if target_node == node_id:
            continue

        distance = graph.shortest_path_length(node_id, target_node)

        if distance != float('inf'):
            total_distance += distance
            reachable_nodes += 1

    # If node is isolated or no paths exist
    if total_distance == 0 or reachable_nodes == 0:
        return 0.0

    # CC = (|V| - 1) / ∑ distances
    closeness = (num_nodes - 1) / total_distance

    return closeness


def betweenness_centrality(node_id: str, graph: NetworkGraph) -> float:
    """
    Calculate the Betweenness Centrality of a node (optional, not in paper).

    Betweenness centrality measures how often a node appears on shortest paths
    between other nodes.

    Args:
        node_id: Node identifier
        graph: Network graph

    Returns:
        Normalized betweenness centrality
    """
    try:
        betweenness = nx.betweenness_centrality(graph.graph)
        return betweenness.get(node_id, 0.0)
    except:
        return 0.0


def eigenvector_centrality(node_id: str, graph: NetworkGraph) -> float:
    """
    Calculate the Eigenvector Centrality of a node (optional, not in paper).

    Eigenvector centrality measures the influence of a node in a network based
    on the concept that connections to high-scoring nodes contribute more.

    Args:
        node_id: Node identifier
        graph: Network graph

    Returns:
        Eigenvector centrality value
    """
    try:
        if not graph.is_connected():
            # Eigenvector centrality requires connected graph
            # Use largest connected component
            largest_cc = max(nx.connected_components(graph.graph), key=len)
            if node_id not in largest_cc:
                return 0.0
            subgraph = graph.graph.subgraph(largest_cc)
            eigenvector = nx.eigenvector_centrality(subgraph, max_iter=1000)
        else:
            eigenvector = nx.eigenvector_centrality(graph.graph, max_iter=1000)

        return eigenvector.get(node_id, 0.0)
    except:
        return 0.0


def get_topology_score(
    node_id: str,
    graph: NetworkGraph,
    alpha: float = 0.5,
    use_degree_only: bool = False
) -> float:
    """
    Calculate a combined topology score for a node.

    Args:
        node_id: Node identifier
        graph: Network graph
        alpha: Weight for degree centrality (1-alpha for closeness)
        use_degree_only: If True, only use degree centrality

    Returns:
        Combined topology score
    """
    dc = degree_centrality(node_id, graph)

    if use_degree_only:
        return dc

    cc = closeness_centrality(node_id, graph)
    return alpha * dc + (1 - alpha) * cc


def calculate_all_degree_centralities(graph: NetworkGraph) -> Dict[str, float]:
    """
    Calculate degree centrality for all nodes in the graph.

    Args:
        graph: Network graph

    Returns:
        Dictionary mapping node_id -> DC value
    """
    return {
        node_id: degree_centrality(node_id, graph)
        for node_id in graph.get_all_nodes()
    }


def calculate_all_closeness_centralities(graph: NetworkGraph) -> Dict[str, float]:
    """
    Calculate closeness centrality for all nodes in the graph.

    Args:
        graph: Network graph

    Returns:
        Dictionary mapping node_id -> CC value
    """
    return {
        node_id: closeness_centrality(node_id, graph)
        for node_id in graph.get_all_nodes()
    }


def calculate_all_centralities(graph: NetworkGraph) -> Dict[str, Dict[str, float]]:
    """
    Calculate all centrality metrics for all nodes.

    Args:
        graph: Network graph

    Returns:
        Dictionary mapping node_id -> {metric_name: value}
    """
    all_nodes = graph.get_all_nodes()

    # Calculate basic centralities
    dc_values = calculate_all_degree_centralities(graph)
    cc_values = calculate_all_closeness_centralities(graph)

    # Combine into single dictionary
    result = {}
    for node_id in all_nodes:
        result[node_id] = {
            'degree_centrality': dc_values[node_id],
            'closeness_centrality': cc_values[node_id]
        }

    return result


def rank_nodes_by_degree_centrality(
    graph: NetworkGraph,
    descending: bool = True
) -> List[Tuple[str, float]]:
    """
    Rank all nodes by their degree centrality.

    Args:
        graph: Network graph
        descending: If True, rank from highest to lowest

    Returns:
        List of (node_id, DC_value) tuples, sorted
    """
    dc_values = calculate_all_degree_centralities(graph)
    return sorted(dc_values.items(), key=lambda x: x[1], reverse=descending)


def rank_nodes_by_closeness_centrality(
    graph: NetworkGraph,
    descending: bool = True
) -> List[Tuple[str, float]]:
    """
    Rank all nodes by their closeness centrality.

    Args:
        graph: Network graph
        descending: If True, rank from highest to lowest

    Returns:
        List of (node_id, CC_value) tuples, sorted
    """
    cc_values = calculate_all_closeness_centralities(graph)
    return sorted(cc_values.items(), key=lambda x: x[1], reverse=descending)


def normalize_centrality_metrics(metrics: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize centrality metrics to [0, 1] range.

    Args:
        metrics: Dictionary of node_id -> metric_value

    Returns:
        Dictionary of node_id -> normalized_value
    """
    if not metrics:
        return {}

    values = list(metrics.values())
    min_val = min(values)
    max_val = max(values)

    if max_val == min_val:
        # All values are the same
        return {node_id: 1.0 for node_id in metrics.keys()}

    normalized = {}
    for node_id, value in metrics.items():
        normalized[node_id] = (value - min_val) / (max_val - min_val)

    return normalized


def get_node_importance_ranking(
    graph: NetworkGraph,
    dc_weight: float = 0.5,
    cc_weight: float = 0.5
) -> List[Tuple[str, float]]:
    """
    Rank nodes by a weighted combination of degree and closeness centrality.

    Args:
        graph: Network graph
        dc_weight: Weight for degree centrality
        cc_weight: Weight for closeness centrality

    Returns:
        List of (node_id, combined_score) tuples, sorted descending
    """
    dc_values = calculate_all_degree_centralities(graph)
    cc_values = calculate_all_closeness_centralities(graph)

    combined_scores = {}
    for node_id in graph.get_all_nodes():
        score = dc_weight * dc_values[node_id] + cc_weight * cc_values[node_id]
        combined_scores[node_id] = score

    return sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
