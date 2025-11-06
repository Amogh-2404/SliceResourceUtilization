#!/usr/bin/env python3
"""
Dashboard Launcher Script

Quick launcher for the 5G Network Slice Provisioning Dashboard.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.visualization.dashboard import run_dashboard


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Launch the 5G Network Slice Provisioning Dashboard"
    )
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Host address (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8050,
        help='Port number (default: 8050)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )

    args = parser.parse_args()

    run_dashboard(host=args.host, port=args.port, debug=args.debug)
