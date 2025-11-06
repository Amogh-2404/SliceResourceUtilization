"""
Core Graph Module

Provides graph data structures for physical networks and slice requests.
"""

from .network_graph import NetworkGraph
from .physical_network import PhysicalNetwork
from .slice_request import SliceRequest

__all__ = ['NetworkGraph', 'PhysicalNetwork', 'SliceRequest']
