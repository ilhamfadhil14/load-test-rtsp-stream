"""
RTSP Load Tester

A Python-based RTSP stream publisher for load testing AI video processing pipelines.
Publishes multiple looping video streams simultaneously to test parallel processing capabilities.
"""

__version__ = "0.1.0"

from .orchestrator import LoadTestOrchestrator
from .stream_publisher import RTSPStreamPublisher

__all__ = ["LoadTestOrchestrator", "RTSPStreamPublisher"]
