"""
Interactive Dashboard for 5G Network Slice Provisioning

Provides a web-based interface for:
- Real-time simulation visualization
- Interactive parameter tuning
- Performance metrics tracking
- Network topology visualization
"""

from .app import app, run_dashboard

__all__ = ['app', 'run_dashboard']
