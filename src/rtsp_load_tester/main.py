"""
RTSP Load Tester - Main Entry Point
"""

import argparse
import yaml
import sys
from pathlib import Path
from loguru import logger

from .orchestrator import LoadTestOrchestrator

# Optional import for video generation (not needed in Docker)
try:
    from .video_generator import DummyVideoGenerator
    HAS_VIDEO_GENERATOR = True
except ImportError:
    HAS_VIDEO_GENERATOR = False


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        sys.exit(1)


def validate_setup():
    """Validate that required dependencies are available"""
    import subprocess
    
    # Check FFmpeg
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        logger.info(f"✓ FFmpeg is installed: {result.stdout.decode().splitlines()[0]}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("✗ FFmpeg is not installed or not in PATH")
        logger.error("Please install FFmpeg: https://ffmpeg.org/download.html")
        return False
    
    return True


def check_video_exists(config: dict):
    """Check if video file exists"""
    # Support new config format (single video)
    if config.get("video"):
        video_path = Path(config["video"]["path"])
        if not video_path.exists():
            logger.error(f"✗ Video file not found: {video_path}")
            logger.error(f"Please place your video file at: {video_path}")
            sys.exit(1)
        logger.info(f"✓ Video file exists: {video_path}")
        return

    # Support old config format (video_sources)
    if config.get("video_sources"):
        video_sources = config.get("video_sources", [])
        missing_videos = []

        for source in video_sources:
            video_path = Path(source["video_path"])
            if not video_path.exists():
                missing_videos.append(video_path)

        if missing_videos:
            logger.error(f"✗ Found {len(missing_videos)} missing video files")
            for video in missing_videos:
                logger.error(f"  - {video}")
            logger.error("Please provide video files in the videos/ directory")
            sys.exit(1)
        logger.info("✓ All video files exist")


def print_stream_info(orchestrator: LoadTestOrchestrator):
    """Print information about available streams"""
    urls = orchestrator.get_stream_urls()
    
    print("\n" + "=" * 60)
    print("RTSP STREAM URLS")
    print("=" * 60)
    print("\nYour AI pipeline can connect to these streams:\n")
    
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")
    
    print("\nExample VLC command to view a stream:")
    if urls:
        print(f"  vlc {urls[0]}")
    
    print("\nExample Python code to consume streams:")
    print("""
  import cv2
  
  cap = cv2.VideoCapture('rtsp://localhost:8554/stream1')
  while True:
      ret, frame = cap.read()
      if not ret:
          break
      # Process frame with your AI pipeline
      cv2.imshow('Frame', frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break
  cap.release()
    """)
    print("=" * 60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="RTSP Load Tester - Publish multiple video streams for AI pipeline testing"
    )
    parser.add_argument(
        "-c", "--config",
        default="config/config.yaml",
        help="Path to configuration file (default: config/config.yaml)"
    )
    parser.add_argument(
        "--generate-videos",
        action="store_true",
        help="Generate test videos and exit"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate setup and exit"
    )
    parser.add_argument(
        "--skip-prompt",
        action="store_true",
        help="Skip MediaMTX running confirmation prompt (for Docker/automation)"
    )

    args = parser.parse_args()
    
    # ASCII banner
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║         RTSP Load Tester for AI Pipelines            ║
    ║              Multiple Stream Publisher                ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    # Validate setup
    if not validate_setup():
        sys.exit(1)
    
    if args.validate:
        logger.info("Setup validation complete")
        sys.exit(0)
    
    # Load configuration
    logger.info(f"Loading configuration from: {args.config}")
    config = load_config(args.config)
    
    # Generate videos if requested (for backward compatibility)
    if args.generate_videos:
        if not HAS_VIDEO_GENERATOR:
            logger.error("video_generator module not available")
            logger.error("Please use this feature outside of Docker")
            sys.exit(1)
        try:
            generator = DummyVideoGenerator()
            generator.generate_all_test_videos()
            logger.info("Test videos generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate videos: {e}")
        sys.exit(0)

    # Check if video file exists
    check_video_exists(config)

    # Check MediaMTX warning (skip if --skip-prompt is used)
    if not args.skip_prompt:
        print("\n⚠️  IMPORTANT: Make sure MediaMTX is running!")
        print("Download from: https://github.com/bluenviron/mediamtx")
        print("Run with: ./mediamtx (or mediamtx.exe on Windows)\n")

        response = input("Is MediaMTX running? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            logger.warning("Please start MediaMTX before running the load test")
            sys.exit(0)
    else:
        logger.info("Skipping MediaMTX confirmation prompt (--skip-prompt flag set)")
    
    # Create orchestrator
    orchestrator = LoadTestOrchestrator(config)
    
    # Print stream information
    print_stream_info(orchestrator)
    
    # Start load test
    try:
        orchestrator.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error running load test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        orchestrator.stop()


if __name__ == "__main__":
    main()
