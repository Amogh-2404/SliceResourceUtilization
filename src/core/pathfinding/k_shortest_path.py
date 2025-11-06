"""
K-Shortest Path Algorithm

Implements Yen's algorithm for finding k shortest loopless paths.
Used for slice link provisioning with bandwidth constraints.

Reference: Yen, J.Y. (1971). Finding the k shortest loopless paths in a network.
Time Complexity: O(k|V|(|E| + |V|log|V|))
"""

from typing import List, Tuple, Optional
import networkx as nx
from ..graph.physical_network import PhysicalNetwork


class Path:
    """
    Represents a path in the physical network.

    Attributes:
        nodes: List of node IDs in the path
        cost: Total cost (e.g., hop count, weighted distance)
        bandwidth: Minimum bandwidth along the path
    """

    def __init__(self, nodes: List[str], cost: float = 0.0, bandwidth: float = float('inf')):
        """
        Initialize a path.

        Args:
            nodes: List of node IDs forming the path
            cost: Total path cost
            bandwidth: Minimum bandwidth in the path
        """
        self.nodes = nodes
        self.cost = cost
        self.bandwidth = bandwidth

    @property
    def links(self) -> List[Tuple[str, str]]:
        """Get the list of links in the path."""
        return [(self.nodes[i], self.nodes[i + 1]) for i in range(len(self.nodes) - 1)]

    @property
    def hop_count(self) -> int:
        """Get the number of hops (links) in the path."""
        return len(self.nodes) - 1

    def __len__(self) -> int:
        """Length of path (number of nodes)."""
        return len(self.nodes)

    def __eq__(self, other: 'Path') -> bool:
        """Check if two paths are equal."""
        return isinstance(other, Path) and self.nodes == other.nodes

    def __hash__(self) -> int:
        """Hash based on nodes."""
        return hash(tuple(self.nodes))

    def __repr__(self) -> str:
        """String representation."""
        return f"Path(nodes={self.nodes}, cost={self.cost:.2f}, hops={self.hop_count})"

    def __str__(self) -> str:
        """Human-readable string."""
        return " -> ".join(self.nodes)


def yen_k_shortest_paths(
    physical_network: PhysicalNetwork,
    source: str,
    target: str,
    k: int = 3,
    min_bandwidth: float = 0.0,
    weight: Optional[str] = None
) -> List[Path]:
    """
    Find k shortest loopless paths using Yen's algorithm.

    Yen's algorithm finds k simple shortest paths from source to target.
    We filter paths that meet the minimum bandwidth requirement.

    Time Complexity: O(k|V|(|E| + |V|log|V|))

    Args:
        physical_network: Physical network graph
        source: Source node ID
        target: Target node ID
        k: Number of paths to find
        min_bandwidth: Minimum bandwidth required (for constraint checking)
        weight: Edge attribute to use as weight (None for hop count)

    Returns:
        List of Path objects, sorted by cost (up to k paths)

    Reference:
        Yen, J.Y. (1971). "Finding the k shortest loopless paths in a network."
        Management Science, 17(11), 712-716.
    """
    if source == target:
        return []

    if not physical_network.has_node(source) or not physical_network.has_node(target):
        return []

    # Graph for shortest path computation
    graph = physical_network.graph.copy()

    # A: List of k shortest paths
    A = []

    # B: Heap of potential k shortest paths
    B = []

    try:
        # Find the first shortest path
        if weight:
            first_path_nodes = nx.dijkstra_path(graph, source, target, weight=weight)
            first_cost = nx.dijkstra_path_length(graph, source, target, weight=weight)
        else:
            first_path_nodes = nx.shortest_path(graph, source, target)
            first_cost = len(first_path_nodes) - 1  # Hop count

        # Calculate minimum bandwidth
        first_bandwidth = _calculate_path_bandwidth(physical_network, first_path_nodes)

        # Check bandwidth constraint
        if first_bandwidth >= min_bandwidth:
            first_path = Path(first_path_nodes, first_cost, first_bandwidth)
            A.append(first_path)

    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []

    # Find k-1 more paths
    for k_iter in range(1, k):
        if not A:
            break

        # The (k-1)th path
        prev_path = A[-1]

        # Iterate through each node in the previous path except the target
        for i in range(len(prev_path.nodes) - 1):
            # Spur node: node from which to find deviation
            spur_node = prev_path.nodes[i]

            # Root path: portion from source to spur node
            root_path = prev_path.nodes[:i + 1]

            # Create a copy of the graph for this iteration
            temp_graph = graph.copy()

            # Remove links that are part of the previous shortest paths
            # sharing the same root path
            for path in A:
                if len(path.nodes) > i and path.nodes[:i + 1] == root_path:
                    # Remove the link from spur node to next node in this path
                    if len(path.nodes) > i + 1:
                        spur_next = path.nodes[i + 1]
                        if temp_graph.has_edge(spur_node, spur_next):
                            temp_graph.remove_edge(spur_node, spur_next)

            # Remove nodes in root path (except spur node) to ensure loop-free
            for node in root_path[:-1]:
                if temp_graph.has_node(node):
                    temp_graph.remove_node(node)

            # Find shortest path from spur node to target in modified graph
            try:
                if weight:
                    spur_path_nodes = nx.dijkstra_path(temp_graph, spur_node, target, weight=weight)
                    spur_cost = nx.dijkstra_path_length(temp_graph, spur_node, target, weight=weight)
                else:
                    spur_path_nodes = nx.shortest_path(temp_graph, spur_node, target)
                    spur_cost = len(spur_path_nodes) - 1

                # Combine root path and spur path
                total_path_nodes = root_path[:-1] + spur_path_nodes

                # Calculate cost
                if weight:
                    total_cost = _calculate_path_cost(graph, total_path_nodes, weight)
                else:
                    total_cost = len(total_path_nodes) - 1

                # Calculate bandwidth
                total_bandwidth = _calculate_path_bandwidth(physical_network, total_path_nodes)

                # Check bandwidth constraint
                if total_bandwidth >= min_bandwidth:
                    total_path = Path(total_path_nodes, total_cost, total_bandwidth)

                    # Add to potential paths if not already found
                    if total_path not in A and total_path not in B:
                        B.append(total_path)

            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue

        if not B:
            break

        # Sort B by cost and add the shortest to A
        B.sort(key=lambda p: p.cost)
        A.append(B.pop(0))

    return A


def _calculate_path_bandwidth(
    physical_network: PhysicalNetwork,
    path_nodes: List[str]
) -> float:
    """
    Calculate the minimum bandwidth along a path.

    Args:
        physical_network: Physical network
        path_nodes: List of node IDs in the path

    Returns:
        Minimum bandwidth (bottleneck bandwidth)
    """
    if len(path_nodes) < 2:
        return float('inf')

    min_bandwidth = float('inf')

    for i in range(len(path_nodes) - 1):
        source, dest = path_nodes[i], path_nodes[i + 1]
        bandwidth = physical_network.get_link_bandwidth_available(source, dest)

        if bandwidth is not None:
            min_bandwidth = min(min_bandwidth, bandwidth)

    return min_bandwidth if min_bandwidth != float('inf') else 0.0


def _calculate_path_cost(
    graph: nx.Graph,
    path_nodes: List[str],
    weight: Optional[str]
) -> float:
    """
    Calculate the total cost of a path.

    Args:
        graph: NetworkX graph
        path_nodes: List of node IDs in the path
        weight: Edge attribute to use as weight

    Returns:
        Total path cost
    """
    if len(path_nodes) < 2:
        return 0.0

    total_cost = 0.0

    for i in range(len(path_nodes) - 1):
        source, dest = path_nodes[i], path_nodes[i + 1]

        if weight and graph.has_edge(source, dest):
            edge_weight = graph[source][dest].get(weight, 1.0)
            total_cost += edge_weight
        else:
            total_cost += 1.0  # Hop count

    return total_cost


def k_shortest_paths_with_bandwidth(
    physical_network: PhysicalNetwork,
    source: str,
    target: str,
    bandwidth_demand: float,
    k: int = 3
) -> List[Path]:
    """
    Find k shortest paths that satisfy bandwidth constraint.

    Wrapper function that ensures all returned paths have sufficient bandwidth.

    Args:
        physical_network: Physical network
        source: Source node ID
        target: Target node ID
        bandwidth_demand: Required bandwidth
        k: Number of paths to find

    Returns:
        List of feasible paths (up to k) with sufficient bandwidth
    """
    paths = yen_k_shortest_paths(
        physical_network,
        source,
        target,
        k=k,
        min_bandwidth=bandwidth_demand
    )

    # Filter paths by bandwidth (extra safety check)
    feasible_paths = [p for p in paths if p.bandwidth >= bandwidth_demand]

    return feasible_paths


def get_shortest_path(
    physical_network: PhysicalNetwork,
    source: str,
    target: str,
    bandwidth_demand: float = 0.0
) -> Optional[Path]:
    """
    Get the single shortest path with bandwidth constraint.

    Args:
        physical_network: Physical network
        source: Source node ID
        target: Target node ID
        bandwidth_demand: Required bandwidth

    Returns:
        Shortest feasible path, or None if no path exists
    """
    paths = yen_k_shortest_paths(
        physical_network,
        source,
        target,
        k=1,
        min_bandwidth=bandwidth_demand
    )

    return paths[0] if paths else None


# Utility functions for path analysis

def get_path_stats(path: Path, physical_network: PhysicalNetwork) -> dict:
    """
    Get statistics about a path.

    Args:
        path: Path object
        physical_network: Physical network

    Returns:
        Dictionary with path statistics
    """
    # Calculate average and maximum link utilization
    utilizations = []

    for source, dest in path.links:
        initial_bw = physical_network.get_link_bandwidth_initial(source, dest)
        available_bw = physical_network.get_link_bandwidth_available(source, dest)

        if initial_bw > 0:
            util = 1.0 - (available_bw / initial_bw)
            utilizations.append(util)

    avg_util = sum(utilizations) / len(utilizations) if utilizations else 0.0
    max_util = max(utilizations) if utilizations else 0.0

    return {
        'hop_count': path.hop_count,
        'bandwidth': path.bandwidth,
        'cost': path.cost,
        'avg_link_utilization': avg_util,
        'max_link_utilization': max_util,
        'nodes': path.nodes,
        'num_nodes': len(path.nodes)
    }


def compare_paths(
    paths: List[Path],
    physical_network: PhysicalNetwork
) -> List[Tuple[Path, dict]]:
    """
    Compare multiple paths with statistics.

    Args:
        paths: List of Path objects
        physical_network: Physical network

    Returns:
        List of (Path, stats_dict) tuples
    """
    return [(path, get_path_stats(path, physical_network)) for path in paths]
