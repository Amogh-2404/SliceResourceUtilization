"""
Link Provisioning Algorithm

Implements Algorithm 2 from the paper: Slice link provisioning based on
minMaxBWUtilHops strategy.
"""

from typing import Dict, List, Optional, Tuple
from ..graph.physical_network import PhysicalNetwork
from ..graph.slice_request import SliceRequest
from ..pathfinding.k_shortest_path import (
    Path,
    k_shortest_paths_with_bandwidth
)


class LinkProvisioner:
    """
    Provisions slice links to physical paths.

    Implements Algorithm 2: Slice link provisioning based on minMaxBWUtilHops.
    """

    def __init__(self, k: int = 3, use_minmax_strategy: bool = False):
        """
        Initialize the link provisioner.

        Args:
            k: Number of shortest paths to consider
            use_minmax_strategy: Whether to use minMaxBWUtilHops strategy (RT-CSP+)
                                 or basic shortest path (RT-CSP)
        """
        self.k = k
        self.use_minmax_strategy = use_minmax_strategy

    def provision(
        self,
        slice_request: SliceRequest,
        physical_network: PhysicalNetwork,
        node_mapping: Dict[str, str]
    ) -> Optional[Dict[Tuple[str, str], List[str]]]:
        """
        Provision all slice links to physical paths.

        Algorithm 2: Slice link provisioning based on minMaxBWUtilHops.

        Steps:
            1. Rank slice links by bandwidth demand (descending)
            2. For each slice link (in ranked order):
                a. Get source and destination physical nodes from node_mapping
                b. Find k shortest paths with bandwidth constraint
                c. If use_minmax_strategy:
                      Select path with minimum Γ (Equation 20)
                   Else:
                      Select shortest path
                d. Allocate bandwidth on selected path

        Args:
            slice_request: The slice request
            physical_network: The physical network
            node_mapping: Mapping from slice_node_id to physical_node_id

        Returns:
            Dictionary mapping (slice_src, slice_dst) -> physical_path_nodes if successful,
            None if provisioning fails

        Constraint enforced:
            - Equation 6: Bandwidth constraint on physical links
        """
        # Step 1: Rank slice links by bandwidth demand (descending)
        ranked_slice_links = self._rank_slice_links_by_bandwidth(slice_request)

        # Link mapping: (slice_src, slice_dst) -> physical_path_nodes
        link_mapping = {}

        # Step 2: Provision each slice link in ranked order
        for slice_link in ranked_slice_links:
            slice_src, slice_dst = slice_link
            bandwidth_demand = slice_request.get_link_bandwidth_demand(slice_src, slice_dst)

            # Step 2a: Get source and destination physical nodes
            physical_src = node_mapping.get(slice_src)
            physical_dst = node_mapping.get(slice_dst)

            if physical_src is None or physical_dst is None:
                # Node mapping incomplete
                self._rollback_link_mappings(link_mapping, slice_request, physical_network)
                return None

            # Step 2b: Find k shortest paths with bandwidth constraint
            candidate_paths = k_shortest_paths_with_bandwidth(
                physical_network,
                physical_src,
                physical_dst,
                bandwidth_demand,
                k=self.k
            )

            if not candidate_paths:
                # No feasible path found
                self._rollback_link_mappings(link_mapping, slice_request, physical_network)
                return None

            # Step 2c: Select best path
            if self.use_minmax_strategy:
                best_path = self._minmax_bw_util_hops(
                    candidate_paths, physical_network
                )
            else:
                # Basic strategy: use shortest path
                best_path = candidate_paths[0]

            # Step 2d: Allocate bandwidth on the selected path
            success = physical_network.allocate_path_resources(
                best_path.nodes,
                bandwidth_demand,
                slice_request.slice_id
            )

            if not success:
                # Allocation failed
                self._rollback_link_mappings(link_mapping, slice_request, physical_network)
                return None

            # Record mapping
            link_mapping[slice_link] = best_path.nodes

        return link_mapping

    def _rank_slice_links_by_bandwidth(
        self,
        slice_request: SliceRequest
    ) -> List[Tuple[str, str]]:
        """
        Rank slice links by bandwidth demand (descending).

        Rationale: Slice links with larger bandwidth demand are more
        difficult to provision, so they should be provisioned first.

        Args:
            slice_request: Slice request

        Returns:
            List of (source, dest) tuples, sorted by bandwidth (descending)
        """
        slice_links = slice_request.get_all_links()

        # Sort by bandwidth demand (descending)
        sorted_links = sorted(
            slice_links,
            key=lambda link: slice_request.get_link_bandwidth_demand(link[0], link[1]),
            reverse=True
        )

        return sorted_links

    def _minmax_bw_util_hops(
        self,
        candidate_paths: List[Path],
        physical_network: PhysicalNetwork
    ) -> Path:
        """
        Select path using minMaxBWUtilHops strategy.

        Equation 20:
            Γ_pI = (1 - ba(eI)/b0(eI))_max × |L(pI)|

        Select the path with minimum Γ value.

        Strategy rationale:
            - Minimizes the maximum link bandwidth utilization to avoid bottlenecks
            - Prefers paths with fewer hops to reduce bandwidth cost
            - Balances between path quality and path length

        Args:
            candidate_paths: List of candidate Path objects
            physical_network: Physical network

        Returns:
            Path with minimum Γ value
        """
        best_path = None
        min_gamma = float('inf')

        for path in candidate_paths:
            # Calculate maximum bandwidth utilization along the path
            max_utilization = 0.0

            for source, dest in path.links:
                # Get available and initial bandwidth
                available_bw = physical_network.get_link_bandwidth_available(source, dest)
                initial_bw = physical_network.get_link_bandwidth_initial(source, dest)

                if initial_bw > 0:
                    # Utilization = 1 - (available / initial)
                    utilization = 1.0 - (available_bw / initial_bw)
                    max_utilization = max(max_utilization, utilization)

            # Calculate Γ: max_utilization × hop_count
            hop_count = path.hop_count
            gamma = max_utilization * hop_count

            # Select path with minimum Γ
            if gamma < min_gamma:
                min_gamma = gamma
                best_path = path

        return best_path if best_path else candidate_paths[0]

    def _rollback_link_mappings(
        self,
        link_mapping: Dict[Tuple[str, str], List[str]],
        slice_request: SliceRequest,
        physical_network: PhysicalNetwork
    ) -> None:
        """
        Rollback (deallocate) all provisioned links.

        Args:
            link_mapping: (slice_src, slice_dst) -> physical_path mapping
            slice_request: Slice request
            physical_network: Physical network
        """
        for (slice_src, slice_dst), physical_path in link_mapping.items():
            bandwidth_demand = slice_request.get_link_bandwidth_demand(slice_src, slice_dst)

            # Deallocate bandwidth on each link in the path
            for i in range(len(physical_path) - 1):
                physical_network.deallocate_link_resources(
                    physical_path[i],
                    physical_path[i + 1],
                    bandwidth_demand,
                    slice_request.slice_id
                )

    def get_provisioning_stats(
        self,
        slice_request: SliceRequest,
        link_mapping: Dict[Tuple[str, str], List[str]],
        physical_network: PhysicalNetwork
    ) -> Dict:
        """
        Get statistics about a link provisioning result.

        Args:
            slice_request: Slice request
            link_mapping: (slice_src, slice_dst) -> physical_path mapping
            physical_network: Physical network

        Returns:
            Dictionary with provisioning statistics
        """
        if not link_mapping:
            return {}

        # Calculate statistics
        total_hops = 0
        total_bandwidth = 0.0
        max_path_length = 0
        min_path_length = float('inf')

        for (slice_src, slice_dst), physical_path in link_mapping.items():
            hop_count = len(physical_path) - 1
            total_hops += hop_count
            max_path_length = max(max_path_length, hop_count)
            min_path_length = min(min_path_length, hop_count)

            bandwidth = slice_request.get_link_bandwidth_demand(slice_src, slice_dst)
            total_bandwidth += bandwidth * hop_count  # Bandwidth cost

        avg_path_length = total_hops / len(link_mapping) if link_mapping else 0.0

        return {
            'num_links_mapped': len(link_mapping),
            'total_hops': total_hops,
            'avg_path_length': avg_path_length,
            'max_path_length': max_path_length,
            'min_path_length': min_path_length if min_path_length != float('inf') else 0,
            'total_bandwidth_cost': total_bandwidth,
            'mapping': link_mapping
        }

    def __repr__(self) -> str:
        """String representation."""
        strategy = "minMaxBWUtilHops" if self.use_minmax_strategy else "basic k-shortest"
        return f"LinkProvisioner(k={self.k}, strategy={strategy})"


# Utility functions

def provision_slice_links(
    slice_request: SliceRequest,
    physical_network: PhysicalNetwork,
    node_mapping: Dict[str, str],
    k: int = 3,
    use_minmax: bool = False
) -> Optional[Dict[Tuple[str, str], List[str]]]:
    """
    Provision slice links using the default provisioner.

    Args:
        slice_request: Slice request
        physical_network: Physical network
        node_mapping: slice_node -> physical_node mapping
        k: Number of shortest paths to consider
        use_minmax: Whether to use minMaxBWUtilHops strategy

    Returns:
        Link mapping if successful, None otherwise
    """
    provisioner = LinkProvisioner(k=k, use_minmax_strategy=use_minmax)
    return provisioner.provision(slice_request, physical_network, node_mapping)


def validate_link_mapping(
    link_mapping: Dict[Tuple[str, str], List[str]],
    slice_request: SliceRequest,
    physical_network: PhysicalNetwork
) -> Tuple[bool, List[str]]:
    """
    Validate that a link mapping satisfies all constraints.

    Args:
        link_mapping: (slice_src, slice_dst) -> physical_path mapping
        slice_request: Slice request
        physical_network: Physical network

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check that all slice links are mapped
    if len(link_mapping) != slice_request.num_links():
        errors.append(f"Not all slice links are mapped: {len(link_mapping)} / {slice_request.num_links()}")

    # Check Equation 6: Bandwidth constraint
    # Track bandwidth usage on each physical link
    link_bandwidth_usage = {}

    for (slice_src, slice_dst), physical_path in link_mapping.items():
        bandwidth_demand = slice_request.get_link_bandwidth_demand(slice_src, slice_dst)

        # Check each physical link in the path
        for i in range(len(physical_path) - 1):
            phys_src, phys_dst = physical_path[i], physical_path[i + 1]
            link_key = tuple(sorted([phys_src, phys_dst]))

            if link_key not in link_bandwidth_usage:
                link_bandwidth_usage[link_key] = 0.0
            link_bandwidth_usage[link_key] += bandwidth_demand

    # Verify bandwidth constraints
    for link_key, total_usage in link_bandwidth_usage.items():
        phys_src, phys_dst = link_key
        available_bw = physical_network.get_link_bandwidth_initial(phys_src, phys_dst)

        if total_usage > available_bw:
            errors.append(f"Bandwidth constraint violated on link {link_key}: usage={total_usage:.2f} > capacity={available_bw:.2f}")

    return (len(errors) == 0, errors)


def calculate_path_gamma(
    path_nodes: List[str],
    physical_network: PhysicalNetwork
) -> float:
    """
    Calculate the Γ value for a physical path (Equation 20).

    Args:
        path_nodes: List of node IDs in the path
        physical_network: Physical network

    Returns:
        Γ value
    """
    if len(path_nodes) < 2:
        return 0.0

    max_utilization = 0.0

    for i in range(len(path_nodes) - 1):
        source, dest = path_nodes[i], path_nodes[i + 1]
        available_bw = physical_network.get_link_bandwidth_available(source, dest)
        initial_bw = physical_network.get_link_bandwidth_initial(source, dest)

        if initial_bw > 0:
            utilization = 1.0 - (available_bw / initial_bw)
            max_utilization = max(max_utilization, utilization)

    hop_count = len(path_nodes) - 1
    gamma = max_utilization * hop_count

    return gamma
