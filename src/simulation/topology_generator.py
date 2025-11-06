"""
Topology Generator Module

Generates physical network topologies using Waxman and BA models.
Based on Table 2 parameters from the paper.
"""

import random
import math
from typing import Tuple, Optional
import networkx as nx
from ..core.graph.physical_network import PhysicalNetwork


def generate_waxman_topology(
    num_nodes: int,
    area_size: Tuple[float, float] = (500, 500),
    alpha: float = 0.5,
    beta: float = 0.2,
    cpu_range: Tuple[float, float] = (50, 100),
    bandwidth_range: Tuple[float, float] = (50, 100),
    random_seed: Optional[int] = None
) -> PhysicalNetwork:
    """
    Generate a physical network using Waxman random topology model.

    Waxman model: P(u,v) = β * exp(-d(u,v) / (α * L))
    where d(u,v) is Euclidean distance and L is maximum distance.

    Reference:
        Waxman, B.M. (1988). "Routing of multipoint connections."
        IEEE Journal on Selected Areas in Communications, 6(9), 1617-1622.

    Args:
        num_nodes: Number of physical nodes
        area_size: (width, height) of the deployment area
        alpha: Parameter affecting link probability (default: 0.5)
        beta: Parameter affecting link probability (default: 0.2)
        cpu_range: (min, max) CPU capacity for nodes
        bandwidth_range: (min, max) bandwidth for links
        random_seed: Random seed for reproducibility

    Returns:
        PhysicalNetwork instance

    Paper Parameters (Table 2):
        - num_nodes: 50, 100, or 150
        - area_size: (500, 500)
        - cpu_range: (50, 100)
        - bandwidth_range: (50, 100)
    """
    if random_seed is not None:
        random.seed(random_seed)

    physical_network = PhysicalNetwork()

    # Step 1: Place nodes randomly in the area
    node_positions = {}
    for i in range(num_nodes):
        node_id = f"PN{i}"
        x = random.uniform(0, area_size[0])
        y = random.uniform(0, area_size[1])
        cpu = random.uniform(cpu_range[0], cpu_range[1])

        node_positions[node_id] = (x, y)
        physical_network.add_physical_node(node_id, cpu, (x, y))

    # Step 2: Calculate maximum distance (L)
    max_distance = math.sqrt(area_size[0]**2 + area_size[1]**2)

    # Step 3: Add links based on Waxman probability
    node_list = list(node_positions.keys())
    for i in range(len(node_list)):
        for j in range(i + 1, len(node_list)):
            node1, node2 = node_list[i], node_list[j]
            pos1, pos2 = node_positions[node1], node_positions[node2]

            # Calculate Euclidean distance
            distance = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

            # Waxman probability
            probability = beta * math.exp(-distance / (alpha * max_distance))

            # Add link with probability
            if random.random() < probability:
                bandwidth = random.uniform(bandwidth_range[0], bandwidth_range[1])
                physical_network.add_physical_link(node1, node2, bandwidth)

    # Ensure connectivity (add minimum spanning tree if disconnected)
    if not physical_network.is_connected():
        physical_network = _ensure_connectivity(
            physical_network, node_positions, bandwidth_range
        )

    return physical_network


def generate_erdos_renyi_topology(
    num_nodes: int,
    connection_probability: float = 0.5,
    area_size: Tuple[float, float] = (500, 500),
    cpu_range: Tuple[float, float] = (50, 100),
    bandwidth_range: Tuple[float, float] = (50, 100),
    random_seed: Optional[int] = None
) -> PhysicalNetwork:
    """
    Generate a physical network using Erdős-Rényi random graph model.

    Each pair of nodes is connected with probability p.

    Args:
        num_nodes: Number of physical nodes
        connection_probability: Probability of connecting two nodes (default: 0.5)
        area_size: (width, height) of the deployment area
        cpu_range: (min, max) CPU capacity for nodes
        bandwidth_range: (min, max) bandwidth for links
        random_seed: Random seed for reproducibility

    Returns:
        PhysicalNetwork instance

    Paper Parameters (Table 2):
        - connection_probability: 0.5
    """
    if random_seed is not None:
        random.seed(random_seed)

    physical_network = PhysicalNetwork()

    # Step 1: Place nodes randomly
    node_positions = {}
    for i in range(num_nodes):
        node_id = f"PN{i}"
        x = random.uniform(0, area_size[0])
        y = random.uniform(0, area_size[1])
        cpu = random.uniform(cpu_range[0], cpu_range[1])

        node_positions[node_id] = (x, y)
        physical_network.add_physical_node(node_id, cpu, (x, y))

    # Step 2: Add links with probability p
    node_list = list(node_positions.keys())
    for i in range(len(node_list)):
        for j in range(i + 1, len(node_list)):
            if random.random() < connection_probability:
                node1, node2 = node_list[i], node_list[j]
                bandwidth = random.uniform(bandwidth_range[0], bandwidth_range[1])
                physical_network.add_physical_link(node1, node2, bandwidth)

    # Ensure connectivity
    if not physical_network.is_connected():
        physical_network = _ensure_connectivity(
            physical_network, node_positions, bandwidth_range
        )

    return physical_network


def _ensure_connectivity(
    physical_network: PhysicalNetwork,
    node_positions: dict,
    bandwidth_range: Tuple[float, float]
) -> PhysicalNetwork:
    """
    Ensure network connectivity by adding links between components.

    Uses minimum spanning tree to connect disconnected components.

    Args:
        physical_network: Physical network (may be disconnected)
        node_positions: Dictionary mapping node_id -> (x, y)
        bandwidth_range: (min, max) bandwidth for new links

    Returns:
        Connected physical network
    """
    # Get connected components
    components = list(physical_network.connected_components())

    if len(components) <= 1:
        return physical_network  # Already connected

    # Connect components
    main_component = components[0]

    for component in components[1:]:
        # Find closest pair of nodes between main_component and this component
        min_distance = float('inf')
        best_pair = None

        for node1 in main_component:
            for node2 in component:
                pos1 = node_positions[node1]
                pos2 = node_positions[node2]
                distance = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

                if distance < min_distance:
                    min_distance = distance
                    best_pair = (node1, node2)

        # Add link between closest nodes
        if best_pair:
            bandwidth = random.uniform(bandwidth_range[0], bandwidth_range[1])
            physical_network.add_physical_link(best_pair[0], best_pair[1], bandwidth)

        # Merge component into main component
        main_component.update(component)

    return physical_network


def generate_barabasi_albert_topology(
    num_nodes: int,
    m: int = 2,
    area_size: Tuple[float, float] = (500, 500),
    cpu_range: Tuple[float, float] = (50, 100),
    bandwidth_range: Tuple[float, float] = (50, 100),
    random_seed: Optional[int] = None
) -> PhysicalNetwork:
    """
    Generate a physical network using Barabási-Albert preferential attachment model.

    Creates a scale-free network using preferential attachment.

    Args:
        num_nodes: Number of physical nodes
        m: Number of edges to attach from a new node to existing nodes
        area_size: (width, height) of the deployment area
        cpu_range: (min, max) CPU capacity for nodes
        bandwidth_range: (min, max) bandwidth for links
        random_seed: Random seed for reproducibility

    Returns:
        PhysicalNetwork instance
    """
    if random_seed is not None:
        random.seed(random_seed)

    # Generate BA graph structure using NetworkX
    ba_graph = nx.barabasi_albert_graph(num_nodes, m, seed=random_seed)

    physical_network = PhysicalNetwork()

    # Add nodes with random positions and CPU
    for i in range(num_nodes):
        node_id = f"PN{i}"
        x = random.uniform(0, area_size[0])
        y = random.uniform(0, area_size[1])
        cpu = random.uniform(cpu_range[0], cpu_range[1])

        physical_network.add_physical_node(node_id, cpu, (x, y))

    # Add links from BA graph with random bandwidth
    for edge in ba_graph.edges():
        node1 = f"PN{edge[0]}"
        node2 = f"PN{edge[1]}"
        bandwidth = random.uniform(bandwidth_range[0], bandwidth_range[1])

        physical_network.add_physical_link(node1, node2, bandwidth)

    return physical_network


def get_topology_statistics(physical_network: PhysicalNetwork) -> dict:
    """
    Calculate statistics about a physical network topology.

    Args:
        physical_network: Physical network

    Returns:
        Dictionary with topology statistics
    """
    num_nodes = physical_network.num_nodes()
    num_links = physical_network.num_links()

    # Average degree
    total_degree = sum(physical_network.degree(node) for node in physical_network.get_all_nodes())
    avg_degree = total_degree / num_nodes if num_nodes > 0 else 0

    # Average path length
    if physical_network.is_connected():
        total_distance = 0
        count = 0
        for node1 in physical_network.get_all_nodes():
            for node2 in physical_network.get_all_nodes():
                if node1 < node2:  # Avoid counting twice
                    distance = physical_network.shortest_path_length(node1, node2)
                    if distance != float('inf'):
                        total_distance += distance
                        count += 1
        avg_path_length = total_distance / count if count > 0 else 0
    else:
        avg_path_length = float('inf')

    # Resource statistics
    total_cpu = sum(
        physical_network.get_node_cpu_initial(node)
        for node in physical_network.get_all_nodes()
    )

    total_bandwidth = sum(
        physical_network.get_link_bandwidth_initial(u, v)
        for u, v in physical_network.get_all_links()
    )

    return {
        'num_nodes': num_nodes,
        'num_links': num_links,
        'avg_degree': avg_degree,
        'avg_path_length': avg_path_length,
        'is_connected': physical_network.is_connected(),
        'num_components': len(list(physical_network.connected_components())),
        'total_cpu_capacity': total_cpu,
        'total_bandwidth_capacity': total_bandwidth,
        'avg_cpu_per_node': total_cpu / num_nodes if num_nodes > 0 else 0,
        'avg_bandwidth_per_link': total_bandwidth / num_links if num_links > 0 else 0
    }


# Default topology generation function

def generate_physical_network(
    num_nodes: int = 100,
    topology_model: str = "waxman",
    **kwargs
) -> PhysicalNetwork:
    """
    Generate a physical network using the specified topology model.

    Args:
        num_nodes: Number of physical nodes
        topology_model: "waxman", "erdos_renyi", or "barabasi_albert"
        **kwargs: Additional parameters for the topology model

    Returns:
        PhysicalNetwork instance

    Raises:
        ValueError: If topology_model is not recognized
    """
    topology_model = topology_model.lower()

    if topology_model == "waxman":
        return generate_waxman_topology(num_nodes, **kwargs)
    elif topology_model in ["erdos_renyi", "erdos-renyi", "er"]:
        return generate_erdos_renyi_topology(num_nodes, **kwargs)
    elif topology_model in ["barabasi_albert", "barabasi-albert", "ba"]:
        return generate_barabasi_albert_topology(num_nodes, **kwargs)
    else:
        raise ValueError(f"Unknown topology model: {topology_model}. "
                        f"Use 'waxman', 'erdos_renyi', or 'barabasi_albert'")
