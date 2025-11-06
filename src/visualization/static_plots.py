"""
Static Plot Generation Module

Generates Matplotlib plots to reproduce all figures from the paper:
- Figure 2: Slice acceptance ratio over time
- Figure 3a: Long-term average revenue
- Figure 3b: Revenue-to-cost ratio
- Figures 4-5: Results with varying link connection probability
- Figures 6-7: Results with varying arrival rate
- Figures 8-9: Results with varying network size
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import Dict, List, Tuple, Optional
import os
from pathlib import Path


# Plot styling constants
COLORS = {
    'RT-CSP': '#1f77b4',     # Blue
    'RT-CSP+': '#ff7f0e',    # Orange
    'grid': '#cccccc',
    'background': '#ffffff'
}

LINE_STYLES = {
    'RT-CSP': '-',
    'RT-CSP+': '--'
}

MARKERS = {
    'RT-CSP': 'o',
    'RT-CSP+': 's'
}

FIGURE_SIZE = (10, 6)
DPI = 300


def setup_plot_style():
    """Configure matplotlib style for publication-quality plots."""
    plt.rcParams['font.size'] = 12
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['figure.titlesize'] = 18
    plt.rcParams['lines.linewidth'] = 2
    plt.rcParams['lines.markersize'] = 8
    plt.rcParams['grid.alpha'] = 0.3


def save_figure(fig: plt.Figure, filename: str, output_dir: str = "output/figures"):
    """
    Save figure to file with high quality settings.

    Args:
        fig: Matplotlib figure
        filename: Output filename
        output_dir: Output directory path
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filepath = output_path / filename
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight', facecolor='white')
    print(f"  Saved figure: {filepath}")


def plot_acceptance_ratio_over_time(
    results_dict: Dict[str, Dict],
    output_dir: str = "output/figures",
    show_plot: bool = False
) -> plt.Figure:
    """
    Plot Figure 2: Slice acceptance ratio over time.

    Shows how the acceptance ratio changes as the simulation progresses,
    comparing RT-CSP and RT-CSP+.

    Args:
        results_dict: Dictionary with algorithm names as keys and results as values
                     Each result should contain 'time_series' with 'time' and 'acceptance_ratio'
        output_dir: Directory to save the figure
        show_plot: Whether to display the plot

    Returns:
        Matplotlib figure
    """
    setup_plot_style()
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    for algorithm, results in results_dict.items():
        time_series = results.get('time_series', {})
        times = time_series.get('time', [])
        acceptance_ratios = time_series.get('acceptance_ratio', [])

        if times and acceptance_ratios:
            # Convert to percentages
            acceptance_ratios_pct = [ratio * 100 for ratio in acceptance_ratios]

            ax.plot(
                times,
                acceptance_ratios_pct,
                label=algorithm,
                color=COLORS.get(algorithm, 'black'),
                linestyle=LINE_STYLES.get(algorithm, '-'),
                marker=MARKERS.get(algorithm, 'o'),
                markevery=max(len(times) // 10, 1),  # Show ~10 markers
                alpha=0.8
            )

    ax.set_xlabel('Simulation Time')
    ax.set_ylabel('Slice Acceptance Ratio (%)')
    ax.set_title('Slice Acceptance Ratio Over Time')
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 105])

    if output_dir:
        save_figure(fig, 'figure2_acceptance_ratio_time.png', output_dir)

    if show_plot:
        plt.show()

    return fig


def plot_revenue_comparison(
    results_dict: Dict[str, Dict],
    output_dir: str = "output/figures",
    show_plot: bool = False
) -> plt.Figure:
    """
    Plot Figure 3a: Long-term average revenue comparison.

    Bar chart comparing total revenue between algorithms.

    Args:
        results_dict: Dictionary with algorithm names and their results
        output_dir: Directory to save the figure
        show_plot: Whether to display the plot

    Returns:
        Matplotlib figure
    """
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(8, 6))

    algorithms = list(results_dict.keys())
    revenues = [results_dict[alg]['metrics']['total_revenue'] for alg in algorithms]

    x_pos = np.arange(len(algorithms))
    colors_list = [COLORS.get(alg, 'gray') for alg in algorithms]

    bars = ax.bar(x_pos, revenues, color=colors_list, alpha=0.8, edgecolor='black', linewidth=1.5)

    # Add value labels on bars
    for bar, revenue in zip(bars, revenues):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.,
            height,
            f'{revenue:.1f}',
            ha='center',
            va='bottom',
            fontsize=11,
            fontweight='bold'
        )

    ax.set_xlabel('Algorithm')
    ax.set_ylabel('Total Revenue')
    ax.set_title('Long-term Average Revenue')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(algorithms)
    ax.grid(axis='y', alpha=0.3)

    if output_dir:
        save_figure(fig, 'figure3a_revenue_comparison.png', output_dir)

    if show_plot:
        plt.show()

    return fig


def plot_revenue_cost_ratio(
    results_dict: Dict[str, Dict],
    output_dir: str = "output/figures",
    show_plot: bool = False
) -> plt.Figure:
    """
    Plot Figure 3b: Revenue-to-cost ratio comparison.

    Bar chart comparing revenue/cost ratio between algorithms.

    Args:
        results_dict: Dictionary with algorithm names and their results
        output_dir: Directory to save the figure
        show_plot: Whether to display the plot

    Returns:
        Matplotlib figure
    """
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(8, 6))

    algorithms = list(results_dict.keys())
    ratios = [results_dict[alg]['metrics']['revenue_cost_ratio'] for alg in algorithms]

    x_pos = np.arange(len(algorithms))
    colors_list = [COLORS.get(alg, 'gray') for alg in algorithms]

    bars = ax.bar(x_pos, ratios, color=colors_list, alpha=0.8, edgecolor='black', linewidth=1.5)

    # Add value labels on bars
    for bar, ratio in zip(bars, ratios):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.,
            height,
            f'{ratio:.3f}',
            ha='center',
            va='bottom',
            fontsize=11,
            fontweight='bold'
        )

    ax.set_xlabel('Algorithm')
    ax.set_ylabel('Revenue-to-Cost Ratio')
    ax.set_title('Revenue-to-Cost Ratio Comparison')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(algorithms)
    ax.grid(axis='y', alpha=0.3)

    if output_dir:
        save_figure(fig, 'figure3b_revenue_cost_ratio.png', output_dir)

    if show_plot:
        plt.show()

    return fig


def plot_varying_link_probability(
    experiment_results: Dict[float, Dict[str, Dict]],
    metric: str = 'acceptance_ratio',
    output_dir: str = "output/figures",
    show_plot: bool = False
) -> plt.Figure:
    """
    Plot Figures 4-5: Results with varying link connection probability.

    Line plot showing how performance varies with link probability (0.2, 0.5, 0.8).

    Args:
        experiment_results: Dict mapping link_prob -> {algorithm: results}
        metric: Metric to plot ('acceptance_ratio', 'revenue_cost_ratio', etc.)
        output_dir: Directory to save the figure
        show_plot: Whether to display the plot

    Returns:
        Matplotlib figure
    """
    setup_plot_style()
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    link_probs = sorted(experiment_results.keys())

    # Get all algorithms
    algorithms = list(next(iter(experiment_results.values())).keys())

    for algorithm in algorithms:
        metric_values = []
        for prob in link_probs:
            value = experiment_results[prob][algorithm]['metrics'][metric]
            # Convert to percentage if it's acceptance_ratio
            if metric == 'acceptance_ratio':
                value *= 100
            metric_values.append(value)

        ax.plot(
            link_probs,
            metric_values,
            label=algorithm,
            color=COLORS.get(algorithm, 'black'),
            linestyle=LINE_STYLES.get(algorithm, '-'),
            marker=MARKERS.get(algorithm, 'o'),
            markersize=10,
            alpha=0.8
        )

    ax.set_xlabel('Link Connection Probability')
    ax.set_ylabel(metric.replace('_', ' ').title() + (' (%)' if metric == 'acceptance_ratio' else ''))
    ax.set_title(f'{metric.replace("_", " ").title()} vs Link Connection Probability')
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(link_probs)

    if output_dir:
        filename = f'figure4_varying_link_prob_{metric}.png'
        save_figure(fig, filename, output_dir)

    if show_plot:
        plt.show()

    return fig


def plot_varying_arrival_rate(
    experiment_results: Dict[float, Dict[str, Dict]],
    metric: str = 'acceptance_ratio',
    output_dir: str = "output/figures",
    show_plot: bool = False
) -> plt.Figure:
    """
    Plot Figures 6-7: Results with varying arrival rate.

    Line plot showing how performance varies with arrival rate (0.02-0.1).

    Args:
        experiment_results: Dict mapping arrival_rate -> {algorithm: results}
        metric: Metric to plot ('acceptance_ratio', 'revenue_cost_ratio', etc.)
        output_dir: Directory to save the figure
        show_plot: Whether to display the plot

    Returns:
        Matplotlib figure
    """
    setup_plot_style()
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    arrival_rates = sorted(experiment_results.keys())

    # Get all algorithms
    algorithms = list(next(iter(experiment_results.values())).keys())

    for algorithm in algorithms:
        metric_values = []
        for rate in arrival_rates:
            value = experiment_results[rate][algorithm]['metrics'][metric]
            # Convert to percentage if it's acceptance_ratio
            if metric == 'acceptance_ratio':
                value *= 100
            metric_values.append(value)

        ax.plot(
            arrival_rates,
            metric_values,
            label=algorithm,
            color=COLORS.get(algorithm, 'black'),
            linestyle=LINE_STYLES.get(algorithm, '-'),
            marker=MARKERS.get(algorithm, 'o'),
            markersize=10,
            alpha=0.8
        )

    ax.set_xlabel('Arrival Rate (requests per time unit)')
    ax.set_ylabel(metric.replace('_', ' ').title() + (' (%)' if metric == 'acceptance_ratio' else ''))
    ax.set_title(f'{metric.replace("_", " ").title()} vs Arrival Rate')
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(arrival_rates)

    if output_dir:
        filename = f'figure6_varying_arrival_rate_{metric}.png'
        save_figure(fig, filename, output_dir)

    if show_plot:
        plt.show()

    return fig


def plot_varying_network_size(
    experiment_results: Dict[int, Dict[str, Dict]],
    metric: str = 'acceptance_ratio',
    output_dir: str = "output/figures",
    show_plot: bool = False
) -> plt.Figure:
    """
    Plot Figures 8-9: Results with varying network size.

    Line plot showing how performance varies with network size (50, 100, 150 nodes).

    Args:
        experiment_results: Dict mapping num_nodes -> {algorithm: results}
        metric: Metric to plot ('acceptance_ratio', 'revenue_cost_ratio', etc.)
        output_dir: Directory to save the figure
        show_plot: Whether to display the plot

    Returns:
        Matplotlib figure
    """
    setup_plot_style()
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    network_sizes = sorted(experiment_results.keys())

    # Get all algorithms
    algorithms = list(next(iter(experiment_results.values())).keys())

    for algorithm in algorithms:
        metric_values = []
        for size in network_sizes:
            value = experiment_results[size][algorithm]['metrics'][metric]
            # Convert to percentage if it's acceptance_ratio
            if metric == 'acceptance_ratio':
                value *= 100
            metric_values.append(value)

        ax.plot(
            network_sizes,
            metric_values,
            label=algorithm,
            color=COLORS.get(algorithm, 'black'),
            linestyle=LINE_STYLES.get(algorithm, '-'),
            marker=MARKERS.get(algorithm, 'o'),
            markersize=10,
            alpha=0.8
        )

    ax.set_xlabel('Number of Physical Nodes')
    ax.set_ylabel(metric.replace('_', ' ').title() + (' (%)' if metric == 'acceptance_ratio' else ''))
    ax.set_title(f'{metric.replace("_", " ").title()} vs Network Size')
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(network_sizes)

    if output_dir:
        filename = f'figure8_varying_network_size_{metric}.png'
        save_figure(fig, filename, output_dir)

    if show_plot:
        plt.show()

    return fig


def create_all_paper_figures(
    base_results: Dict[str, Dict],
    link_prob_results: Dict[float, Dict[str, Dict]],
    arrival_rate_results: Dict[float, Dict[str, Dict]],
    network_size_results: Dict[int, Dict[str, Dict]],
    output_dir: str = "output/figures",
    show_plots: bool = False
) -> Dict[str, plt.Figure]:
    """
    Generate all 8 figures from the paper at once.

    Args:
        base_results: Results for base case experiment
        link_prob_results: Results varying link probability
        arrival_rate_results: Results varying arrival rate
        network_size_results: Results varying network size
        output_dir: Directory to save figures
        show_plots: Whether to display plots

    Returns:
        Dictionary mapping figure names to figure objects
    """
    print("Generating all paper figures...")
    print("=" * 60)

    figures = {}

    # Figure 2: Acceptance ratio over time
    print("\nGenerating Figure 2: Acceptance Ratio Over Time")
    figures['figure2'] = plot_acceptance_ratio_over_time(
        base_results, output_dir, show_plots
    )

    # Figure 3a: Revenue comparison
    print("Generating Figure 3a: Revenue Comparison")
    figures['figure3a'] = plot_revenue_comparison(
        base_results, output_dir, show_plots
    )

    # Figure 3b: Revenue-to-cost ratio
    print("Generating Figure 3b: Revenue-to-Cost Ratio")
    figures['figure3b'] = plot_revenue_cost_ratio(
        base_results, output_dir, show_plots
    )

    # Figures 4-5: Varying link probability
    print("\nGenerating Figure 4: Acceptance Ratio vs Link Probability")
    figures['figure4_acceptance'] = plot_varying_link_probability(
        link_prob_results, 'acceptance_ratio', output_dir, show_plots
    )

    print("Generating Figure 5: Revenue-Cost Ratio vs Link Probability")
    figures['figure5_revenue_cost'] = plot_varying_link_probability(
        link_prob_results, 'revenue_cost_ratio', output_dir, show_plots
    )

    # Figures 6-7: Varying arrival rate
    print("\nGenerating Figure 6: Acceptance Ratio vs Arrival Rate")
    figures['figure6_acceptance'] = plot_varying_arrival_rate(
        arrival_rate_results, 'acceptance_ratio', output_dir, show_plots
    )

    print("Generating Figure 7: Revenue-Cost Ratio vs Arrival Rate")
    figures['figure7_revenue_cost'] = plot_varying_arrival_rate(
        arrival_rate_results, 'revenue_cost_ratio', output_dir, show_plots
    )

    # Figures 8-9: Varying network size
    print("\nGenerating Figure 8: Acceptance Ratio vs Network Size")
    figures['figure8_acceptance'] = plot_varying_network_size(
        network_size_results, 'acceptance_ratio', output_dir, show_plots
    )

    print("Generating Figure 9: Revenue-Cost Ratio vs Network Size")
    figures['figure9_revenue_cost'] = plot_varying_network_size(
        network_size_results, 'revenue_cost_ratio', output_dir, show_plots
    )

    print("\n" + "=" * 60)
    print(f"All figures saved to: {output_dir}")
    print("=" * 60)

    return figures


def plot_multi_metric_comparison(
    results_dict: Dict[str, Dict],
    metrics: List[str] = ['acceptance_ratio', 'total_revenue', 'revenue_cost_ratio'],
    output_dir: str = "output/figures",
    show_plot: bool = False
) -> plt.Figure:
    """
    Create a multi-panel plot comparing multiple metrics.

    Args:
        results_dict: Dictionary with algorithm names and their results
        metrics: List of metrics to plot
        output_dir: Directory to save the figure
        show_plot: Whether to display the plot

    Returns:
        Matplotlib figure
    """
    setup_plot_style()
    num_metrics = len(metrics)
    fig, axes = plt.subplots(1, num_metrics, figsize=(6 * num_metrics, 5))

    if num_metrics == 1:
        axes = [axes]

    algorithms = list(results_dict.keys())
    x_pos = np.arange(len(algorithms))
    colors_list = [COLORS.get(alg, 'gray') for alg in algorithms]

    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        values = [results_dict[alg]['metrics'][metric] for alg in algorithms]

        # Convert to percentage if it's acceptance_ratio
        if metric == 'acceptance_ratio':
            values = [v * 100 for v in values]
            ylabel = 'Acceptance Ratio (%)'
        else:
            ylabel = metric.replace('_', ' ').title()

        bars = ax.bar(x_pos, values, color=colors_list, alpha=0.8,
                     edgecolor='black', linewidth=1.5)

        # Add value labels
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'{value:.2f}',
                ha='center',
                va='bottom',
                fontsize=10,
                fontweight='bold'
            )

        ax.set_ylabel(ylabel)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(algorithms)
        ax.grid(axis='y', alpha=0.3)
        ax.set_title(ylabel)

    plt.tight_layout()

    if output_dir:
        save_figure(fig, 'multi_metric_comparison.png', output_dir)

    if show_plot:
        plt.show()

    return fig
