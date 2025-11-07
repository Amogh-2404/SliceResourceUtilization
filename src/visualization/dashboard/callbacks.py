"""
Dashboard Callbacks

Handles all interactive callbacks for the Dash dashboard.
"""

from dash import Input, Output, State, callback
from dash import html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import json
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.simulation import (
    generate_physical_network,
    generate_slice_requests,
    SliceProvisioningSimulator
)


def register_callbacks(app):
    """Register all dashboard callbacks."""

    # Update slider labels
    @app.callback(
        Output('nodes-label', 'children'),
        Input('num-nodes-slider', 'value')
    )
    def update_nodes_label(value):
        return f"Physical Nodes: {value}"

    @app.callback(
        Output('requests-label', 'children'),
        Input('num-requests-slider', 'value')
    )
    def update_requests_label(value):
        return f"Slice Requests: {value}"

    @app.callback(
        Output('arrival-rate-label', 'children'),
        Input('arrival-rate-slider', 'value')
    )
    def update_arrival_rate_label(value):
        return f"Arrival Rate: {value:.2f}"

    @app.callback(
        Output('link-prob-label', 'children'),
        Input('link-prob-slider', 'value')
    )
    def update_link_prob_label(value):
        return f"Link Probability: {value:.1f}"

    # Run simulation with enhanced UX
    @app.callback(
        [
            Output('simulation-data', 'data'),
            Output('network-data', 'data'),
            Output('simulation-status', 'children'),
            Output('loading-overlay', 'style'),
            Output('loading-overlay', 'children'),
            Output('run-button', 'disabled'),
            Output('reset-button', 'disabled'),
            Output('toast-container', 'children'),
            Output('progress-container', 'style'),
            Output('simulation-progress', 'value'),
            Output('progress-text', 'children')
        ],
        [Input('run-button', 'n_clicks')],
        [
            State('algorithm-select', 'value'),
            State('topology-select', 'value'),
            State('num-nodes-slider', 'value'),
            State('num-requests-slider', 'value'),
            State('arrival-rate-slider', 'value'),
            State('link-prob-slider', 'value')
        ],
        prevent_initial_call=True
    )
    def run_simulation(n_clicks, algorithm, topology, num_nodes, num_requests, arrival_rate, link_prob):
        if n_clicks is None:
            return None, None, "", {'display': 'none'}, None, False, False, None, {'display': 'none'}, 0, ""

        try:
            # Show loading overlay
            loading_overlay = html.Div([
                html.Div([
                    html.Div(className="spinner-custom"),
                    html.H4("Running Simulation...", className="text-primary"),
                    html.P(f"Provisioning {num_requests} slice requests on {num_nodes} nodes", className="text-muted"),
                    html.P(f"Algorithm: {algorithm}", className="small text-muted")
                ], className="loading-content")
            ], className="loading-overlay")

            # Progress indication
            progress_style = {'display': 'block'}

            # Step 1: Generate physical network (20% progress)
            physical_network = generate_physical_network(
                num_nodes=num_nodes,
                topology_model=topology,
                random_seed=42
            )
            progress_val = 20
            progress_msg = f"Generated physical network with {physical_network.num_nodes()} nodes"

            # Store network data
            network_data = {
                'num_nodes': physical_network.num_nodes(),
                'num_links': physical_network.num_links()
            }

            # Step 2: Generate slice requests (40% progress)
            slice_requests = generate_slice_requests(
                num_requests=num_requests,
                arrival_rate=arrival_rate,
                connection_probability=link_prob,
                random_seed=42
            )
            progress_val = 40
            progress_msg = f"Generated {len(slice_requests)} slice requests"

            # Step 3: Run simulation (80% progress)
            simulator = SliceProvisioningSimulator(
                physical_network=physical_network,
                algorithm=algorithm,
                verbose=False
            )
            simulator.add_slice_requests(slice_requests)
            progress_val = 60
            progress_msg = "Running provisioning simulation..."

            results = simulator.run()
            progress_val = 100
            progress_msg = "Simulation complete!"

            # Success status
            status = dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                html.Span([
                    html.Strong("Success! "),
                    f"Accepted {results['metrics']['accepted_requests']}/{num_requests} requests ",
                    f"({results['metrics']['acceptance_ratio']:.1%} acceptance ratio)"
                ])
            ], color="success", className="fade-in")

            # Toast notification
            toast = dbc.Toast([
                html.I(className="fas fa-check-circle me-2 text-success"),
                f"Simulation completed successfully!"
            ], header=f"{algorithm} Results", icon="success", duration=4000, is_open=True,
               style={"position": "fixed", "top": 80, "right": 20, "minWidth": 350})

            # Hide loading overlay, enable buttons
            return (json.dumps(results, default=str), json.dumps(network_data), status,
                    {'display': 'none'}, None, False, False, toast,
                    {'display': 'none'}, 100, "Complete")

        except Exception as e:
            # Error status
            status = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                html.Span([
                    html.Strong("Error: "),
                    str(e)
                ])
            ], color="danger", className="fade-in")

            # Error toast
            toast = dbc.Toast([
                html.I(className="fas fa-exclamation-triangle me-2 text-danger"),
                "Simulation failed. Please check parameters."
            ], header="Error", icon="danger", duration=4000, is_open=True,
               style={"position": "fixed", "top": 80, "right": 20, "minWidth": 350})

            return (None, None, status, {'display': 'none'}, None, False, False, toast,
                    {'display': 'none'}, 0, "")

    # Update metric cards
    @app.callback(
        [
            Output('acceptance-ratio-card', 'children'),
            Output('total-revenue-card', 'children'),
            Output('revenue-cost-card', 'children'),
            Output('accepted-requests-card', 'children')
        ],
        Input('simulation-data', 'data')
    )
    def update_metric_cards(data):
        if data is None:
            return "--", "--", "--", "--"

        results = json.loads(data)
        metrics = results['metrics']

        acceptance = f"{metrics['acceptance_ratio']:.1%}"
        revenue = f"${metrics['total_revenue']:.0f}"
        revenue_cost = f"{metrics['revenue_cost_ratio']:.3f}"
        accepted = f"{metrics['accepted_requests']}"

        return acceptance, revenue, revenue_cost, accepted

    # Update acceptance ratio plot
    @app.callback(
        Output('acceptance-ratio-plot', 'figure'),
        Input('simulation-data', 'data')
    )
    def update_acceptance_plot(data):
        if data is None:
            # Empty plot
            fig = go.Figure()
            fig.update_layout(
                title="Run a simulation to see results",
                xaxis_title="Simulation Time",
                yaxis_title="Acceptance Ratio (%)",
                template="plotly_white"
            )
            return fig

        results = json.loads(data)
        time_series = results['time_series']

        fig = go.Figure()

        # Add time series line
        if 'time' in time_series and 'acceptance_ratio' in time_series:
            times = time_series['time']
            ratios = [r * 100 for r in time_series['acceptance_ratio']]

            fig.add_trace(go.Scatter(
                x=times,
                y=ratios,
                mode='lines+markers',
                name='Acceptance Ratio',
                line=dict(color='#28a745', width=2),
                marker=dict(size=6)
            ))

        fig.update_layout(
            title=f"Acceptance Ratio Over Time ({results['algorithm']})",
            xaxis_title="Simulation Time",
            yaxis_title="Acceptance Ratio (%)",
            template="plotly_white",
            hovermode='x unified'
        )

        return fig

    # Update revenue plot
    @app.callback(
        Output('revenue-plot', 'figure'),
        Input('simulation-data', 'data')
    )
    def update_revenue_plot(data):
        if data is None:
            fig = go.Figure()
            fig.update_layout(
                title="Run a simulation to see results",
                template="plotly_white"
            )
            return fig

        results = json.loads(data)
        metrics = results['metrics']

        fig = go.Figure()

        # Bar chart with revenue and cost
        fig.add_trace(go.Bar(
            x=['Total Revenue', 'Total Cost'],
            y=[metrics['total_revenue'], metrics['total_cost']],
            marker_color=['#007bff', '#dc3545'],
            text=[f"${metrics['total_revenue']:.0f}", f"${metrics['total_cost']:.0f}"],
            textposition='auto'
        ))

        fig.update_layout(
            title=f"Revenue and Cost ({results['algorithm']})",
            yaxis_title="Amount ($)",
            template="plotly_white",
            showlegend=False
        )

        return fig

    # Update utilization plot
    @app.callback(
        Output('utilization-plot', 'figure'),
        Input('simulation-data', 'data')
    )
    def update_utilization_plot(data):
        if data is None:
            fig = go.Figure()
            fig.update_layout(
                title="Run a simulation to see results",
                template="plotly_white"
            )
            return fig

        results = json.loads(data)
        util = results['final_utilization']

        fig = go.Figure()

        # Bar chart for CPU and bandwidth utilization
        fig.add_trace(go.Bar(
            x=['CPU Utilization', 'Bandwidth Utilization'],
            y=[util['cpu_utilization_percent'], util['bandwidth_utilization_percent']],
            marker_color=['#17a2b8', '#ffc107'],
            text=[f"{util['cpu_utilization_percent']:.1f}%",
                  f"{util['bandwidth_utilization_percent']:.1f}%"],
            textposition='auto'
        ))

        fig.update_layout(
            title="Final Resource Utilization",
            yaxis_title="Utilization (%)",
            template="plotly_white",
            showlegend=False,
            yaxis=dict(range=[0, 100])
        )

        return fig

    # Update network topology plot
    @app.callback(
        Output('network-topology-plot', 'figure'),
        Input('network-data', 'data')
    )
    def update_network_plot(data):
        if data is None:
            fig = go.Figure()
            fig.update_layout(
                title="Run a simulation to see network topology",
                template="plotly_white"
            )
            return fig

        network_data = json.loads(data)

        # Create a simple network visualization
        fig = go.Figure()

        # For now, just show network statistics
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=network_data['num_nodes'],
            title={'text': "Physical Nodes"},
            domain={'x': [0, 0.5], 'y': [0.5, 1]}
        ))

        fig.add_trace(go.Indicator(
            mode="number",
            value=network_data['num_links'],
            title={'text': "Physical Links"},
            domain={'x': [0.5, 1], 'y': [0.5, 1]}
        ))

        # Calculate average degree
        avg_degree = (2 * network_data['num_links']) / network_data['num_nodes'] if network_data['num_nodes'] > 0 else 0

        fig.add_trace(go.Indicator(
            mode="number",
            value=avg_degree,
            title={'text': "Average Node Degree"},
            domain={'x': [0.25, 0.75], 'y': [0, 0.5]}
        ))

        fig.update_layout(
            title="Network Statistics",
            template="plotly_white"
        )

        return fig

    # Update detailed stats
    @app.callback(
        Output('detailed-stats', 'children'),
        Input('simulation-data', 'data')
    )
    def update_detailed_stats(data):
        if data is None:
            return html.P("Run a simulation to see detailed statistics.", className="text-muted")

        results = json.loads(data)
        metrics = results['metrics']

        stats_table = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Metric"),
                    html.Th("Value")
                ])
            ]),
            html.Tbody([
                html.Tr([html.Td("Algorithm"), html.Td(results['algorithm'])]),
                html.Tr([html.Td("Simulation Time"), html.Td(f"{results['simulation_time']:.2f}")]),
                html.Tr([html.Td("Total Arrivals"), html.Td(str(results['total_arrivals']))]),
                html.Tr([html.Td("Total Departures"), html.Td(str(results['total_departures']))]),
                html.Tr([html.Td("Accepted Requests"), html.Td(str(metrics['accepted_requests']))]),
                html.Tr([html.Td("Rejected Requests"), html.Td(str(metrics['rejected_requests']))]),
                html.Tr([html.Td("Acceptance Ratio"), html.Td(f"{metrics['acceptance_ratio']:.2%}")]),
                html.Tr([html.Td("Total Revenue"), html.Td(f"${metrics['total_revenue']:.2f}")]),
                html.Tr([html.Td("Total Cost"), html.Td(f"${metrics['total_cost']:.2f}")]),
                html.Tr([html.Td("Revenue/Cost Ratio"), html.Td(f"{metrics['revenue_cost_ratio']:.3f}")]),
                html.Tr([html.Td("Average Revenue per Slice"), html.Td(f"${metrics.get('average_revenue', 0):.2f}")]),
                html.Tr([html.Td("Physical Nodes"), html.Td(str(results['physical_network_stats']['num_nodes']))]),
                html.Tr([html.Td("Physical Links"), html.Td(str(results['physical_network_stats']['num_links']))]),
                html.Tr([html.Td("CPU Utilization"), html.Td(f"{results['final_utilization']['cpu_utilization_percent']:.2f}%")]),
                html.Tr([html.Td("Bandwidth Utilization"), html.Td(f"{results['final_utilization']['bandwidth_utilization_percent']:.2f}%")]),
            ])
        ], bordered=True, hover=True, striped=True)

        return stats_table

    # Show reset confirmation modal
    @app.callback(
        Output('reset-modal', 'is_open'),
        [Input('reset-button', 'n_clicks'), Input('reset-confirm', 'n_clicks'), Input('reset-cancel', 'n_clicks')],
        [State('reset-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_reset_modal(reset_click, confirm_click, cancel_click, is_open):
        from dash.ctx import triggered_id

        if triggered_id == 'reset-button':
            return True
        elif triggered_id in ['reset-confirm', 'reset-cancel']:
            return False
        return is_open

    # Reset simulation with confirmation
    @app.callback(
        [
            Output('simulation-data', 'data', allow_duplicate=True),
            Output('network-data', 'data', allow_duplicate=True),
            Output('simulation-status', 'children', allow_duplicate=True),
            Output('toast-container', 'children', allow_duplicate=True)
        ],
        Input('reset-confirm', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_simulation(n_clicks):
        if n_clicks is None:
            return None, None, "", None

        status = dbc.Alert([
            html.I(className="fas fa-info-circle me-2"),
            html.Span([
                html.Strong("Dashboard Reset. "),
                "Configure parameters and run a new simulation to see results."
            ])
        ], color="info", className="fade-in")

        # Toast notification
        toast = dbc.Toast([
            html.I(className="fas fa-redo me-2 text-info"),
            "Dashboard has been reset successfully."
        ], header="Reset Complete", icon="info", duration=3000, is_open=True,
           style={"position": "fixed", "top": 80, "right": 20, "minWidth": 350})

        return None, None, status, toast
