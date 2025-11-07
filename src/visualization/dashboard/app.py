"""
Interactive Dash Dashboard for 5G Network Slice Provisioning

Provides real-time visualization, parameter tuning, and performance analysis.
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from typing import Dict, List, Optional
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.simulation import (
    generate_physical_network,
    generate_slice_requests,
    SliceProvisioningSimulator
)

# Import callbacks
from .callbacks import register_callbacks

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

app.title = "5G Network Slice Provisioning Dashboard"

# Custom CSS for animations and improved UX
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Button animations */
            .btn {
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }

            .btn:active {
                transform: translateY(0);
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }

            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none !important;
            }

            /* Card animations */
            .card {
                transition: all 0.3s ease;
            }

            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            }

            /* Loading overlay */
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.7);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                backdrop-filter: blur(4px);
            }

            .loading-content {
                background: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }

            /* Spinner animation */
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .spinner-custom {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #007bff;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }

            /* Fade in animation */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .fade-in {
                animation: fadeIn 0.5s ease;
            }

            /* Progress bar */
            .progress {
                height: 25px;
                border-radius: 10px;
                overflow: hidden;
            }

            .progress-bar {
                transition: width 0.4s ease;
            }

            /* Status badge animations */
            .status-badge {
                transition: all 0.3s ease;
                display: inline-block;
            }

            .status-badge.pulse {
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.6; }
            }

            /* Smooth transitions for all interactive elements */
            input[type="range"] {
                transition: all 0.2s ease;
            }

            input[type="range"]:hover {
                cursor: pointer;
            }

            /* Alert animations */
            .alert {
                animation: slideIn 0.3s ease;
            }

            @keyframes slideIn {
                from { transform: translateX(-100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Global state for storing simulation results
simulation_state = {
    'physical_network': None,
    'simulator': None,
    'results': None,
    'is_running': False
}


def create_header():
    """Create dashboard header."""
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-network-wired me-2"),
                        html.Span("5G Network Slice Provisioning", className="fw-bold")
                    ], className="d-flex align-items-center")
                ], width="auto"),
            ], align="center"),
            dbc.Row([
                dbc.Col([
                    html.Small("RT-CSP & RT-CSP+ Algorithms", className="text-muted")
                ])
            ])
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4"
    )


def create_control_panel():
    """Create simulation control panel."""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-sliders-h me-2"),
            "Simulation Parameters"
        ]),
        dbc.CardBody([
            # Algorithm selection
            dbc.Row([
                dbc.Col([
                    dbc.Label("Algorithm"),
                    dcc.Dropdown(
                        id='algorithm-select',
                        options=[
                            {'label': 'RT-CSP', 'value': 'RT-CSP'},
                            {'label': 'RT-CSP+', 'value': 'RT-CSP+'},
                        ],
                        value='RT-CSP+',
                        clearable=False
                    )
                ], md=6),
                dbc.Col([
                    dbc.Label("Topology Model"),
                    dcc.Dropdown(
                        id='topology-select',
                        options=[
                            {'label': 'Waxman', 'value': 'waxman'},
                            {'label': 'ErdQs-R�nyi', 'value': 'erdos_renyi'},
                            {'label': 'Barab�si-Albert', 'value': 'barabasi_albert'},
                        ],
                        value='waxman',
                        clearable=False
                    )
                ], md=6)
            ], className="mb-3"),

            # Network size
            dbc.Row([
                dbc.Col([
                    dbc.Label(id='nodes-label', children="Physical Nodes: 100"),
                    dcc.Slider(
                        id='num-nodes-slider',
                        min=20,
                        max=200,
                        step=10,
                        value=100,
                        marks={i: str(i) for i in range(20, 201, 40)},
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ], md=12)
            ], className="mb-3"),

            # Number of requests
            dbc.Row([
                dbc.Col([
                    dbc.Label(id='requests-label', children="Slice Requests: 500"),
                    dcc.Slider(
                        id='num-requests-slider',
                        min=100,
                        max=2000,
                        step=100,
                        value=500,
                        marks={i: str(i) for i in range(100, 2001, 500)},
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ], md=12)
            ], className="mb-3"),

            # Arrival rate
            dbc.Row([
                dbc.Col([
                    dbc.Label(id='arrival-rate-label', children="Arrival Rate: 0.04"),
                    dcc.Slider(
                        id='arrival-rate-slider',
                        min=0.02,
                        max=0.1,
                        step=0.02,
                        value=0.04,
                        marks={i/100: f"{i/100:.2f}" for i in range(2, 11, 2)},
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ], md=12)
            ], className="mb-3"),

            # Link probability
            dbc.Row([
                dbc.Col([
                    dbc.Label(id='link-prob-label', children="Link Probability: 0.5"),
                    dcc.Slider(
                        id='link-prob-slider',
                        min=0.2,
                        max=0.8,
                        step=0.1,
                        value=0.5,
                        marks={i/10: f"{i/10:.1f}" for i in range(2, 9, 2)},
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ], md=12)
            ], className="mb-3"),

            # Control buttons
            dbc.Row([
                dbc.Col([
                    dcc.Loading(
                        id="loading-run-button",
                        type="default",
                        children=dbc.Button(
                            [html.I(className="fas fa-play me-2"), "Run Simulation"],
                            id='run-button',
                            color="success",
                            className="w-100"
                        )
                    )
                ], md=6),
                dbc.Col([
                    dbc.Button(
                        [html.I(className="fas fa-redo me-2"), "Reset"],
                        id='reset-button',
                        color="secondary",
                        className="w-100"
                    )
                ], md=6)
            ])
        ])
    ])


def create_metrics_cards():
    """Create metric summary cards with hover animations."""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-check-circle fa-2x mb-2 text-success"),
                        html.H4(id='acceptance-ratio-card', children="--", className="text-success mb-0"),
                        html.P("Acceptance Ratio", className="text-muted mb-0 small")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-dollar-sign fa-2x mb-2 text-primary"),
                        html.H4(id='total-revenue-card', children="--", className="text-primary mb-0"),
                        html.P("Total Revenue", className="text-muted mb-0 small")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chart-line fa-2x mb-2 text-info"),
                        html.H4(id='revenue-cost-card', children="--", className="text-info mb-0"),
                        html.P("Revenue/Cost Ratio", className="text-muted mb-0 small")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-tasks fa-2x mb-2 text-warning"),
                        html.H4(id='accepted-requests-card', children="--", className="text-warning mb-0"),
                        html.P("Accepted Requests", className="text-muted mb-0 small")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], md=3)
    ], className="mb-4 fade-in")


def create_main_layout():
    """Create main dashboard layout with enhanced UX."""
    return dbc.Container([
        create_header(),

        # Toast notifications container
        html.Div(id='toast-container', style={'position': 'fixed', 'top': 80, 'right': 20, 'zIndex': 9999}),

        # Loading overlay
        html.Div(id='loading-overlay', style={'display': 'none'}),

        # Confirmation modal for reset
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle([
                html.I(className="fas fa-exclamation-triangle me-2 text-warning"),
                "Confirm Reset"
            ])),
            dbc.ModalBody([
                html.P("Are you sure you want to reset the dashboard?"),
                html.P("This will clear all simulation results and you'll need to run a new simulation.",
                       className="text-muted small")
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="reset-cancel", color="secondary", className="me-2"),
                dbc.Button([
                    html.I(className="fas fa-redo me-2"),
                    "Reset"
                ], id="reset-confirm", color="danger")
            ])
        ], id="reset-modal", is_open=False),

        dbc.Row([
            # Left panel - Controls
            dbc.Col([
                create_control_panel(),
                html.Div(id='simulation-status', className="mt-3"),
                # Progress indicator
                html.Div(id='progress-container', style={'display': 'none'}, children=[
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Simulation Progress", className="mb-3"),
                            dbc.Progress(id='simulation-progress', value=0, className="mb-2"),
                            html.P(id='progress-text', className="small text-muted mb-0")
                        ])
                    ], className="mt-3")
                ])
            ], md=3),

            # Right panel - Visualizations
            dbc.Col([
                create_metrics_cards(),

                # Tabs for different views
                dbc.Tabs([
                    dbc.Tab([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Loading(
                                    id="loading-acceptance",
                                    type="circle",
                                    children=dcc.Graph(id='acceptance-ratio-plot', style={'height': '400px'})
                                ),
                            ])
                        ], className="mt-3 shadow-sm")
                    ], label="Acceptance Ratio", tab_id="tab-acceptance"),

                    dbc.Tab([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Loading(
                                    id="loading-revenue",
                                    type="circle",
                                    children=dcc.Graph(id='revenue-plot', style={'height': '400px'})
                                ),
                            ])
                        ], className="mt-3 shadow-sm")
                    ], label="Revenue", tab_id="tab-revenue"),

                    dbc.Tab([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Loading(
                                    id="loading-utilization",
                                    type="circle",
                                    children=dcc.Graph(id='utilization-plot', style={'height': '400px'})
                                ),
                            ])
                        ], className="mt-3 shadow-sm")
                    ], label="Resource Utilization", tab_id="tab-utilization"),

                    dbc.Tab([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Loading(
                                    id="loading-network",
                                    type="circle",
                                    children=dcc.Graph(id='network-topology-plot', style={'height': '500px'})
                                ),
                            ])
                        ], className="mt-3 shadow-sm")
                    ], label="Network Topology", tab_id="tab-network"),

                    dbc.Tab([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Loading(
                                    id="loading-stats",
                                    type="circle",
                                    children=html.Div(id='detailed-stats')
                                ),
                            ])
                        ], className="mt-3 shadow-sm")
                    ], label="Detailed Stats", tab_id="tab-stats")
                ], id="tabs", active_tab="tab-acceptance")
            ], md=9)
        ]),

        # Hidden div to store simulation data
        dcc.Store(id='simulation-data'),
        dcc.Store(id='network-data'),
        dcc.Store(id='is-running', data=False)

    ], fluid=True)


# Set the layout
app.layout = create_main_layout()

# Register callbacks
register_callbacks(app)


def run_dashboard(host='127.0.0.1', port=8050, debug=True):
    """
    Launch the dashboard application.

    Args:
        host: Host address
        port: Port number
        debug: Enable debug mode
    """
    print("\n" + "=" * 70)
    print("5G Network Slice Provisioning Dashboard")
    print("=" * 70)
    print(f"\nStarting dashboard at http://{host}:{port}")
    print("\nFeatures:")
    print("  - Real-time simulation visualization")
    print("  - Interactive parameter tuning")
    print("  - Network topology visualization")
    print("  - Performance metrics tracking")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70 + "\n")

    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_dashboard()
