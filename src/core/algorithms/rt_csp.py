"""
RT-CSP Algorithm

Implements Algorithm 3: Complete slice provisioning algorithm.
Combines node provisioning and link provisioning.

RT-CSP: Basic version with k-shortest path
RT-CSP+: Enhanced version with minMaxBWUtilHops strategy
"""

from typing import Dict, Optional, Tuple
from ..graph.physical_network import PhysicalNetwork
from ..graph.slice_request import SliceRequest
from .node_provisioning import NodeProvisioner
from .link_provisioning import LinkProvisioner


class ProvisioningResult:
    """
    Encapsulates the result of a slice provisioning attempt.
    """

    def __init__(
        self,
        success: bool,
        node_mapping: Optional[Dict[str, str]] = None,
        link_mapping: Optional[Dict[Tuple[str, str], list]] = None,
        failure_reason: Optional[str] = None
    ):
        """
        Initialize provisioning result.

        Args:
            success: Whether provisioning was successful
            node_mapping: slice_node -> physical_node mapping
            link_mapping: (slice_src, slice_dst) -> physical_path mapping
            failure_reason: Reason for failure if unsuccessful
        """
        self.success = success
        self.node_mapping = node_mapping or {}
        self.link_mapping = link_mapping or {}
        self.failure_reason = failure_reason

    def __bool__(self) -> bool:
        """Boolean value indicates success."""
        return self.success

    def __repr__(self) -> str:
        """String representation."""
        if self.success:
            return (f"ProvisioningResult(success=True, "
                    f"nodes={len(self.node_mapping)}, links={len(self.link_mapping)})")
        return f"ProvisioningResult(success=False, reason='{self.failure_reason}')"


class RTCSP:
    """
    RT-CSP: Resource and Topology based Core Slice Provisioning.

    Two-stage heuristic algorithm:
        Stage 1: Node provisioning based on resource & topology attributes
        Stage 2: Link provisioning using k-shortest path

    Implements Algorithm 3 from the paper.
    """

    def __init__(
        self,
        alpha: float = 0.5,
        beta: float = 0.5,
        k: int = 3,
        epsilon: float = 1e-5
    ):
        """
        Initialize RT-CSP algorithm.

        Args:
            alpha: Weight for local attributes (LR × DC)
            beta: Weight for global attributes (GR × CC)
            k: Number of shortest paths to consider
            epsilon: Small constant to prevent division by zero
        """
        self.alpha = alpha
        self.beta = beta
        self.k = k
        self.epsilon = epsilon

        # Initialize provisioners
        self.node_provisioner = NodeProvisioner(
            alpha=alpha,
            beta=beta,
            epsilon=epsilon
        )

        self.link_provisioner = LinkProvisioner(
            k=k,
            use_minmax_strategy=False  # Basic RT-CSP uses standard k-shortest
        )

    def provision_slice(
        self,
        slice_request: SliceRequest,
        physical_network: PhysicalNetwork
    ) -> ProvisioningResult:
        """
        Provision a complete slice (nodes and links).

        Algorithm 3: Slice provisioning algorithm RT-CSP.

        Steps:
            1. Check slice requests whose lifetime ends, release resources
            2. Provision slice nodes using Algorithm 1
            3. If node provisioning failed, return failure
            4. Provision slice links using Algorithm 2
            5. If link provisioning failed, rollback nodes and return failure
            6. Return success with mappings

        Args:
            slice_request: The slice request to provision
            physical_network: The physical network

        Returns:
            ProvisioningResult with success status and mappings
        """
        # Stage 1: Node Provisioning
        node_mapping = self.node_provisioner.provision(
            slice_request, physical_network
        )

        if node_mapping is None:
            return ProvisioningResult(
                success=False,
                failure_reason="Node provisioning failed: no feasible physical nodes"
            )

        # Stage 2: Link Provisioning
        link_mapping = self.link_provisioner.provision(
            slice_request, physical_network, node_mapping
        )

        if link_mapping is None:
            # Link provisioning failed, rollback node allocations
            self._rollback_node_resources(
                node_mapping, slice_request, physical_network
            )
            return ProvisioningResult(
                success=False,
                failure_reason="Link provisioning failed: no feasible physical paths"
            )

        # Success
        return ProvisioningResult(
            success=True,
            node_mapping=node_mapping,
            link_mapping=link_mapping
        )

    def _rollback_node_resources(
        self,
        node_mapping: Dict[str, str],
        slice_request: SliceRequest,
        physical_network: PhysicalNetwork
    ) -> None:
        """
        Rollback node resource allocations.

        Args:
            node_mapping: slice_node -> physical_node mapping
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

    def get_algorithm_name(self) -> str:
        """Get the algorithm name."""
        return "RT-CSP"

    def __repr__(self) -> str:
        """String representation."""
        return (f"RTCSP(alpha={self.alpha}, beta={self.beta}, k={self.k})")


class RTCSPPlus(RTCSP):
    """
    RT-CSP+: Enhanced RT-CSP with minMaxBWUtilHops strategy.

    Differs from RT-CSP only in link provisioning stage:
        - Uses minMaxBWUtilHops strategy to select best path (Equation 20)
        - Minimizes: max_link_utilization × hop_count
        - Avoids bottlenecks and reduces bandwidth cost
    """

    def __init__(
        self,
        alpha: float = 0.5,
        beta: float = 0.5,
        k: int = 3,
        epsilon: float = 1e-5
    ):
        """
        Initialize RT-CSP+ algorithm.

        Args:
            alpha: Weight for local attributes (LR × DC)
            beta: Weight for global attributes (GR × CC)
            k: Number of shortest paths to consider
            epsilon: Small constant to prevent division by zero
        """
        super().__init__(alpha, beta, k, epsilon)

        # Override link provisioner with minMaxBWUtilHops strategy
        self.link_provisioner = LinkProvisioner(
            k=k,
            use_minmax_strategy=True  # RT-CSP+ uses minMaxBWUtilHops
        )

    def get_algorithm_name(self) -> str:
        """Get the algorithm name."""
        return "RT-CSP+"

    def __repr__(self) -> str:
        """String representation."""
        return (f"RTCSPPlus(alpha={self.alpha}, beta={self.beta}, k={self.k})")


# Factory function

def create_provisioning_algorithm(
    algorithm_name: str,
    alpha: float = 0.5,
    beta: float = 0.5,
    k: int = 3,
    epsilon: float = 1e-5
) -> RTCSP:
    """
    Factory function to create provisioning algorithm.

    Args:
        algorithm_name: "RT-CSP" or "RT-CSP+"
        alpha: Weight for local attributes
        beta: Weight for global attributes
        k: Number of shortest paths
        epsilon: Division safety constant

    Returns:
        RTCSP or RTCSPPlus instance

    Raises:
        ValueError: If algorithm_name is not recognized
    """
    algorithm_name = algorithm_name.upper().replace("_", "-")

    if algorithm_name == "RT-CSP":
        return RTCSP(alpha=alpha, beta=beta, k=k, epsilon=epsilon)
    elif algorithm_name == "RT-CSP+":
        return RTCSPPlus(alpha=alpha, beta=beta, k=k, epsilon=epsilon)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm_name}. Use 'RT-CSP' or 'RT-CSP+'")


# Utility functions

def provision_slice_request(
    slice_request: SliceRequest,
    physical_network: PhysicalNetwork,
    algorithm: str = "RT-CSP+",
    **kwargs
) -> ProvisioningResult:
    """
    Provision a slice request using the specified algorithm.

    Args:
        slice_request: Slice request
        physical_network: Physical network
        algorithm: Algorithm name ("RT-CSP" or "RT-CSP+")
        **kwargs: Additional algorithm parameters (alpha, beta, k, epsilon)

    Returns:
        ProvisioningResult
    """
    algo = create_provisioning_algorithm(algorithm, **kwargs)
    return algo.provision_slice(slice_request, physical_network)


def calculate_provisioning_cost(
    slice_request: SliceRequest,
    result: ProvisioningResult
) -> float:
    """
    Calculate the provisioning cost for a successful provisioning.

    Equation 10:
        COST(G^S, t) = ∑ c(v^S) + ∑ |L(p^I(e^S))|·b(e^S)

    Args:
        slice_request: Slice request
        result: Provisioning result

    Returns:
        Total cost
    """
    if not result.success:
        return 0.0

    # Node cost (CPU)
    node_cost = sum(
        slice_request.get_node_cpu_demand(slice_node)
        for slice_node in result.node_mapping.keys()
    )

    # Link cost (bandwidth × hop count)
    link_cost = 0.0
    for (slice_src, slice_dst), physical_path in result.link_mapping.items():
        bandwidth = slice_request.get_link_bandwidth_demand(slice_src, slice_dst)
        hop_count = len(physical_path) - 1
        link_cost += bandwidth * hop_count

    return node_cost + link_cost


def get_provisioning_statistics(
    slice_request: SliceRequest,
    result: ProvisioningResult,
    physical_network: PhysicalNetwork
) -> Dict:
    """
    Get comprehensive statistics about a provisioning result.

    Args:
        slice_request: Slice request
        result: Provisioning result
        physical_network: Physical network

    Returns:
        Dictionary with statistics
    """
    if not result.success:
        return {
            'success': False,
            'failure_reason': result.failure_reason
        }

    # Calculate metrics
    revenue = slice_request.calculate_revenue()

    cost = calculate_provisioning_cost(slice_request, result)

    revenue_cost_ratio = revenue / cost if cost > 0 else 0.0

    # Path statistics
    total_hops = sum(
        len(path) - 1
        for path in result.link_mapping.values()
    )

    avg_path_length = total_hops / len(result.link_mapping) if result.link_mapping else 0.0

    return {
        'success': True,
        'num_nodes_mapped': len(result.node_mapping),
        'num_links_mapped': len(result.link_mapping),
        'revenue': revenue,
        'cost': cost,
        'revenue_cost_ratio': revenue_cost_ratio,
        'total_hops': total_hops,
        'avg_path_length': avg_path_length,
        'node_mapping': result.node_mapping,
        'link_mapping': result.link_mapping
    }
