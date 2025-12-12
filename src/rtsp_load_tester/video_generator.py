"""
Video Generator Utility
Creates dummy video files for testing
"""

import cv2
import numpy as np
import os
from pathlib import Path
from loguru import logger


class DummyVideoGenerator:
    """Generate dummy test videos with various patterns"""
    
    def __init__(self, output_dir: str = "videos"):
        """
        Initialize video generator
        
        Args:
            output_dir: Directory to save generated videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_color_bars_video(
        self,
        filename: str,
        duration: int = 30,
        fps: int = 30,
        width: int = 1920,
        height: int = 1080
    ):
        """
        Generate a video with color bars and frame counter
        
        Args:
            filename: Output filename
            duration: Video duration in seconds
            fps: Frames per second
            width: Video width
            height: Video height
        """
        output_path = self.output_dir / filename
        
        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        total_frames = duration * fps
        
        logger.info(f"Generating color bars video: {filename}")
        logger.info(f"  Duration: {duration}s, FPS: {fps}, Resolution: {width}x{height}")
        
        # Color bars (RGB)
        colors = [
            (255, 255, 255),  # White
            (255, 255, 0),    # Yellow
            (0, 255, 255),    # Cyan
            (0, 255, 0),      # Green
            (255, 0, 255),    # Magenta
            (255, 0, 0),      # Red
            (0, 0, 255),      # Blue
            (0, 0, 0),        # Black
        ]
        
        bar_width = width // len(colors)
        
        for frame_num in range(total_frames):
            # Create frame with color bars
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Draw color bars
            for i, color in enumerate(colors):
                x_start = i * bar_width
                x_end = (i + 1) * bar_width if i < len(colors) - 1 else width
                frame[:, x_start:x_end] = color
            
            # Add frame counter
            text = f"Frame: {frame_num + 1}/{total_frames}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2
            thickness = 3
            
            # Get text size
            (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
            
            # Position text in center
            x = (width - text_width) // 2
            y = (height + text_height) // 2
            
            # Draw text with black outline
            cv2.putText(frame, text, (x, y), font, font_scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
            cv2.putText(frame, text, (x, y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
            
            # Write frame
            out.write(frame)
            
            if (frame_num + 1) % fps == 0:
                logger.debug(f"  Generated {frame_num + 1}/{total_frames} frames")
        
        out.release()
        logger.info(f"Video saved: {output_path}")
        
        return str(output_path)
    
    def generate_animated_pattern_video(
        self,
        filename: str,
        duration: int = 30,
        fps: int = 30,
        width: int = 1280,
        height: int = 720
    ):
        """
        Generate a video with animated geometric patterns
        
        Args:
            filename: Output filename
            duration: Video duration in seconds
            fps: Frames per second
            width: Video width
            height: Video height
        """
        output_path = self.output_dir / filename
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        total_frames = duration * fps
        
        logger.info(f"Generating animated pattern video: {filename}")
        logger.info(f"  Duration: {duration}s, FPS: {fps}, Resolution: {width}x{height}")
        
        for frame_num in range(total_frames):
            # Create black background
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Animate circles
            angle = (frame_num / fps) * 2 * np.pi
            
            # Draw moving circles
            for i in range(5):
                phase = i * (2 * np.pi / 5)
                x = int(width / 2 + np.cos(angle + phase) * min(width, height) / 4)
                y = int(height / 2 + np.sin(angle + phase) * min(width, height) / 4)
                
                color = (
                    int(127 + 127 * np.sin(angle + phase)),
                    int(127 + 127 * np.cos(angle + phase + np.pi / 3)),
                    int(127 + 127 * np.sin(angle + phase + 2 * np.pi / 3))
                )
                
                cv2.circle(frame, (x, y), 50, color, -1)
            
            # Add timestamp
            timestamp = f"Time: {frame_num / fps:.2f}s"
            cv2.putText(frame, timestamp, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, (255, 255, 255), 2, cv2.LINE_AA)
            
            out.write(frame)
            
            if (frame_num + 1) % fps == 0:
                logger.debug(f"  Generated {frame_num + 1}/{total_frames} frames")
        
        out.release()
        logger.info(f"Video saved: {output_path}")
        
        return str(output_path)
    
    def generate_gradient_video(
        self,
        filename: str,
        duration: int = 30,
        fps: int = 25,
        width: int = 1920,
        height: int = 1080
    ):
        """
        Generate a video with animated color gradients
        
        Args:
            filename: Output filename
            duration: Video duration in seconds
            fps: Frames per second
            width: Video width
            height: Video height
        """
        output_path = self.output_dir / filename
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        total_frames = duration * fps
        
        logger.info(f"Generating gradient video: {filename}")
        logger.info(f"  Duration: {duration}s, FPS: {fps}, Resolution: {width}x{height}")
        
        for frame_num in range(total_frames):
            # Create gradient
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Animate color shift
            offset = (frame_num / total_frames) * 255
            
            for y in range(height):
                for x in range(width):
                    r = int((x / width) * 255)
                    g = int((y / height) * 255)
                    b = int(((x + y) / (width + height)) * 255 + offset) % 255
                    
                    frame[y, x] = (b, g, r)
            
            # Add info text
            info_text = f"Frame {frame_num + 1}/{total_frames}"
            cv2.putText(frame, info_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                       1, (255, 255, 255), 2, cv2.LINE_AA)
            
            out.write(frame)
            
            if (frame_num + 1) % fps == 0:
                logger.debug(f"  Generated {frame_num + 1}/{total_frames} frames")
        
        out.release()
        logger.info(f"Video saved: {output_path}")
        
        return str(output_path)
    
    def generate_all_test_videos(self):
        """Generate a complete set of test videos"""
        logger.info("Generating all test videos...")
        
        videos = []
        
        # Video 1: Color bars (HD)
        videos.append(
            self.generate_color_bars_video(
                "dummy_video1.mp4",
                duration=30,
                fps=30,
                width=1920,
                height=1080
            )
        )
        
        # Video 2: Animated pattern (HD 720p)
        videos.append(
            self.generate_animated_pattern_video(
                "dummy_video2.mp4",
                duration=30,
                fps=25,
                width=1280,
                height=720
            )
        )
        
        # Video 3: Gradient (Full HD)
        videos.append(
            self.generate_gradient_video(
                "dummy_video3.mp4",
                duration=30,
                fps=30,
                width=1920,
                height=1080
            )
        )
        
        logger.info(f"Generated {len(videos)} test videos")
        return videos


if __name__ == "__main__":
    generator = DummyVideoGenerator()
    generator.generate_all_test_videos()
