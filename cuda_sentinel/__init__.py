"""
CUDA Sentinel - GPU Health Monitoring and Benchmarking Tool

A comprehensive toolkit for monitoring NVIDIA GPU health, performance,
and running diagnostics using the NVIDIA Management Library (NVML).

Main features:
- Real-time GPU monitoring
- Health status analysis  
- Performance benchmarking
- Multiple export formats
- CLI interface
"""

__version__ = "0.1.0"
__author__ = "CUDA Sentinel Team"
__license__ = "MIT"

from .core.collector import GPUCollector
from .core.models import GPUInfo, GPUMetrics, HealthStatus, HealthReport

__all__ = [
    "GPUCollector", 
    "GPUInfo", 
    "GPUMetrics", 
    "HealthStatus", 
    "HealthReport"
]
