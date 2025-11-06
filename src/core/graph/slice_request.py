"""
Slice Request Module

Represents a 5G core network slice request with virtual topology and resource demands.
"""

from typing import Dict, List, Tuple, Optional
from .network_graph import NetworkGraph
import time


class SliceRequest(NetworkGraph):
    """
    Represents a 5G core network slice request.

    Attributes:
        slice_id: Unique identifier for the slice request
        arrival_time: When the request arrives at the system
        lifetime: How long the slice will be active
        departure_time: When the slice will be released
    """

    def __init__(
        self,
        slice_id: str,
        arrival_time: float,
        lifetime: float
    ):
        """
        Initialize a slice request.

        Args:
            slice_id: Unique identifier
            arrival_time: Arrival time (t^a_i in paper)
            lifetime: Duration of the slice (t^l_i in paper)

        Notation:
            SR_i = (G^S_i, t^a_i, t^l_i) - Equation from Section 3.2.2
        """
        super().__init__()
        self.slice_id = slice_id
        self.arrival_time = arrival_time
        self.lifetime = lifetime
        self.departure_time = arrival_time + lifetime
        self._status = "pending"  # pending, active, completed, rejected

    def add_slice_node(
        self,
        node_id: str,
        cpu_demand: float,
        expected_location: Tuple[float, float],
        max_deviation: float
    ) -> None:
        """
        Add a slice node (virtual network function) to the request.

        Args:
            node_id: Unique identifier for the slice node
            cpu_demand: Required CPU capacity c(v^S)
            expected_location: Expected deployment location loc(v^S)
            max_deviation: Maximum allowed deployment deviation r(v^S)

        Notation from paper (Section 3.2.2):
            - c(v^S): CPU capability required
            - loc(v^S): Expected deployed location
            - r(v^S): Maximum deployment deviation allowed
        """
        self.add_node(
            node_id,
            cpu_demand=cpu_demand,
            expected_location=expected_location,
            max_deviation=max_deviation
        )

    def add_slice_link(
        self,
        source: str,
        dest: str,
        bandwidth_demand: float
    ) -> None:
        """
        Add a slice link between two slice nodes.

        Args:
            source: Source slice node ID
            dest: Destination slice node ID
            bandwidth_demand: Required bandwidth b(e^S)

        Notation from paper:
            - b(e^S): Bandwidth required by slice link
        """
        self.add_link(
            source,
            dest,
            bandwidth_demand=bandwidth_demand
        )

    def get_node_cpu_demand(self, node_id: str) -> float:
        """
        Get the CPU demand of a slice node.

        Args:
            node_id: Slice node identifier

        Returns:
            CPU demand c(v^S)
        """
        return self.get_node_attribute(node_id, 'cpu_demand') or 0.0

    def get_node_expected_location(self, node_id: str) -> Optional[Tuple[float, float]]:
        """
        Get the expected deployment location of a slice node.

        Args:
            node_id: Slice node identifier

        Returns:
            Expected location loc(v^S) as (x, y) tuple
        """
        return self.get_node_attribute(node_id, 'expected_location')

    def get_node_max_deviation(self, node_id: str) -> float:
        """
        Get the maximum allowed deployment deviation.

        Args:
            node_id: Slice node identifier

        Returns:
            Maximum deviation r(v^S)
        """
        return self.get_node_attribute(node_id, 'max_deviation') or 0.0

    def get_link_bandwidth_demand(self, source: str, dest: str) -> float:
        """
        Get the bandwidth demand of a slice link.

        Args:
            source: Source slice node ID
            dest: Destination slice node ID

        Returns:
            Bandwidth demand b(e^S)
        """
        return self.get_link_attribute(source, dest, 'bandwidth_demand') or 0.0

    def calculate_revenue(self) -> float:
        """
        Calculate the provisioning revenue of this slice request.

        Equation 8:
            REV(G^S, t) = ∑(v^S∈V^S) c(v^S) + ∑(e^S∈E^S) b(e^S)

        Assumes unit price of 1 for both CPU and bandwidth.

        Returns:
            Total revenue
        """
        node_revenue = sum(
            self.get_node_cpu_demand(node) for node in self.get_all_nodes()
        )

        link_revenue = sum(
            self.get_link_bandwidth_demand(u, v) for u, v in self.get_all_links()
        )

        return node_revenue + link_revenue

    def calculate_cost(self, physical_mapping: Dict) -> float:
        """
        Calculate the provisioning cost given a physical mapping.

        Equation 10:
            COST(G^S, t) = ∑(v^S∈V^S) c(v^S) + ∑(e^S∈E^S) |L(p^I(e^S))|·b(e^S)

        Args:
            physical_mapping: Dictionary with 'nodes' and 'links' mappings
                nodes: {slice_node_id: physical_node_id}
                links: {(slice_src, slice_dst): physical_path}

        Returns:
            Total cost
        """
        # Node cost (same as revenue)
        node_cost = sum(
            self.get_node_cpu_demand(node) for node in self.get_all_nodes()
        )

        # Link cost (bandwidth × hop count)
        link_cost = 0.0
        if 'links' in physical_mapping:
            for (src, dst), physical_path in physical_mapping['links'].items():
                bandwidth_demand = self.get_link_bandwidth_demand(src, dst)
                hop_count = len(physical_path) - 1  # Number of links in path
                link_cost += hop_count * bandwidth_demand

        return node_cost + link_cost

    def get_total_cpu_demand(self) -> float:
        """
        Get the total CPU demand across all slice nodes.

        Returns:
            Sum of all CPU demands
        """
        return sum(self.get_node_cpu_demand(node) for node in self.get_all_nodes())

    def get_total_bandwidth_demand(self) -> float:
        """
        Get the total bandwidth demand across all slice links.

        Returns:
            Sum of all bandwidth demands
        """
        return sum(
            self.get_link_bandwidth_demand(u, v) for u, v in self.get_all_links()
        )

    def set_status(self, status: str) -> None:
        """
        Set the status of the slice request.

        Args:
            status: One of 'pending', 'active', 'completed', 'rejected'
        """
        valid_statuses = ['pending', 'active', 'completed', 'rejected']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        self._status = status

    def get_status(self) -> str:
        """Get the current status of the slice request."""
        return self._status

    def is_active(self, current_time: float) -> bool:
        """
        Check if the slice is currently active.

        Args:
            current_time: Current simulation time

        Returns:
            True if slice is active at the given time
        """
        return (self._status == 'active' and
                self.arrival_time <= current_time < self.departure_time)

    def should_depart(self, current_time: float) -> bool:
        """
        Check if the slice should depart at the current time.

        Args:
            current_time: Current simulation time

        Returns:
            True if slice has reached its departure time
        """
        return current_time >= self.departure_time

    def validate_constraints(self) -> Tuple[bool, List[str]]:
        """
        Validate that the slice request has valid parameters.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check that we have at least one node
        if self.num_nodes() == 0:
            errors.append("Slice request must have at least one node")

        # Check node attributes
        for node_id in self.get_all_nodes():
            cpu = self.get_node_cpu_demand(node_id)
            if cpu <= 0:
                errors.append(f"Node {node_id} has invalid CPU demand: {cpu}")

            location = self.get_node_expected_location(node_id)
            if location is None:
                errors.append(f"Node {node_id} missing expected location")

            max_dev = self.get_node_max_deviation(node_id)
            if max_dev < 0:
                errors.append(f"Node {node_id} has negative max deviation: {max_dev}")

        # Check link attributes
        for src, dst in self.get_all_links():
            bandwidth = self.get_link_bandwidth_demand(src, dst)
            if bandwidth <= 0:
                errors.append(f"Link ({src}, {dst}) has invalid bandwidth demand: {bandwidth}")

        # Check timing
        if self.lifetime <= 0:
            errors.append(f"Invalid lifetime: {self.lifetime}")

        if self.arrival_time < 0:
            errors.append(f"Invalid arrival time: {self.arrival_time}")

        return (len(errors) == 0, errors)

    def get_topology_stats(self) -> Dict:
        """
        Get statistics about the slice topology.

        Returns:
            Dictionary with topology metrics
        """
        return {
            'num_nodes': self.num_nodes(),
            'num_links': self.num_links(),
            'total_cpu_demand': self.get_total_cpu_demand(),
            'total_bandwidth_demand': self.get_total_bandwidth_demand(),
            'avg_node_degree': (2 * self.num_links() / self.num_nodes()) if self.num_nodes() > 0 else 0,
            'is_connected': self.is_connected(),
            'revenue': self.calculate_revenue()
        }

    def to_dict(self) -> Dict:
        """
        Convert slice request to dictionary representation.

        Returns:
            Dictionary with all slice information
        """
        base_dict = super().to_dict()
        base_dict.update({
            'slice_id': self.slice_id,
            'arrival_time': self.arrival_time,
            'lifetime': self.lifetime,
            'departure_time': self.departure_time,
            'status': self._status,
            'revenue': self.calculate_revenue(),
            'total_cpu_demand': self.get_total_cpu_demand(),
            'total_bandwidth_demand': self.get_total_bandwidth_demand()
        })
        return base_dict

    def __repr__(self) -> str:
        """String representation."""
        return (f"SliceRequest(id={self.slice_id}, nodes={self.num_nodes()}, "
                f"links={self.num_links()}, arrival={self.arrival_time:.1f}, "
                f"lifetime={self.lifetime:.1f}, status={self._status})")

    def __str__(self) -> str:
        """Human-readable string representation."""
        stats = self.get_topology_stats()
        return (f"Slice Request {self.slice_id}:\n"
                f"  Status: {self._status}\n"
                f"  Topology: {stats['num_nodes']} nodes, {stats['num_links']} links\n"
                f"  Resources: CPU={stats['total_cpu_demand']:.1f}, "
                f"BW={stats['total_bandwidth_demand']:.1f}\n"
                f"  Timing: Arrival={self.arrival_time:.1f}, "
                f"Lifetime={self.lifetime:.1f}, Departure={self.departure_time:.1f}\n"
                f"  Revenue: {stats['revenue']:.2f}")

    def __lt__(self, other: 'SliceRequest') -> bool:
        """
        Compare slice requests by arrival time (for priority queue).

        Args:
            other: Another SliceRequest

        Returns:
            True if self arrives before other
        """
        return self.arrival_time < other.arrival_time

    def __eq__(self, other: 'SliceRequest') -> bool:
        """
        Check equality based on slice ID.

        Args:
            other: Another SliceRequest

        Returns:
            True if same slice ID
        """
        return isinstance(other, SliceRequest) and self.slice_id == other.slice_id

    def __hash__(self) -> int:
        """Hash based on slice ID."""
        return hash(self.slice_id)
