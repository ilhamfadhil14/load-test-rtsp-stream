"""
RTSP Stream Publisher
Handles publishing video files to RTSP streams using FFmpeg
"""

import subprocess
import threading
import time
import os
from typing import Optional, Dict, Any
from loguru import logger
import cv2


class RTSPStreamPublisher:
    """Publishes a video file to an RTSP stream with looping support"""
    
    def __init__(
        self,
        stream_name: str,
        video_path: str,
        rtsp_url: str,
        loop: bool = True,
        fps: int = 30,
        codec: str = "libx264",
        preset: str = "ultrafast",
        bitrate: str = "2M",
        pixel_format: str = "yuv420p"
    ):
        """
        Initialize RTSP stream publisher
        
        Args:
            stream_name: Unique name for this stream
            video_path: Path to video file
            rtsp_url: Full RTSP URL to publish to
            loop: Whether to loop the video
            fps: Frames per second
            codec: Video codec to use
            preset: Encoding preset
            bitrate: Video bitrate
            pixel_format: Pixel format
        """
        self.stream_name = stream_name
        self.video_path = video_path
        self.rtsp_url = rtsp_url
        self.loop = loop
        self.fps = fps
        self.codec = codec
        self.preset = preset
        self.bitrate = bitrate
        self.pixel_format = pixel_format
        
        self.process: Optional[subprocess.Popen] = None
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self.error_count = 0
        self.frame_count = 0
        self.start_time: Optional[float] = None
        
        # Validate video file
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Get video properties
        self._get_video_properties()
        
    def _get_video_properties(self):
        """Extract video properties using OpenCV"""
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {self.video_path}")
        
        self.video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.video_fps = cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.video_fps if self.video_fps > 0 else 0
        
        cap.release()
        
        logger.info(
            f"[{self.stream_name}] Video properties: "
            f"{self.video_width}x{self.video_height} @ {self.video_fps}fps, "
            f"{self.total_frames} frames, {self.duration:.2f}s duration"
        )
    
    def _build_ffmpeg_command(self) -> list:
        """Build FFmpeg command for streaming"""
        # Input options
        input_opts = [
            "-hide_banner",
            "-loglevel", "error",
            "-re",  # Read input at native frame rate
            "-stream_loop", "-1" if self.loop else "0",  # Loop infinitely or once
            "-i", self.video_path
        ]
        
        # Output options
        output_opts = [
            "-c:v", self.codec,
            "-preset", self.preset,
            "-b:v", self.bitrate,
            "-pix_fmt", self.pixel_format,
            "-r", str(self.fps),
            "-f", "rtsp",
            "-g", str(self.fps * 2),  
            "-keyint_min", str(self.fps),
            "-sc_threshold", "0",
            "-rtsp_transport", "tcp",
        ]
        
        command = ["ffmpeg"] + input_opts + output_opts + [self.rtsp_url]
        
        return command
    
    def start(self):
        """Start publishing the stream"""
        if self.running:
            logger.warning(f"[{self.stream_name}] Stream already running")
            return
        
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._publish_loop, daemon=True)
        self.thread.start()
        
        logger.info(f"[{self.stream_name}] Started publishing to {self.rtsp_url}")
    
    def _publish_loop(self):
        """Main publishing loop"""
        while self.running:
            try:
                command = self._build_ffmpeg_command()
                
                logger.debug(f"[{self.stream_name}] FFmpeg command: {' '.join(command)}")
                
                # Start FFmpeg process
                self.process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # Monitor the process
                while self.running and self.process.poll() is None:
                    time.sleep(0.1)
                
                # Check if process ended unexpectedly
                if self.running:
                    stderr_output = self.process.stderr.read() if self.process.stderr else ""
                    logger.error(
                        f"[{self.stream_name}] FFmpeg process ended unexpectedly. "
                        f"Error: {stderr_output[:500]}"
                    )
                    self.error_count += 1
                    
                    # Wait before restarting
                    time.sleep(2)
                
            except Exception as e:
                logger.error(f"[{self.stream_name}] Error in publish loop: {e}")
                self.error_count += 1
                time.sleep(2)
    
    def stop(self):
        """Stop publishing the stream"""
        logger.info(f"[{self.stream_name}] Stopping stream...")
        self.running = False
        
        # Terminate FFmpeg process
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"[{self.stream_name}] Force killing FFmpeg process")
                self.process.kill()
            except Exception as e:
                logger.error(f"[{self.stream_name}] Error stopping process: {e}")
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        logger.info(f"[{self.stream_name}] Stream stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get stream statistics"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        return {
            "stream_name": self.stream_name,
            "rtsp_url": self.rtsp_url,
            "running": self.running,
            "uptime_seconds": uptime,
            "error_count": self.error_count,
            "video_path": self.video_path,
            "resolution": f"{self.video_width}x{self.video_height}",
            "fps": self.fps,
            "is_alive": self.thread.is_alive() if self.thread else False
        }
    
    def is_healthy(self) -> bool:
        """Check if stream is healthy"""
        return (
            self.running and
            self.thread is not None and
            self.thread.is_alive() and
            self.error_count < 10
        )
