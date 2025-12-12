"""
Load Test Orchestrator
Manages multiple RTSP streams for load testing
"""

import time
import signal
import sys
import json
from typing import List, Dict, Any
from pathlib import Path
from loguru import logger
import psutil

from .stream_publisher import RTSPStreamPublisher


class LoadTestOrchestrator:
    """Orchestrates multiple RTSP streams for load testing"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the load test orchestrator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.publishers: List[RTSPStreamPublisher] = []
        self.running = False
        self.start_time: float = 0
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Setup logging
        self._setup_logging()
        
        # Validate configuration
        self._validate_config()
    
    def _setup_logging(self):
        """Configure logging"""
        log_level = self.config.get("monitoring", {}).get("log_level", "INFO")
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Configure loguru
        logger.remove()  # Remove default handler
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
        )
        logger.add(
            "logs/rtsp_load_test_{time}.log",
            rotation="100 MB",
            retention="7 days",
            level=log_level
        )
    
    def _validate_config(self):
        """Validate configuration"""
        # Support both old (video_sources) and new (video) config formats
        if not self.config.get("video_sources") and not self.config.get("video"):
            raise ValueError("No video source configured (use 'video' section)")

        if not self.config.get("rtsp_server"):
            raise ValueError("RTSP server configuration missing")

        # Check max streams limit
        max_streams = self.config.get("limits", {}).get("max_streams", 50)
        concurrent_streams = self.config.get("load_test", {}).get("concurrent_streams", 1)

        if concurrent_streams > max_streams:
            raise ValueError(
                f"Concurrent streams ({concurrent_streams}) exceeds max limit ({max_streams})"
            )
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def create_publishers(self):
        """Create stream publishers based on configuration"""
        rtsp_base_url = self.config["rtsp_server"]["base_url"]
        publisher_config = self.config.get("publisher", {})

        # Check if using new config format (single video for all streams)
        if self.config.get("video"):
            video_config = self.config["video"]
            video_path = video_config["path"]
            loop = video_config.get("loop", True)
            fps = video_config.get("fps", 30)

            # Get number of concurrent streams
            concurrent_streams = self.config.get("load_test", {}).get("concurrent_streams", 3)

            # Create multiple publishers from the same video
            for i in range(1, concurrent_streams + 1):
                stream_name = f"stream{i}"
                rtsp_url = f"{rtsp_base_url}/{stream_name}"

                publisher = RTSPStreamPublisher(
                    stream_name=stream_name,
                    video_path=video_path,
                    rtsp_url=rtsp_url,
                    loop=loop,
                    fps=fps,
                    codec=publisher_config.get("codec", "libx264"),
                    preset=publisher_config.get("preset", "ultrafast"),
                    bitrate=publisher_config.get("bitrate", "2M"),
                    pixel_format=publisher_config.get("pixel_format", "yuv420p")
                )

                self.publishers.append(publisher)
                logger.info(f"Created publisher for stream: {stream_name}")

        # Support old config format (video_sources array)
        elif self.config.get("video_sources"):
            video_sources = self.config["video_sources"]

            for source in video_sources:
                stream_name = source["name"]
                video_path = source["video_path"]
                rtsp_url = f"{rtsp_base_url}/{stream_name}"

                # Create publisher
                publisher = RTSPStreamPublisher(
                    stream_name=stream_name,
                    video_path=video_path,
                    rtsp_url=rtsp_url,
                    loop=source.get("loop", True),
                    fps=source.get("fps", 30),
                    codec=publisher_config.get("codec", "libx264"),
                    preset=publisher_config.get("preset", "ultrafast"),
                    bitrate=publisher_config.get("bitrate", "2M"),
                    pixel_format=publisher_config.get("pixel_format", "yuv420p")
                )

                self.publishers.append(publisher)
                logger.info(f"Created publisher for stream: {stream_name}")

        logger.info(f"Created {len(self.publishers)} stream publishers")
    
    def start(self):
        """Start all stream publishers"""
        if self.running:
            logger.warning("Load test already running")
            return
        
        if not self.publishers:
            self.create_publishers()
        
        self.running = True
        self.start_time = time.time()
        
        logger.info("=" * 60)
        logger.info("Starting RTSP Load Test")
        logger.info("=" * 60)
        
        # Start all publishers
        for publisher in self.publishers:
            try:
                publisher.start()
                time.sleep(0.5)  # Small delay between starts
            except Exception as e:
                logger.error(f"Failed to start publisher {publisher.stream_name}: {e}")
        
        logger.info(f"Started {len(self.publishers)} streams")
        
        # Start monitoring loop
        self._monitoring_loop()
    
    def _monitoring_loop(self):
        """Monitor streams and system resources"""
        report_interval = self.config.get("load_test", {}).get("report_interval", 10)
        duration = self.config.get("load_test", {}).get("duration", 0)
        
        last_report_time = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                elapsed = current_time - self.start_time
                
                # Check duration limit
                if duration > 0 and elapsed >= duration:
                    logger.info(f"Test duration reached ({duration}s), stopping...")
                    break
                
                # Periodic status report
                if current_time - last_report_time >= report_interval:
                    self._print_status_report()
                    last_report_time = current_time
                
                # Check resource limits
                self._check_resource_limits()
                
                # Check stream health
                self._check_stream_health()
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
        
        self.stop()
    
    def _print_status_report(self):
        """Print status report"""
        logger.info("=" * 60)
        logger.info("STATUS REPORT")
        logger.info("=" * 60)
        
        # System resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        logger.info(f"System CPU: {cpu_percent:.1f}%")
        logger.info(f"System Memory: {memory.percent:.1f}% ({memory.used / 1024**3:.2f}GB / {memory.total / 1024**3:.2f}GB)")
        
        # Stream statistics
        healthy_count = sum(1 for p in self.publishers if p.is_healthy())
        logger.info(f"Streams: {healthy_count}/{len(self.publishers)} healthy")
        
        # Individual stream stats
        for publisher in self.publishers:
            stats = publisher.get_stats()
            status = "✓" if stats["is_alive"] else "✗"
            logger.info(
                f"  {status} {stats['stream_name']}: "
                f"Uptime={stats['uptime_seconds']:.0f}s, "
                f"Errors={stats['error_count']}, "
                f"Resolution={stats['resolution']}"
            )
        
        logger.info("=" * 60)
    
    def _check_resource_limits(self):
        """Check if resource limits are exceeded"""
        limits = self.config.get("limits", {})
        
        # Memory check
        max_memory = limits.get("max_memory_percent", 80)
        memory_percent = psutil.virtual_memory().percent
        
        if memory_percent > max_memory:
            logger.error(
                f"Memory usage ({memory_percent:.1f}%) exceeds limit ({max_memory}%). "
                "Stopping test..."
            )
            self.stop()
        
        # CPU check (warning only)
        max_cpu = limits.get("max_cpu_percent", 90)
        cpu_percent = psutil.cpu_percent(interval=1)
        
        if cpu_percent > max_cpu:
            logger.warning(f"CPU usage ({cpu_percent:.1f}%) exceeds limit ({max_cpu}%)")
    
    def _check_stream_health(self):
        """Check health of all streams"""
        unhealthy_streams = [p for p in self.publishers if not p.is_healthy()]
        
        if unhealthy_streams:
            logger.warning(f"Found {len(unhealthy_streams)} unhealthy streams")
            
            for publisher in unhealthy_streams:
                if publisher.error_count >= 10:
                    logger.error(
                        f"Stream {publisher.stream_name} has too many errors, stopping it"
                    )
                    publisher.stop()
    
    def stop(self):
        """Stop all stream publishers"""
        if not self.running:
            return
        
        logger.info("Stopping all streams...")
        self.running = False
        
        # Stop all publishers
        for publisher in self.publishers:
            try:
                publisher.stop()
            except Exception as e:
                logger.error(f"Error stopping publisher {publisher.stream_name}: {e}")
        
        # Generate final report
        self._generate_final_report()
        
        logger.info("Load test stopped")
    
    def _generate_final_report(self):
        """Generate final test report"""
        elapsed = time.time() - self.start_time
        
        report = {
            "test_duration_seconds": elapsed,
            "total_streams": len(self.publishers),
            "streams": []
        }
        
        logger.info("=" * 60)
        logger.info("FINAL REPORT")
        logger.info("=" * 60)
        logger.info(f"Test Duration: {elapsed:.2f}s ({elapsed/60:.2f} minutes)")
        logger.info(f"Total Streams: {len(self.publishers)}")
        
        for publisher in self.publishers:
            stats = publisher.get_stats()
            report["streams"].append(stats)
            
            logger.info(f"\nStream: {stats['stream_name']}")
            logger.info(f"  URL: {stats['rtsp_url']}")
            logger.info(f"  Uptime: {stats['uptime_seconds']:.2f}s")
            logger.info(f"  Errors: {stats['error_count']}")
            logger.info(f"  Resolution: {stats['resolution']}")
        
        # Save report to file
        if self.config.get("monitoring", {}).get("enabled", True):
            metrics_file = self.config.get("monitoring", {}).get("metrics_file", "logs/metrics.json")
            Path(metrics_file).parent.mkdir(exist_ok=True)
            
            with open(metrics_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"\nReport saved to: {metrics_file}")
        
        logger.info("=" * 60)
    
    def get_stream_urls(self) -> List[str]:
        """Get list of all stream URLs"""
        return [p.rtsp_url for p in self.publishers]
