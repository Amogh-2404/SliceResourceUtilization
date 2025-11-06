"""
Base Network Graph Module

Provides the base class for both physical network and slice request graphs.
Uses NetworkX for graph operations.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from abc import ABC, abstractmethod


class NetworkGraph(ABC):
    """
    Abstract base class for network graphs.
    Provides common graph operations for both physical and slice networks.
    """

    def __init__(self):
        """Initialize an empty undirected graph."""
        self.graph = nx.Graph()
        self._node_attributes = {}
        self._link_attributes = {}

    def add_node(self, node_id: str, **attributes) -> None:
        """
        Add a node to the graph with attributes.

        Args:
            node_id: Unique identifier for the node
            **attributes: Node attributes (e.g., cpu, location)
        """
        self.graph.add_node(node_id, **attributes)
        self._node_attributes[node_id] = attributes

    def add_link(self, source: str, dest: str, **attributes) -> None:
        """
        Add an undirected link between two nodes.

        Args:
            source: Source node ID
            dest: Destination node ID
            **attributes: Link attributes (e.g., bandwidth)
        """
        self.graph.add_edge(source, dest, **attributes)
        # Store link in both directions for undirected graph
        link_id = self._get_link_id(source, dest)
        self._link_attributes[link_id] = attributes

    def get_node_attribute(self, node_id: str, attribute: str):
        """
        Get a specific attribute of a node.

        Args:
            node_id: Node identifier
            attribute: Attribute name

        Returns:
            Attribute value or None if not found
        """
        return self.graph.nodes[node_id].get(attribute, None)

    def set_node_attribute(self, node_id: str, attribute: str, value) -> None:
        """
        Set a specific attribute of a node.

        Args:
            node_id: Node identifier
            attribute: Attribute name
            value: New value
        """
        self.graph.nodes[node_id][attribute] = value
        if node_id in self._node_attributes:
            self._node_attributes[node_id][attribute] = value

    def get_link_attribute(self, source: str, dest: str, attribute: str):
        """
        Get a specific attribute of a link.

        Args:
            source: Source node ID
            dest: Destination node ID
            attribute: Attribute name

        Returns:
            Attribute value or None if not found
        """
        if self.graph.has_edge(source, dest):
            return self.graph[source][dest].get(attribute, None)
        return None

    def set_link_attribute(self, source: str, dest: str, attribute: str, value) -> None:
        """
        Set a specific attribute of a link.

        Args:
            source: Source node ID
            dest: Destination node ID
            attribute: Attribute name
            value: New value
        """
        if self.graph.has_edge(source, dest):
            self.graph[source][dest][attribute] = value
            link_id = self._get_link_id(source, dest)
            if link_id in self._link_attributes:
                self._link_attributes[link_id][attribute] = value

    def get_all_nodes(self) -> List[str]:
        """
        Get list of all node IDs.

        Returns:
            List of node identifiers
        """
        return list(self.graph.nodes())

    def get_all_links(self) -> List[Tuple[str, str]]:
        """
        Get list of all links as (source, dest) tuples.

        Returns:
            List of link tuples
        """
        return list(self.graph.edges())

    def get_adjacent_nodes(self, node_id: str) -> List[str]:
        """
        Get all nodes adjacent to the given node.

        Args:
            node_id: Node identifier

        Returns:
            List of adjacent node IDs
        """
        return list(self.graph.neighbors(node_id))

    def get_adjacent_links(self, node_id: str) -> List[Tuple[str, str]]:
        """
        Get all links adjacent to the given node.

        Args:
            node_id: Node identifier

        Returns:
            List of adjacent links as (source, dest) tuples
        """
        adjacent_links = []
        for neighbor in self.graph.neighbors(node_id):
            adjacent_links.append((node_id, neighbor))
        return adjacent_links

    def shortest_path(self, source: str, dest: str, weight: Optional[str] = None) -> List[str]:
        """
        Find the shortest path between two nodes.

        Args:
            source: Source node ID
            dest: Destination node ID
            weight: Edge attribute to use as weight (None for hop count)

        Returns:
            List of node IDs in the path, or empty list if no path exists
        """
        try:
            if weight:
                path = nx.dijkstra_path(self.graph, source, dest, weight=weight)
            else:
                path = nx.shortest_path(self.graph, source, dest)
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def shortest_path_length(self, source: str, dest: str, weight: Optional[str] = None) -> float:
        """
        Get the length of the shortest path between two nodes.

        Args:
            source: Source node ID
            dest: Destination node ID
            weight: Edge attribute to use as weight (None for hop count)

        Returns:
            Path length, or infinity if no path exists
        """
        try:
            if weight:
                return nx.dijkstra_path_length(self.graph, source, dest, weight=weight)
            else:
                return nx.shortest_path_length(self.graph, source, dest)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return float('inf')

    def all_simple_paths(self, source: str, dest: str, cutoff: Optional[int] = None) -> List[List[str]]:
        """
        Find all simple paths between two nodes.

        Args:
            source: Source node ID
            dest: Destination node ID
            cutoff: Maximum path length to consider

        Returns:
            List of paths, where each path is a list of node IDs
        """
        try:
            paths = nx.all_simple_paths(self.graph, source, dest, cutoff=cutoff)
            return list(paths)
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return []

    def adjacency_matrix(self) -> np.ndarray:
        """
        Get the adjacency matrix of the graph.

        Returns:
            NumPy array representing the adjacency matrix
        """
        return nx.to_numpy_array(self.graph)

    def distance_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate all-pairs shortest path distances.

        Returns:
            Dictionary mapping (source -> dest -> distance)
        """
        return dict(nx.all_pairs_shortest_path_length(self.graph))

    def degree(self, node_id: str) -> int:
        """
        Get the degree of a node.

        Args:
            node_id: Node identifier

        Returns:
            Number of adjacent links
        """
        return self.graph.degree(node_id)

    def has_node(self, node_id: str) -> bool:
        """
        Check if a node exists in the graph.

        Args:
            node_id: Node identifier

        Returns:
            True if node exists, False otherwise
        """
        return self.graph.has_node(node_id)

    def has_link(self, source: str, dest: str) -> bool:
        """
        Check if a link exists between two nodes.

        Args:
            source: Source node ID
            dest: Destination node ID

        Returns:
            True if link exists, False otherwise
        """
        return self.graph.has_edge(source, dest)

    def num_nodes(self) -> int:
        """
        Get the number of nodes in the graph.

        Returns:
            Node count
        """
        return self.graph.number_of_nodes()

    def num_links(self) -> int:
        """
        Get the number of links in the graph.

        Returns:
            Link count
        """
        return self.graph.number_of_edges()

    def is_connected(self) -> bool:
        """
        Check if the graph is connected.

        Returns:
            True if connected, False otherwise
        """
        return nx.is_connected(self.graph)

    def connected_components(self) -> List[Set[str]]:
        """
        Get all connected components.

        Returns:
            List of sets, each containing node IDs of a component
        """
        return list(nx.connected_components(self.graph))

    def subgraph(self, nodes: List[str]) -> nx.Graph:
        """
        Extract a subgraph containing the specified nodes.

        Args:
            nodes: List of node IDs to include

        Returns:
            NetworkX subgraph
        """
        return self.graph.subgraph(nodes)

    def copy(self) -> 'NetworkGraph':
        """
        Create a deep copy of the network graph.

        Returns:
            New NetworkGraph instance
        """
        new_graph = self.__class__()
        new_graph.graph = self.graph.copy()
        new_graph._node_attributes = self._node_attributes.copy()
        new_graph._link_attributes = self._link_attributes.copy()
        return new_graph

    def _get_link_id(self, source: str, dest: str) -> Tuple[str, str]:
        """
        Get a canonical link identifier (ordered tuple).

        Args:
            source: Source node ID
            dest: Destination node ID

        Returns:
            Ordered tuple (smaller_id, larger_id)
        """
        return tuple(sorted([source, dest]))

    def to_dict(self) -> Dict:
        """
        Convert the graph to a dictionary representation.

        Returns:
            Dictionary with nodes and links
        """
        return {
            'nodes': [
                {'id': node, **self.graph.nodes[node]}
                for node in self.graph.nodes()
            ],
            'links': [
                {'source': u, 'target': v, **self.graph[u][v]}
                for u, v in self.graph.edges()
            ]
        }

    def from_dict(self, data: Dict) -> None:
        """
        Load graph from a dictionary representation.

        Args:
            data: Dictionary with 'nodes' and 'links' keys
        """
        self.graph.clear()
        self._node_attributes.clear()
        self._link_attributes.clear()

        # Add nodes
        for node_data in data.get('nodes', []):
            node_id = node_data.pop('id')
            self.add_node(node_id, **node_data)

        # Add links
        for link_data in data.get('links', []):
            source = link_data.pop('source')
            target = link_data.pop('target')
            self.add_link(source, target, **link_data)

    def __repr__(self) -> str:
        """String representation of the graph."""
        return f"{self.__class__.__name__}(nodes={self.num_nodes()}, links={self.num_links()})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (f"{self.__class__.__name__}:\n"
                f"  Nodes: {self.num_nodes()}\n"
                f"  Links: {self.num_links()}\n"
                f"  Connected: {self.is_connected()}")
