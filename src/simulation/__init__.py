"""
Simulation Module

Provides simulation framework for slice provisioning experiments.
"""

from .topology_generator import (
    generate_physical_network,
    generate_waxman_topology,
    generate_erdos_renyi_topology
)

from .request_generator import (
    generate_slice_requests,
    get_request_statistics
)

from .simulator import (
    SliceProvisioningSimulator,
    run_single_simulation,
    run_comparison
)

__all__ = [
    'generate_physical_network',
    'generate_waxman_topology',
    'generate_erdos_renyi_topology',
    'generate_slice_requests',
    'get_request_statistics',
    'SliceProvisioningSimulator',
    'run_single_simulation',
    'run_comparison'
]
