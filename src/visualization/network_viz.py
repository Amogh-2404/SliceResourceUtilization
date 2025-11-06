"""
Network Visualization Module

Provides tools to visualize physical networks, slice requests,
and slice-to-physical mappings using NetworkX and Matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path

from ..core.graph.physical_network import PhysicalNetwork
from ..core.graph.slice_request import SliceRequest


# Color schemes
NODE_COLORS = {
    'physical': '#3498db',       # Blue
    'physical_mapped': '#e74c3c', # Red
    'slice': '#2ecc71',          # Green
    'highlight': '#f39c12'       # Orange
}

EDGE_COLORS = {
    'physical': '#95a5a6',       # Gray
    'physical_mapped': '#e74c3c', # Red
    'slice': '#27ae60',          # Dark green
}

FIGURE_SIZE = (12, 8)
DPI = 150


def create_network_layout(
    graph: nx.Graph,
    layout_type: str = 'spring',
    use_positions: bool = True,
    **kwargs
) -> Dict[str, Tuple[float, float]]:
    """
    Create a layout for visualizing a network graph.

    Args:
        graph: NetworkX graph
        layout_type: Type of layout ('spring', 'circular', 'kamada_kawai', 'positions')
        use_positions: Use node position attributes if available
        **kwargs: Additional arguments for layout algorithm

    Returns:
        Dictionary mapping node_id -> (x, y) position
    """
    # Try to use existing positions from node attributes
    if use_positions and layout_type == 'positions':
        pos = {}
        for node in graph.nodes():
            if 'pos' in graph.nodes[node]:
                pos[node] = graph.nodes[node]['pos']
            elif 'location' in graph.nodes[node]:
                pos[node] = graph.nodes[node]['location']
        if pos and len(pos) == len(graph.nodes()):
            return pos

    # Otherwise, use NetworkX layout algorithms
    if layout_type == 'spring':
        return nx.spring_layout(graph, **kwargs)
    elif layout_type == 'circular':
        return nx.circular_layout(graph, **kwargs)
    elif layout_type == 'kamada_kawai':
        return nx.kamada_kawai_layout(graph, **kwargs)
    elif layout_type == 'spectral':
        return nx.spectral_layout(graph, **kwargs)
    else:
        # Default to spring layout
        return nx.spring_layout(graph, **kwargs)


def visualize_physical_network(
    physical_network: PhysicalNetwork,
    layout_type: str = 'positions',
    show_labels: bool = True,
    show_resources: bool = True,
    highlight_nodes: Optional[List[str]] = None,
    highlight_edges: Optional[List[Tuple[str, str]]] = None,
    title: str = "Physical Network Topology",
    output_path: Optional[str] = None,
    show_plot: bool = False
) -> plt.Figure:
    """
    Visualize a physical network topology.

    Args:
        physical_network: Physical network to visualize
        layout_type: Layout algorithm to use
        show_labels: Whether to show node labels
        show_resources: Whether to show resource utilization
        highlight_nodes: List of nodes to highlight
        highlight_edges: List of edges to highlight
        title: Plot title
        output_path: Path to save the figure
        show_plot: Whether to display the plot

    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    # Convert to NetworkX graph
    G = physical_network.graph

    # Create layout
    pos = create_network_layout(G, layout_type)

    # Determine node colors
    node_colors = []
    for node in G.nodes():
        if highlight_nodes and node in highlight_nodes:
            node_colors.append(NODE_COLORS['highlight'])
        else:
            node_colors.append(NODE_COLORS['physical'])

    # Determine node sizes based on CPU capacity
    if show_resources:
        node_sizes = []
        for node in G.nodes():
            cpu_initial = physical_network.get_node_cpu_initial(node)
            # Scale size between 300 and 3000
            size = 300 + (cpu_initial / 100) * 2700
            node_sizes.append(size)
    else:
        node_sizes = 1000

    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=node_sizes,
        alpha=0.8,
        ax=ax
    )

    # Determine edge colors
    edge_colors = []
    edge_widths = []
    for edge in G.edges():
        if highlight_edges and (edge in highlight_edges or edge[::-1] in highlight_edges):
            edge_colors.append(EDGE_COLORS['physical_mapped'])
            edge_widths.append(3.0)
        else:
            edge_colors.append(EDGE_COLORS['physical'])
            edge_widths.append(1.5)

    # Draw edges
    nx.draw_networkx_edges(
        G, pos,
        edge_color=edge_colors,
        width=edge_widths,
        alpha=0.6,
        ax=ax
    )

    # Draw labels
    if show_labels:
        # Adjust label positions slightly above nodes
        label_pos = {node: (x, y + 0.03) for node, (x, y) in pos.items()}
        nx.draw_networkx_labels(
            G, label_pos,
            font_size=8,
            font_weight='bold',
            ax=ax
        )

    # Show resource utilization if requested
    if show_resources:
        util = physical_network.get_resource_utilization()
        resource_text = (
            f"CPU Utilization: {util['cpu_utilization_percent']:.1f}%\n"
            f"Bandwidth Utilization: {util['bandwidth_utilization_percent']:.1f}%"
        )
        ax.text(
            0.02, 0.98, resource_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        )

    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor='white')
        print(f"  Saved figure: {output_path}")

    if show_plot:
        plt.show()

    return fig


def visualize_slice_request(
    slice_request: SliceRequest,
    layout_type: str = 'spring',
    show_labels: bool = True,
    show_demands: bool = True,
    title: Optional[str] = None,
    output_path: Optional[str] = None,
    show_plot: bool = False
) -> plt.Figure:
    """
    Visualize a slice request topology.

    Args:
        slice_request: Slice request to visualize
        layout_type: Layout algorithm to use
        show_labels: Whether to show node labels
        show_demands: Whether to display resource demands
        title: Plot title (auto-generated if None)
        output_path: Path to save the figure
        show_plot: Whether to display the plot

    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 7))

    # Convert to NetworkX graph
    G = slice_request.graph

    # Create layout
    pos = create_network_layout(G, layout_type)

    # Node sizes based on CPU demand
    if show_demands:
        node_sizes = []
        for node in G.nodes():
            cpu_demand = slice_request.get_node_cpu_demand(node)
            # Scale size between 300 and 2000
            size = 300 + (cpu_demand / 20) * 1700
            node_sizes.append(size)
    else:
        node_sizes = 800

    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos,
        node_color=NODE_COLORS['slice'],
        node_size=node_sizes,
        alpha=0.8,
        ax=ax
    )

    # Edge widths based on bandwidth demand
    if show_demands:
        edge_widths = []
        for u, v in G.edges():
            bw_demand = slice_request.get_link_bandwidth_demand(u, v)
            # Scale width between 1 and 5
            width = 1 + (bw_demand / 20) * 4
            edge_widths.append(width)
    else:
        edge_widths = 2.0

    # Draw edges
    nx.draw_networkx_edges(
        G, pos,
        edge_color=EDGE_COLORS['slice'],
        width=edge_widths,
        alpha=0.7,
        ax=ax
    )

    # Draw labels
    if show_labels:
        label_pos = {node: (x, y + 0.03) for node, (x, y) in pos.items()}
        nx.draw_networkx_labels(
            G, label_pos,
            font_size=9,
            font_weight='bold',
            ax=ax
        )

    # Show slice information
    if show_demands:
        info_text = (
            f"Slice ID: {slice_request.slice_id}\n"
            f"Nodes: {slice_request.num_nodes()}\n"
            f"Links: {slice_request.num_links()}\n"
            f"Total CPU Demand: {slice_request.get_total_cpu_demand():.1f}\n"
            f"Total BW Demand: {slice_request.get_total_bandwidth_demand():.1f}\n"
            f"Revenue: {slice_request.calculate_revenue():.2f}"
        )
        ax.text(
            0.02, 0.98, info_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8)
        )

    if title is None:
        title = f"Slice Request: {slice_request.slice_id}"
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor='white')
        print(f"  Saved figure: {output_path}")

    if show_plot:
        plt.show()

    return fig


def visualize_slice_mapping(
    physical_network: PhysicalNetwork,
    slice_request: SliceRequest,
    node_mapping: Dict[str, str],
    link_mapping: Dict[Tuple[str, str], List[str]],
    layout_type: str = 'positions',
    title: Optional[str] = None,
    output_path: Optional[str] = None,
    show_plot: bool = False
) -> plt.Figure:
    """
    Visualize how a slice is mapped onto the physical network.

    Shows both the physical network and highlights the resources
    allocated to the specific slice.

    Args:
        physical_network: Physical network
        slice_request: Slice request
        node_mapping: Dict mapping slice_node -> physical_node
        link_mapping: Dict mapping (slice_src, slice_dst) -> physical_path
        layout_type: Layout algorithm
        title: Plot title
        output_path: Path to save the figure
        show_plot: Whether to display the plot

    Returns:
        Matplotlib figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

    # Left panel: Slice request topology
    G_slice = slice_request.graph
    pos_slice = create_network_layout(G_slice, 'spring')

    nx.draw_networkx_nodes(
        G_slice, pos_slice,
        node_color=NODE_COLORS['slice'],
        node_size=800,
        alpha=0.8,
        ax=ax1
    )
    nx.draw_networkx_edges(
        G_slice, pos_slice,
        edge_color=EDGE_COLORS['slice'],
        width=2,
        alpha=0.7,
        ax=ax1
    )
    nx.draw_networkx_labels(
        G_slice, pos_slice,
        font_size=9,
        font_weight='bold',
        ax=ax1
    )

    ax1.set_title(f"Slice Request: {slice_request.slice_id}", fontsize=12, fontweight='bold')
    ax1.axis('off')

    # Right panel: Physical network with mapping highlighted
    G_physical = physical_network.graph
    pos_physical = create_network_layout(G_physical, layout_type)

    # Determine which physical nodes are mapped
    mapped_physical_nodes = set(node_mapping.values())

    # Determine which physical edges are used
    mapped_physical_edges = set()
    for slice_link, physical_path in link_mapping.items():
        for i in range(len(physical_path) - 1):
            edge = (physical_path[i], physical_path[i + 1])
            mapped_physical_edges.add(edge)

    # Color nodes
    node_colors = []
    for node in G_physical.nodes():
        if node in mapped_physical_nodes:
            node_colors.append(NODE_COLORS['physical_mapped'])
        else:
            node_colors.append(NODE_COLORS['physical'])

    nx.draw_networkx_nodes(
        G_physical, pos_physical,
        node_color=node_colors,
        node_size=600,
        alpha=0.8,
        ax=ax2
    )

    # Draw all edges first (background)
    nx.draw_networkx_edges(
        G_physical, pos_physical,
        edge_color=EDGE_COLORS['physical'],
        width=1,
        alpha=0.3,
        ax=ax2
    )

    # Draw mapped edges on top (highlighted)
    if mapped_physical_edges:
        nx.draw_networkx_edges(
            G_physical, pos_physical,
            edgelist=list(mapped_physical_edges),
            edge_color=EDGE_COLORS['physical_mapped'],
            width=3,
            alpha=0.8,
            ax=ax2
        )

    # Draw labels for mapped nodes
    mapped_labels = {node: node for node in mapped_physical_nodes}
    nx.draw_networkx_labels(
        G_physical, pos_physical,
        labels=mapped_labels,
        font_size=8,
        font_weight='bold',
        ax=ax2
    )

    ax2.set_title(f"Physical Network Mapping", fontsize=12, fontweight='bold')
    ax2.axis('off')

    # Add legend
    legend_elements = [
        mpatches.Patch(color=NODE_COLORS['slice'], label='Slice Node', alpha=0.8),
        mpatches.Patch(color=NODE_COLORS['physical_mapped'], label='Mapped Physical Node', alpha=0.8),
        mpatches.Patch(color=NODE_COLORS['physical'], label='Unmapped Physical Node', alpha=0.8),
        mpatches.Patch(color=EDGE_COLORS['physical_mapped'], label='Mapped Physical Link', alpha=0.8)
    ]
    fig.legend(handles=legend_elements, loc='upper center', ncol=4, fontsize=10,
              bbox_to_anchor=(0.5, 0.98))

    if title is None:
        title = f"Slice Mapping: {slice_request.slice_id}"
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.92)

    plt.tight_layout(rect=[0, 0, 1, 0.90])

    if output_path:
        fig.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor='white')
        print(f"  Saved figure: {output_path}")

    if show_plot:
        plt.show()

    return fig


def visualize_network_utilization_heatmap(
    physical_network: PhysicalNetwork,
    layout_type: str = 'positions',
    resource_type: str = 'cpu',
    title: Optional[str] = None,
    output_path: Optional[str] = None,
    show_plot: bool = False
) -> plt.Figure:
    """
    Create a heatmap visualization of resource utilization.

    Args:
        physical_network: Physical network
        layout_type: Layout algorithm
        resource_type: 'cpu' or 'bandwidth'
        title: Plot title
        output_path: Path to save the figure
        show_plot: Whether to display the plot

    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    G = physical_network.graph
    pos = create_network_layout(G, layout_type)

    if resource_type == 'cpu':
        # CPU utilization for nodes
        utilizations = []
        for node in G.nodes():
            cpu_available = physical_network.get_node_cpu_available(node)
            cpu_initial = physical_network.get_node_cpu_initial(node)
            util = 1 - (cpu_available / cpu_initial) if cpu_initial > 0 else 0
            utilizations.append(util)

        # Draw nodes with color based on utilization
        nodes = nx.draw_networkx_nodes(
            G, pos,
            node_color=utilizations,
            cmap='YlOrRd',
            vmin=0,
            vmax=1,
            node_size=1000,
            alpha=0.9,
            ax=ax
        )

        # Add colorbar
        cbar = plt.colorbar(nodes, ax=ax, label='CPU Utilization', fraction=0.046, pad=0.04)

    else:  # bandwidth
        # Bandwidth utilization for edges
        edge_utilizations = {}
        for u, v in G.edges():
            bw_available = physical_network.get_link_bandwidth_available(u, v)
            bw_initial = physical_network.get_link_bandwidth_initial(u, v)
            util = 1 - (bw_available / bw_initial) if bw_initial > 0 else 0
            edge_utilizations[(u, v)] = util

        # Draw nodes (simple)
        nx.draw_networkx_nodes(
            G, pos,
            node_color=NODE_COLORS['physical'],
            node_size=500,
            alpha=0.6,
            ax=ax
        )

        # Draw edges with color based on utilization
        edge_list = list(edge_utilizations.keys())
        edge_colors = [edge_utilizations[e] for e in edge_list]

        edges = nx.draw_networkx_edges(
            G, pos,
            edgelist=edge_list,
            edge_color=edge_colors,
            edge_cmap=plt.cm.YlOrRd,
            edge_vmin=0,
            edge_vmax=1,
            width=3,
            alpha=0.8,
            ax=ax
        )

        # Add colorbar (manually)
        sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, norm=plt.Normalize(vmin=0, vmax=1))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, label='Bandwidth Utilization', fraction=0.046, pad=0.04)

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)

    if title is None:
        title = f"{resource_type.upper()} Utilization Heatmap"
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor='white')
        print(f"  Saved figure: {output_path}")

    if show_plot:
        plt.show()

    return fig
