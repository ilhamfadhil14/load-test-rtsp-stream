# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based RTSP stream publisher for load testing AI video processing pipelines. It publishes multiple looping video streams simultaneously to test parallel processing capabilities using FFmpeg and MediaMTX RTSP server.

## Commands

### Setup and Installation
```bash
# Install dependencies (automatically creates .venv and installs packages)
uv sync

# Validate setup (checks FFmpeg availability)
uv run python main.py --validate

# Place your video file in videos/ directory
# Example: videos/sample.mp4

# Optional: Generate test videos (for backward compatibility)
uv run python video_generator.py
# or
uv run python main.py --generate-videos
```

### Running the Load Test
```bash
# Run with default config.yaml
uv run python main.py

# Run with custom configuration
uv run python main.py -c custom_config.yaml
```

### Testing Individual Components
```bash
# Test stream publisher directly (for debugging)
uv run python -c "from stream_publisher import RTSPStreamPublisher; p = RTSPStreamPublisher('test', 'videos/dummy_video1.mp4', 'rtsp://localhost:8554/test'); p.start()"

# Test video generator
uv run python video_generator.py
```

### Docker Commands
```bash
# Build and run with official MediaMTX image
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f rtsp-load-tester
docker-compose logs -f mediamtx

# Stop containers
docker-compose down
```

## Architecture

### Component Hierarchy
```
main.py (entry point)
  └─> LoadTestOrchestrator (orchestrator.py)
       └─> RTSPStreamPublisher instances (stream_publisher.py)
            └─> FFmpeg subprocess
```

### Key Components

**1. main.py** - Entry point and CLI
- Validates FFmpeg installation
- Loads YAML configuration
- Generates test videos if missing
- Creates and starts LoadTestOrchestrator
- Provides interactive prompts for MediaMTX readiness

**2. orchestrator.py - LoadTestOrchestrator class**
- Manages multiple RTSPStreamPublisher instances
- Implements monitoring loop with configurable report intervals
- Tracks system resources (CPU, memory via psutil)
- Enforces resource limits (max_memory_percent, max_cpu_percent)
- Handles graceful shutdown via SIGINT/SIGTERM signals
- Generates JSON metrics reports in logs/metrics.json

**3. stream_publisher.py - RTSPStreamPublisher class**
- Wraps FFmpeg subprocess for RTSP streaming
- Runs FFmpeg in background thread with auto-restart on failure
- Uses `-stream_loop -1` for infinite looping
- Tracks stream health (error count, uptime, thread alive status)
- Extracts video properties using OpenCV (resolution, fps, duration)
- Builds FFmpeg command with codec, preset, bitrate, pixel_format settings

**4. video_generator.py - DummyVideoGenerator class**
- Generates test videos using FFmpeg's video filters
- Creates color bars, animated patterns, and gradients
- Default videos: dummy_video1.mp4 (1920x1080@30fps), dummy_video2.mp4 (1280x720@25fps), dummy_video3.mp4 (1920x1080@30fps)

### Critical Dependencies
- **uv**: Fast Python package manager - used for dependency management (replaces pip/venv)
- **FFmpeg**: MUST be installed and in PATH - used for encoding and streaming
- **MediaMTX**: External RTSP server (not included) - must be running before load test starts
- **OpenCV (cv2)**: For video property extraction and example consumer code
- **psutil**: For system resource monitoring
- **loguru**: For structured logging to both stderr and rotating log files

### Configuration Flow
1. YAML config loaded by main.py via `load_config()`
2. Config validated by LoadTestOrchestrator._validate_config()
   - Checks for video_sources and rtsp_server sections
   - Enforces max_streams limit
3. Publishers created from video_sources list
   - Each source becomes one RTSPStreamPublisher
   - RTSP URL format: `{base_url}/{stream_name}`

### Monitoring and Health Checks
- **Stream health criteria** (stream_publisher.py:200-207):
  - running flag is True
  - thread is alive
  - error_count < 10
- **Resource limits** (orchestrator.py:214-234):
  - Memory: Stops test if exceeds max_memory_percent (default 80%)
  - CPU: Logs warning if exceeds max_cpu_percent (default 90%)
- **Status reports** printed every report_interval seconds (default 10s)
- **Auto-restart**: Publishers automatically restart FFmpeg on failure until error_count >= 10

### Signal Handling
- SIGINT and SIGTERM trigger graceful shutdown
- Shutdown sequence: stop all publishers → generate final report → exit
- Each publisher terminates FFmpeg process (5s timeout, then kill)

## Configuration Structure

The config.yaml has these main sections:
- `rtsp_server`: MediaMTX connection details (host, port, base_url)
- `video`: Single video file configuration (path, loop, fps) - **NEW FORMAT**
  - The system will create multiple streams from this single video based on `concurrent_streams` setting
  - Example: If `concurrent_streams: 3`, it will create stream1, stream2, stream3 all using the same video
- `video_sources`: [LEGACY] List of video files to stream (name, video_path, loop, fps) - still supported for backward compatibility
- `publisher`: FFmpeg encoder settings (codec, preset, bitrate, format, pixel_format)
- `load_test`: Test parameters (concurrent_streams, duration, report_interval)
- `monitoring`: Logging configuration (enabled, log_level, metrics_file)
- `limits`: Resource constraints (max_streams, max_memory_percent, max_cpu_percent)

### New Configuration Format (Recommended)
```yaml
video:
  path: "videos/sample.mp4"  # Single video file for all streams
  loop: true
  fps: 30

load_test:
  concurrent_streams: 3  # Creates stream1, stream2, stream3 from same video
```

## Docker Architecture

The project includes a multi-container Docker setup:

### Containers
1. **mediamtx**: Official `bluenviron/mediamtx:latest-ffmpeg` image
   - Runs the RTSP server
   - Exposes ports: 8554 (RTSP), 8888 (WebRTC), 8889 (HLS)

2. **rtsp-load-tester**: Custom Python application
   - Built with `uv` for dependency management
   - Uses `config.docker.yaml` which points to `mediamtx` container hostname
   - Waits 5 seconds for MediaMTX to be ready before starting
   - Runs with `--skip-prompt` flag to bypass interactive MediaMTX check
   - **Requires video files to be mounted from host** - no video generation in container

### Configuration Files
- `config.yaml`: For local development (uses `localhost`)
- `config.docker.yaml`: For Docker containers (uses `mediamtx` hostname)

### Key Implementation Details
- The Dockerfile uses official `uv` base image: `ghcr.io/astral-sh/uv:python3.10-bookworm-slim`
- Dependencies are installed with `uv sync --frozen`
- **No video generation** - videos must be provided in `./videos/` directory on host
- Videos are mounted from `./videos` on host to `/app/videos` in container
- The `--skip-prompt` flag was added to main.py to support non-interactive Docker execution

### Docker Usage
```bash
# 1. Place your video file in videos/ directory
mkdir -p videos
cp /path/to/your/video.mp4 videos/sample.mp4

# 2. Update config.docker.yaml if needed (or use default)

# 3. Build and run
docker-compose up --build
```

## Important Notes

### External Dependencies
**Local Development**: MediaMTX RTSP server must be running before starting the load test. Download from https://github.com/bluenviron/mediamtx/releases.

**Docker**: Uses official `bluenviron/mediamtx:latest-ffmpeg` image automatically via docker-compose.

### FFmpeg Command Structure
The FFmpeg command built by stream_publisher.py follows this pattern:
```
ffmpeg -re -stream_loop -1 -i {video_path} -c:v {codec} -preset {preset} -b:v {bitrate} -pix_fmt {pixel_format} -r {fps} -f rtsp -rtsp_transport tcp {rtsp_url}
```

### Threading Model
- Each RTSPStreamPublisher runs FFmpeg in a daemon thread
- Main thread runs monitoring loop in orchestrator
- All threads stop when orchestrator.running = False

### Error Recovery
Publishers automatically restart FFmpeg subprocess on failure, incrementing error_count. After 10 errors, the stream is considered unhealthy and stopped.

### Logging
Uses loguru with dual output: stderr (colored, formatted) and rotating log files in logs/ directory (100MB rotation, 7 day retention).
