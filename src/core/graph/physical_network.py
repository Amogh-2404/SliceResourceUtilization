"""
Physical Network Module

Represents the 5G core physical infrastructure with nodes and links.
Manages resource allocation and availability.
"""

from typing import Dict, List, Tuple, Optional
from .network_graph import NetworkGraph
import math


class PhysicalNetwork(NetworkGraph):
    """
    Represents the physical 5G core network infrastructure.

    Manages:
    - Physical nodes with CPU capacity and location
    - Physical links with bandwidth capacity
    - Resource allocation and deallocation for slices
    """

    def __init__(self):
        """Initialize an empty physical network."""
        super().__init__()
        self._slice_allocations = {}  # Maps slice_id -> resource allocation details

    def add_physical_node(
        self,
        node_id: str,
        cpu_capacity: float,
        location: Tuple[float, float]
    ) -> None:
        """
        Add a physical node to the network.

        Args:
            node_id: Unique identifier for the node
            cpu_capacity: Initial total CPU capacity
            location: (x, y) coordinates

        Notation from paper (Table 1):
            - c0(v^I): Initial total CPU capacity
            - ca(v^I): Available CPU capacity (initially = c0)
            - cu(v^I): Used CPU capacity (initially = 0)
            - loc(v^I): Location coordinates
        """
        self.add_node(
            node_id,
            cpu_initial=cpu_capacity,
            cpu_available=cpu_capacity,
            cpu_used=0.0,
            location=location
        )

    def add_physical_link(
        self,
        source: str,
        dest: str,
        bandwidth: float
    ) -> None:
        """
        Add a physical link between two nodes.

        Args:
            source: Source node ID
            dest: Destination node ID
            bandwidth: Initial total bandwidth capacity

        Notation from paper (Table 1):
            - b0(e^I): Initial total bandwidth
            - ba(e^I): Available bandwidth (initially = b0)
            - bu(e^I): Used bandwidth (initially = 0)
        """
        self.add_link(
            source,
            dest,
            bandwidth_initial=bandwidth,
            bandwidth_available=bandwidth,
            bandwidth_used=0.0
        )

    def get_node_cpu_initial(self, node_id: str) -> float:
        """Get initial CPU capacity of a node (c0)."""
        return self.get_node_attribute(node_id, 'cpu_initial') or 0.0

    def get_node_cpu_available(self, node_id: str) -> float:
        """Get available CPU capacity of a node (ca)."""
        return self.get_node_attribute(node_id, 'cpu_available') or 0.0

    def get_node_cpu_used(self, node_id: str) -> float:
        """Get used CPU capacity of a node (cu)."""
        return self.get_node_attribute(node_id, 'cpu_used') or 0.0

    def get_node_location(self, node_id: str) -> Optional[Tuple[float, float]]:
        """Get location coordinates of a node (loc)."""
        return self.get_node_attribute(node_id, 'location')

    def get_link_bandwidth_initial(self, source: str, dest: str) -> float:
        """Get initial bandwidth of a link (b0)."""
        return self.get_link_attribute(source, dest, 'bandwidth_initial') or 0.0

    def get_link_bandwidth_available(self, source: str, dest: str) -> float:
        """Get available bandwidth of a link (ba)."""
        return self.get_link_attribute(source, dest, 'bandwidth_available') or 0.0

    def get_link_bandwidth_used(self, source: str, dest: str) -> float:
        """Get used bandwidth of a link (bu)."""
        return self.get_link_attribute(source, dest, 'bandwidth_used') or 0.0

    def euclidean_distance(
        self,
        node1_id: str,
        node2_id: str
    ) -> float:
        """
        Calculate Euclidean distance between two physical nodes.

        Equation 5:
            dis(v^S_k, v^I_i) = √[(x(v^S_k) - x(v^I_i))² + (y(v^S_k) - y(v^I_i))²]

        Args:
            node1_id: First node ID
            node2_id: Second node ID

        Returns:
            Euclidean distance, or infinity if location not available
        """
        loc1 = self.get_node_location(node1_id)
        loc2 = self.get_node_location(node2_id)

        if loc1 is None or loc2 is None:
            return float('inf')

        return math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)

    def distance_to_location(
        self,
        node_id: str,
        location: Tuple[float, float]
    ) -> float:
        """
        Calculate distance from a node to a specific location.

        Args:
            node_id: Physical node ID
            location: Target (x, y) coordinates

        Returns:
            Euclidean distance
        """
        node_loc = self.get_node_location(node_id)
        if node_loc is None:
            return float('inf')

        return math.sqrt(
            (node_loc[0] - location[0]) ** 2 +
            (node_loc[1] - location[1]) ** 2
        )

    def allocate_node_resources(
        self,
        node_id: str,
        cpu_demand: float,
        slice_id: str
    ) -> bool:
        """
        Allocate CPU resources from a physical node to a slice.

        Implements Constraint (Equation 3):
            ∑ x^k_i · c(v^S_k) ≤ ca(v^I_i)

        Args:
            node_id: Physical node ID
            cpu_demand: CPU capacity to allocate
            slice_id: Slice request ID for tracking

        Returns:
            True if allocation successful, False if insufficient resources
        """
        available = self.get_node_cpu_available(node_id)

        if available < cpu_demand:
            return False

        # Update resources
        new_available = available - cpu_demand
        new_used = self.get_node_cpu_used(node_id) + cpu_demand

        self.set_node_attribute(node_id, 'cpu_available', new_available)
        self.set_node_attribute(node_id, 'cpu_used', new_used)

        # Track allocation
        if slice_id not in self._slice_allocations:
            self._slice_allocations[slice_id] = {'nodes': {}, 'links': {}}
        self._slice_allocations[slice_id]['nodes'][node_id] = cpu_demand

        return True

    def allocate_link_resources(
        self,
        source: str,
        dest: str,
        bandwidth_demand: float,
        slice_id: str
    ) -> bool:
        """
        Allocate bandwidth from a physical link to a slice.

        Implements Constraint (Equation 6):
            ∑ y^kl_ij · b(e^S_kl) ≤ ba(e^I_ij)

        Args:
            source: Source node ID
            dest: Destination node ID
            bandwidth_demand: Bandwidth to allocate
            slice_id: Slice request ID for tracking

        Returns:
            True if allocation successful, False if insufficient bandwidth
        """
        available = self.get_link_bandwidth_available(source, dest)

        if available < bandwidth_demand:
            return False

        # Update resources
        new_available = available - bandwidth_demand
        new_used = self.get_link_bandwidth_used(source, dest) + bandwidth_demand

        self.set_link_attribute(source, dest, 'bandwidth_available', new_available)
        self.set_link_attribute(source, dest, 'bandwidth_used', new_used)

        # Track allocation
        if slice_id not in self._slice_allocations:
            self._slice_allocations[slice_id] = {'nodes': {}, 'links': {}}

        link_id = self._get_link_id(source, dest)
        if link_id not in self._slice_allocations[slice_id]['links']:
            self._slice_allocations[slice_id]['links'][link_id] = 0.0
        self._slice_allocations[slice_id]['links'][link_id] += bandwidth_demand

        return True

    def allocate_path_resources(
        self,
        path: List[str],
        bandwidth_demand: float,
        slice_id: str
    ) -> bool:
        """
        Allocate bandwidth resources for all links in a path.

        Args:
            path: List of node IDs forming the path
            bandwidth_demand: Bandwidth to allocate on each link
            slice_id: Slice request ID for tracking

        Returns:
            True if all allocations successful, False otherwise
        """
        # Check if all links have sufficient bandwidth
        for i in range(len(path) - 1):
            available = self.get_link_bandwidth_available(path[i], path[i + 1])
            if available < bandwidth_demand:
                return False

        # Allocate on all links
        for i in range(len(path) - 1):
            success = self.allocate_link_resources(
                path[i], path[i + 1], bandwidth_demand, slice_id
            )
            if not success:
                # Rollback previous allocations
                for j in range(i):
                    self.deallocate_link_resources(
                        path[j], path[j + 1], bandwidth_demand, slice_id
                    )
                return False

        return True

    def deallocate_node_resources(
        self,
        node_id: str,
        cpu_amount: float,
        slice_id: str
    ) -> None:
        """
        Release CPU resources back to a physical node.

        Args:
            node_id: Physical node ID
            cpu_amount: CPU capacity to release
            slice_id: Slice request ID
        """
        available = self.get_node_cpu_available(node_id)
        used = self.get_node_cpu_used(node_id)

        new_available = available + cpu_amount
        new_used = max(0.0, used - cpu_amount)

        self.set_node_attribute(node_id, 'cpu_available', new_available)
        self.set_node_attribute(node_id, 'cpu_used', new_used)

        # Update tracking
        if slice_id in self._slice_allocations:
            if node_id in self._slice_allocations[slice_id]['nodes']:
                del self._slice_allocations[slice_id]['nodes'][node_id]

    def deallocate_link_resources(
        self,
        source: str,
        dest: str,
        bandwidth_amount: float,
        slice_id: str
    ) -> None:
        """
        Release bandwidth resources back to a physical link.

        Args:
            source: Source node ID
            dest: Destination node ID
            bandwidth_amount: Bandwidth to release
            slice_id: Slice request ID
        """
        available = self.get_link_bandwidth_available(source, dest)
        used = self.get_link_bandwidth_used(source, dest)

        new_available = available + bandwidth_amount
        new_used = max(0.0, used - bandwidth_amount)

        self.set_link_attribute(source, dest, 'bandwidth_available', new_available)
        self.set_link_attribute(source, dest, 'bandwidth_used', new_used)

        # Update tracking
        if slice_id in self._slice_allocations:
            link_id = self._get_link_id(source, dest)
            if link_id in self._slice_allocations[slice_id]['links']:
                self._slice_allocations[slice_id]['links'][link_id] -= bandwidth_amount
                if self._slice_allocations[slice_id]['links'][link_id] <= 0:
                    del self._slice_allocations[slice_id]['links'][link_id]

    def deallocate_slice(self, slice_id: str) -> None:
        """
        Release all resources allocated to a slice.

        Args:
            slice_id: Slice request ID
        """
        if slice_id not in self._slice_allocations:
            return

        allocation = self._slice_allocations[slice_id]

        # Release node resources (create copy to avoid RuntimeError)
        for node_id, cpu_amount in list(allocation['nodes'].items()):
            self.deallocate_node_resources(node_id, cpu_amount, slice_id)

        # Release link resources (create copy to avoid RuntimeError)
        for link_id, bandwidth_amount in list(allocation['links'].items()):
            source, dest = link_id
            self.deallocate_link_resources(source, dest, bandwidth_amount, slice_id)

        # Remove tracking
        del self._slice_allocations[slice_id]

    def get_slice_allocation(self, slice_id: str) -> Optional[Dict]:
        """
        Get the resource allocation details for a slice.

        Args:
            slice_id: Slice request ID

        Returns:
            Dictionary with 'nodes' and 'links' allocations, or None if not found
        """
        return self._slice_allocations.get(slice_id, None)

    def get_active_slices(self) -> List[str]:
        """
        Get list of all currently active slice IDs.

        Returns:
            List of slice IDs
        """
        return list(self._slice_allocations.keys())

    def get_resource_utilization(self) -> Dict[str, float]:
        """
        Calculate overall resource utilization metrics.

        Returns:
            Dictionary with CPU and bandwidth utilization percentages
        """
        total_cpu_initial = sum(
            self.get_node_cpu_initial(node) for node in self.get_all_nodes()
        )
        total_cpu_used = sum(
            self.get_node_cpu_used(node) for node in self.get_all_nodes()
        )

        total_bw_initial = sum(
            self.get_link_bandwidth_initial(u, v) for u, v in self.get_all_links()
        )
        total_bw_used = sum(
            self.get_link_bandwidth_used(u, v) for u, v in self.get_all_links()
        )

        cpu_util = (total_cpu_used / total_cpu_initial * 100) if total_cpu_initial > 0 else 0
        bw_util = (total_bw_used / total_bw_initial * 100) if total_bw_initial > 0 else 0

        return {
            'cpu_utilization_percent': cpu_util,
            'bandwidth_utilization_percent': bw_util,
            'total_cpu_initial': total_cpu_initial,
            'total_cpu_used': total_cpu_used,
            'total_cpu_available': total_cpu_initial - total_cpu_used,
            'total_bandwidth_initial': total_bw_initial,
            'total_bandwidth_used': total_bw_used,
            'total_bandwidth_available': total_bw_initial - total_bw_used
        }

    def reset_resources(self) -> None:
        """
        Reset all resources to initial state (deallocate all slices).
        """
        # Deallocate all slices
        for slice_id in list(self._slice_allocations.keys()):
            self.deallocate_slice(slice_id)

        # Reset all node resources
        for node_id in self.get_all_nodes():
            initial_cpu = self.get_node_cpu_initial(node_id)
            self.set_node_attribute(node_id, 'cpu_available', initial_cpu)
            self.set_node_attribute(node_id, 'cpu_used', 0.0)

        # Reset all link resources
        for source, dest in self.get_all_links():
            initial_bw = self.get_link_bandwidth_initial(source, dest)
            self.set_link_attribute(source, dest, 'bandwidth_available', initial_bw)
            self.set_link_attribute(source, dest, 'bandwidth_used', 0.0)

    def __repr__(self) -> str:
        """String representation."""
        util = self.get_resource_utilization()
        return (f"PhysicalNetwork(nodes={self.num_nodes()}, links={self.num_links()}, "
                f"cpu_util={util['cpu_utilization_percent']:.1f}%, "
                f"bw_util={util['bandwidth_utilization_percent']:.1f}%)")
