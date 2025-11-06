"""
Slice Request Generator Module

Generates slice requests with Poisson arrivals and exponential lifetimes.
Based on Table 2 parameters from the paper.
"""

import random
import math
from typing import List, Tuple, Optional
import networkx as nx
from ..core.graph.slice_request import SliceRequest


def generate_slice_requests(
    num_requests: int,
    arrival_rate: float = 0.04,
    avg_lifetime: float = 500,
    node_range: Tuple[int, int] = (2, 10),
    connection_probability: float = 0.5,
    cpu_range: Tuple[float, float] = (1, 20),
    bandwidth_range: Tuple[float, float] = (1, 20),
    area_size: Tuple[float, float] = (500, 500),
    max_location_deviation: float = 80,
    random_seed: Optional[int] = None
) -> List[SliceRequest]:
    """
    Generate a list of slice requests with specified parameters.

    Arrival Process: Poisson process with rate λ (arrival_rate)
    Lifetime: Exponential distribution with mean avg_lifetime

    Args:
        num_requests: Total number of slice requests to generate
        arrival_rate: Mean arrival rate (requests per time unit)
        avg_lifetime: Average lifetime of slices (time units)
        node_range: (min, max) number of nodes in each slice
        connection_probability: Probability of connecting two slice nodes
        cpu_range: (min, max) CPU demand for slice nodes
        bandwidth_range: (min, max) bandwidth demand for slice links
        area_size: (width, height) for expected locations
        max_location_deviation: Maximum allowed deployment deviation
        random_seed: Random seed for reproducibility

    Returns:
        List of SliceRequest objects, sorted by arrival time

    Paper Parameters (Table 2):
        - num_requests: 2000
        - arrival_rate: 0.02, 0.04, 0.06, 0.08, 0.1 (4 requests per 100 time units)
        - avg_lifetime: 500 time units (exponential)
        - node_range: (2, 10)
        - connection_probability: 0.2, 0.5, 0.8
        - cpu_range: (1, 20)
        - bandwidth_range: (1, 20)
        - max_location_deviation: 80
    """
    if random_seed is not None:
        random.seed(random_seed)

    requests = []
    current_time = 0.0

    for i in range(num_requests):
        # Generate arrival time using Poisson process
        # Inter-arrival time follows exponential distribution
        inter_arrival_time = random.expovariate(arrival_rate)
        current_time += inter_arrival_time

        # Generate lifetime using exponential distribution
        lifetime = random.expovariate(1.0 / avg_lifetime)

        # Generate slice topology
        num_nodes = random.randint(node_range[0], node_range[1])

        slice_request = _generate_single_slice_request(
            slice_id=f"SR{i}",
            arrival_time=current_time,
            lifetime=lifetime,
            num_nodes=num_nodes,
            connection_probability=connection_probability,
            cpu_range=cpu_range,
            bandwidth_range=bandwidth_range,
            area_size=area_size,
            max_location_deviation=max_location_deviation
        )

        requests.append(slice_request)

    return requests


def _generate_single_slice_request(
    slice_id: str,
    arrival_time: float,
    lifetime: float,
    num_nodes: int,
    connection_probability: float,
    cpu_range: Tuple[float, float],
    bandwidth_range: Tuple[float, float],
    area_size: Tuple[float, float],
    max_location_deviation: float
) -> SliceRequest:
    """
    Generate a single slice request with random topology.

    Args:
        slice_id: Unique identifier
        arrival_time: When the request arrives
        lifetime: How long the slice will be active
        num_nodes: Number of nodes in the slice
        connection_probability: Probability of connecting two nodes
        cpu_range: (min, max) CPU demand
        bandwidth_range: (min, max) bandwidth demand
        area_size: (width, height) for expected locations
        max_location_deviation: Maximum deployment deviation

    Returns:
        SliceRequest instance
    """
    slice_request = SliceRequest(slice_id, arrival_time, lifetime)

    # Generate slice nodes
    for j in range(num_nodes):
        node_id = f"{slice_id}_VN{j}"

        # Random CPU demand
        cpu_demand = random.uniform(cpu_range[0], cpu_range[1])

        # Random expected location
        expected_x = random.uniform(0, area_size[0])
        expected_y = random.uniform(0, area_size[1])
        expected_location = (expected_x, expected_y)

        # Add slice node
        slice_request.add_slice_node(
            node_id,
            cpu_demand,
            expected_location,
            max_location_deviation
        )

    # Generate slice links using Erdős-Rényi model
    node_list = slice_request.get_all_nodes()

    for i in range(len(node_list)):
        for j in range(i + 1, len(node_list)):
            # Connect with probability
            if random.random() < connection_probability:
                node1, node2 = node_list[i], node_list[j]
                bandwidth_demand = random.uniform(bandwidth_range[0], bandwidth_range[1])

                slice_request.add_slice_link(node1, node2, bandwidth_demand)

    # Ensure connectivity if not connected
    if not slice_request.is_connected() and num_nodes > 1:
        _ensure_slice_connectivity(slice_request, bandwidth_range)

    return slice_request


def _ensure_slice_connectivity(
    slice_request: SliceRequest,
    bandwidth_range: Tuple[float, float]
) -> None:
    """
    Ensure slice topology connectivity by adding links.

    Args:
        slice_request: Slice request (may be disconnected)
        bandwidth_range: (min, max) bandwidth for new links
    """
    components = list(slice_request.connected_components())

    if len(components) <= 1:
        return  # Already connected

    # Connect components using MST approach
    main_component = components[0]

    for component in components[1:]:
        # Pick random nodes from each component and connect them
        node1 = random.choice(list(main_component))
        node2 = random.choice(list(component))

        bandwidth_demand = random.uniform(bandwidth_range[0], bandwidth_range[1])
        slice_request.add_slice_link(node1, node2, bandwidth_demand)

        # Merge component
        main_component.update(component)


def generate_slice_requests_uniform_arrivals(
    num_requests: int,
    simulation_time: float,
    avg_lifetime: float = 500,
    **kwargs
) -> List[SliceRequest]:
    """
    Generate slice requests with uniform arrival times.

    Useful for testing and debugging.

    Args:
        num_requests: Number of requests
        simulation_time: Total simulation time
        avg_lifetime: Average lifetime
        **kwargs: Other parameters for slice generation

    Returns:
        List of SliceRequest objects
    """
    requests = []
    time_interval = simulation_time / num_requests

    for i in range(num_requests):
        arrival_time = i * time_interval
        lifetime = random.expovariate(1.0 / avg_lifetime)

        num_nodes = random.randint(kwargs.get('node_range', (2, 10))[0],
                                   kwargs.get('node_range', (2, 10))[1])

        slice_request = _generate_single_slice_request(
            slice_id=f"SR{i}",
            arrival_time=arrival_time,
            lifetime=lifetime,
            num_nodes=num_nodes,
            connection_probability=kwargs.get('connection_probability', 0.5),
            cpu_range=kwargs.get('cpu_range', (1, 20)),
            bandwidth_range=kwargs.get('bandwidth_range', (1, 20)),
            area_size=kwargs.get('area_size', (500, 500)),
            max_location_deviation=kwargs.get('max_location_deviation', 80)
        )

        requests.append(slice_request)

    return requests


def get_request_statistics(requests: List[SliceRequest]) -> dict:
    """
    Calculate statistics about a set of slice requests.

    Args:
        requests: List of slice requests

    Returns:
        Dictionary with statistics
    """
    if not requests:
        return {}

    # Timing statistics
    arrival_times = [req.arrival_time for req in requests]
    lifetimes = [req.lifetime for req in requests]

    # Topology statistics
    num_nodes_list = [req.num_nodes() for req in requests]
    num_links_list = [req.num_links() for req in requests]

    # Resource statistics
    cpu_demands = [req.get_total_cpu_demand() for req in requests]
    bandwidth_demands = [req.get_total_bandwidth_demand() for req in requests]
    revenues = [req.calculate_revenue() for req in requests]

    return {
        'num_requests': len(requests),
        'avg_arrival_time': sum(arrival_times) / len(arrival_times),
        'min_arrival_time': min(arrival_times),
        'max_arrival_time': max(arrival_times),
        'avg_lifetime': sum(lifetimes) / len(lifetimes),
        'min_lifetime': min(lifetimes),
        'max_lifetime': max(lifetimes),
        'avg_num_nodes': sum(num_nodes_list) / len(num_nodes_list),
        'min_num_nodes': min(num_nodes_list),
        'max_num_nodes': max(num_nodes_list),
        'avg_num_links': sum(num_links_list) / len(num_links_list),
        'avg_cpu_demand': sum(cpu_demands) / len(cpu_demands),
        'total_cpu_demand': sum(cpu_demands),
        'avg_bandwidth_demand': sum(bandwidth_demands) / len(bandwidth_demands),
        'total_bandwidth_demand': sum(bandwidth_demands),
        'avg_revenue': sum(revenues) / len(revenues),
        'total_revenue': sum(revenues)
    }


# Batch generation for experiments

def generate_requests_for_experiment(
    experiment_type: str,
    **kwargs
) -> List[SliceRequest]:
    """
    Generate slice requests for specific experiment configurations.

    Args:
        experiment_type: "base_case", "varying_link_prob",
                        "varying_arrival_rate", or "varying_network_size"
        **kwargs: Experiment-specific parameters

    Returns:
        List of SliceRequest objects

    Experiment Configurations (from paper):
        1. Base case: 100 nodes, arrival_rate=0.04, link_prob=0.5
        2. Varying link probability: 0.2, 0.5, 0.8
        3. Varying arrival rate: 0.02, 0.04, 0.06, 0.08, 0.1
        4. Varying network size: 50, 100, 150 nodes
    """
    # Default parameters
    default_params = {
        'num_requests': 2000,
        'arrival_rate': 0.04,
        'avg_lifetime': 500,
        'node_range': (2, 10),
        'connection_probability': 0.5,
        'cpu_range': (1, 20),
        'bandwidth_range': (1, 20),
        'area_size': (500, 500),
        'max_location_deviation': 80
    }

    # Update with experiment-specific and user-provided parameters
    params = {**default_params, **kwargs}

    return generate_slice_requests(**params)
