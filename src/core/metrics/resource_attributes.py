"""
Resource Attributes Module

Implements local and global resource metrics for node ranking.
Based on Equations 12-13 from the paper.
"""

from typing import Union
from ..graph.network_graph import NetworkGraph
from ..graph.physical_network import PhysicalNetwork
from ..graph.slice_request import SliceRequest


def local_resource(node_id: str, graph: NetworkGraph) -> float:
    """
    Calculate the Local Resource (LR) metric of a node.

    Equation 12:
        LR(vᵢ) = c(vᵢ) × ∑ b(e)
                        e∈E(vᵢ)

    The local resource metric is obtained by multiplying the CPU capacity
    of the node by the sum of bandwidths of all its adjacent links.

    Args:
        node_id: Node identifier
        graph: Network graph (PhysicalNetwork or SliceRequest)

    Returns:
        Local resource metric value

    Rationale:
        The larger LR(vᵢ) is, the more slice nodes can be hosted by the physical node.
    """
    # Get CPU capacity
    if isinstance(graph, PhysicalNetwork):
        cpu = graph.get_node_cpu_available(node_id)
    elif isinstance(graph, SliceRequest):
        cpu = graph.get_node_cpu_demand(node_id)
    else:
        # Generic graph
        cpu = graph.get_node_attribute(node_id, 'cpu') or 0.0

    # Get all adjacent links
    adjacent_links = graph.get_adjacent_links(node_id)

    # Sum bandwidth of all adjacent links
    bandwidth_sum = 0.0
    for source, dest in adjacent_links:
        if isinstance(graph, PhysicalNetwork):
            bandwidth = graph.get_link_bandwidth_available(source, dest)
        elif isinstance(graph, SliceRequest):
            bandwidth = graph.get_link_bandwidth_demand(source, dest)
        else:
            bandwidth = graph.get_link_attribute(source, dest, 'bandwidth') or 0.0
        bandwidth_sum += bandwidth

    # LR = CPU × ∑ Bandwidth
    return cpu * bandwidth_sum


def global_resource(node_id: str, graph: NetworkGraph) -> float:
    """
    Calculate the Global Resource (GR) metric of a node.

    Equation 13:
        GR(vᵢ) = ∑[b(p(vᵢ, vⱼ)) + c(p(vᵢ, vⱼ))] / (|V| - 1)
                i≠j

    Where:
        - b(p(vᵢ, vⱼ)): Minimum bandwidth of the links in the shortest path
        - c(p(vᵢ, vⱼ)): Minimum CPU of the nodes in the shortest path

    Args:
        node_id: Node identifier
        graph: Network graph (PhysicalNetwork or SliceRequest)

    Returns:
        Global resource metric value (normalized)

    Rationale:
        Considering only local resources can cause load imbalance and resource
        fragmentation. Global resource attributes ensure better resource distribution.
    """
    all_nodes = graph.get_all_nodes()

    if len(all_nodes) <= 1:
        return 0.0

    total = 0.0

    # For each other node in the graph
    for target_node in all_nodes:
        if target_node == node_id:
            continue

        # Find shortest path
        path = graph.shortest_path(node_id, target_node)

        if not path or len(path) < 2:
            # No path exists, skip
            continue

        # Calculate minimum bandwidth in the path
        min_bandwidth = float('inf')
        for i in range(len(path) - 1):
            source, dest = path[i], path[i + 1]

            if isinstance(graph, PhysicalNetwork):
                bandwidth = graph.get_link_bandwidth_available(source, dest)
            elif isinstance(graph, SliceRequest):
                bandwidth = graph.get_link_bandwidth_demand(source, dest)
            else:
                bandwidth = graph.get_link_attribute(source, dest, 'bandwidth') or 0.0

            min_bandwidth = min(min_bandwidth, bandwidth)

        # Calculate minimum CPU in the path
        min_cpu = float('inf')
        for path_node in path:
            if isinstance(graph, PhysicalNetwork):
                cpu = graph.get_node_cpu_available(path_node)
            elif isinstance(graph, SliceRequest):
                cpu = graph.get_node_cpu_demand(path_node)
            else:
                cpu = graph.get_node_attribute(path_node, 'cpu') or 0.0

            min_cpu = min(min_cpu, cpu)

        # Add to total (handle infinity case)
        if min_bandwidth != float('inf') and min_cpu != float('inf'):
            total += (min_bandwidth + min_cpu)

    # Normalize by (|V| - 1)
    return total / (len(all_nodes) - 1)


def get_resource_score(
    node_id: str,
    graph: NetworkGraph,
    alpha: float = 0.5,
    use_local_only: bool = False
) -> float:
    """
    Calculate a combined resource score for a node.

    Args:
        node_id: Node identifier
        graph: Network graph
        alpha: Weight for local resource (1-alpha for global)
        use_local_only: If True, only use local resource

    Returns:
        Combined resource score
    """
    lr = local_resource(node_id, graph)

    if use_local_only:
        return lr

    gr = global_resource(node_id, graph)
    return alpha * lr + (1 - alpha) * gr


def calculate_all_local_resources(graph: NetworkGraph) -> dict:
    """
    Calculate local resource metrics for all nodes in the graph.

    Args:
        graph: Network graph

    Returns:
        Dictionary mapping node_id -> LR value
    """
    return {
        node_id: local_resource(node_id, graph)
        for node_id in graph.get_all_nodes()
    }


def calculate_all_global_resources(graph: NetworkGraph) -> dict:
    """
    Calculate global resource metrics for all nodes in the graph.

    Args:
        graph: Network graph

    Returns:
        Dictionary mapping node_id -> GR value
    """
    return {
        node_id: global_resource(node_id, graph)
        for node_id in graph.get_all_nodes()
    }


def normalize_resource_metrics(metrics: dict) -> dict:
    """
    Normalize resource metrics to [0, 1] range.

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


# Utility functions for batch processing

def rank_nodes_by_local_resource(graph: NetworkGraph, descending: bool = True) -> list:
    """
    Rank all nodes by their local resource metric.

    Args:
        graph: Network graph
        descending: If True, rank from highest to lowest

    Returns:
        List of (node_id, LR_value) tuples, sorted
    """
    lr_values = calculate_all_local_resources(graph)
    return sorted(lr_values.items(), key=lambda x: x[1], reverse=descending)


def rank_nodes_by_global_resource(graph: NetworkGraph, descending: bool = True) -> list:
    """
    Rank all nodes by their global resource metric.

    Args:
        graph: Network graph
        descending: If True, rank from highest to lowest

    Returns:
        List of (node_id, GR_value) tuples, sorted
    """
    gr_values = calculate_all_global_resources(graph)
    return sorted(gr_values.items(), key=lambda x: x[1], reverse=descending)
