# RTSP Load Tester for AI Pipelines

A Python-based RTSP stream publisher for load testing AI video processing pipelines. Publishes multiple looping video streams simultaneously to test parallel processing capabilities.

## Features

- ✅ **Multiple Concurrent Streams**: Publish multiple RTSP streams in parallel
- ✅ **Video Looping**: Seamlessly loop videos for continuous testing
- ✅ **Dummy Video Generation**: Built-in test video generator
- ✅ **Resource Monitoring**: Track CPU, memory, and stream health
- ✅ **Configurable**: YAML-based configuration
- ✅ **Graceful Shutdown**: Handles signals for clean shutdown
- ✅ **Detailed Logging**: Comprehensive logging and metrics
- ✅ **Production Ready**: Error handling and recovery mechanisms

## Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Installation Guide](docs/INSTALLATION_GUIDE.md)** - Complete setup instructions
- **[Docker Setup](docs/DOCKER_SETUP.md)** - Run with Docker
- **[Testing Streams](docs/TEST_STREAM_GUIDE.md)** - How to test and consume streams
- **[Developer Guide](docs/CLAUDE.md)** - Architecture and development details
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - High-level overview

## Architecture

```
┌─────────────────────────────────────────────────┐
│           Load Test Orchestrator                │
│  (Manages multiple stream publishers)           │
└──────────┬──────────────────────────────────────┘
           │
           ├──► Stream Publisher 1 (video1.mp4)
           │    └──► rtsp://localhost:8554/stream1
           │
           ├──► Stream Publisher 2 (video2.mp4)
           │    └──► rtsp://localhost:8554/stream2
           │
           └──► Stream Publisher N (videoN.mp4)
                └──► rtsp://localhost:8554/streamN
                
                          │
                          ▼
           ┌──────────────────────────────┐
           │      MediaMTX Server         │
           │      (RTSP Server)           │
           └──────────────────────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │    AI Pipeline Consumers     │
           │    (Your Applications)       │
           └──────────────────────────────┘
```

## Prerequisites

### Required Software

1. **Python 3.8+**
   ```bash
   python --version
   ```

2. **uv** (Fast Python package manager)
   ```bash
   # Install uv (macOS/Linux)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install uv (Windows)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # Or install via pip
   pip install uv
   ```

3. **FFmpeg** (Critical dependency)
   - **Ubuntu/Debian:**
     ```bash
     sudo apt-get update
     sudo apt-get install ffmpeg
     ```
   - **macOS:**
     ```bash
     brew install ffmpeg
     ```
   - **Windows:**
     Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

4. **MediaMTX** (RTSP Server)
   - Download the latest release: [MediaMTX Releases](https://github.com/bluenviron/mediamtx/releases)
   - Extract and place in a convenient location
   - No installation needed, just run the binary

## Installation

### 1. Clone or Download the Project

```bash
cd rtsp_load_tester
```

### 2. Install Dependencies with uv

```bash
# This will automatically create a virtual environment and install all dependencies
uv sync
```

### 3. Validate Setup

```bash
uv run python -m rtsp_load_tester.main --validate
```

## Quick Start

### 1. Start MediaMTX Server

In a **separate terminal**:

```bash
# Linux/macOS
./mediamtx

# Windows
mediamtx.exe
```

You should see output like:
```
INF MediaMTX v1.x.x
INF [RTSP] listener opened on :8554
```

### 2. Generate Test Videos (First Time Only)

```bash
uv run python -m rtsp_load_tester.video_generator
```

This creates three test videos in the `videos/` directory:
- `dummy_video1.mp4` - Color bars with frame counter (1920x1080, 30fps)
- `dummy_video2.mp4` - Animated patterns (1280x720, 25fps)
- `dummy_video3.mp4` - Color gradients (1920x1080, 30fps)

### 3. Run the Load Test

```bash
uv run python -m rtsp_load_tester.main
```

The application will:
1. Validate FFmpeg installation
2. Check for video files (generate if missing)
3. Start publishing streams
4. Print stream URLs for your AI pipeline
5. Monitor streams and system resources
6. Generate reports

### 4. Connect Your AI Pipeline

Use the printed RTSP URLs to connect your AI processing pipeline:

```python
import cv2

# Connect to stream
cap = cv2.VideoCapture('rtsp://localhost:8554/stream1')

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Your AI processing here
    # Example: object detection, classification, etc.
    
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## Configuration

Edit `config.yaml` to customize your load test:

### Basic Configuration

```yaml
# RTSP Server Settings
rtsp_server:
  host: "localhost"
  port: 8554
  base_url: "rtsp://localhost:8554"

# Video Sources
video_sources:
  - name: "stream1"
    video_path: "videos/dummy_video1.mp4"
    loop: true
    fps: 30
  
  - name: "stream2"
    video_path: "videos/dummy_video2.mp4"
    loop: true
    fps: 25

# Load Test Settings
load_test:
  concurrent_streams: 3
  duration: 3600  # 0 = infinite
  report_interval: 10  # seconds
```

### Publisher Settings

```yaml
publisher:
  codec: "libx264"
  preset: "ultrafast"  # ultrafast, fast, medium, slow
  bitrate: "2M"
  format: "rtsp"
  pixel_format: "yuv420p"
```

### Resource Limits

```yaml
limits:
  max_streams: 50
  max_memory_percent: 80
  max_cpu_percent: 90
```

## Usage Examples

### Test with Custom Videos

1. Place your videos in the `videos/` directory
2. Update `config.yaml`:

```yaml
video_sources:
  - name: "my_test_video"
    video_path: "videos/my_video.mp4"
    loop: true
    fps: 30
```

3. Run the load test

### High Load Testing

For stress testing with many streams:

```yaml
load_test:
  concurrent_streams: 20  # 20 parallel streams
  duration: 7200  # 2 hours
```

### Different Resolutions and Bitrates

```yaml
video_sources:
  - name: "hd_stream"
    video_path: "videos/hd_video.mp4"
    fps: 30
    
publisher:
  bitrate: "4M"  # Higher bitrate for HD
```

### Custom Test Duration

```bash
# Edit config.yaml
load_test:
  duration: 1800  # 30 minutes
```

## Monitoring and Logs

### Real-time Monitoring

The application prints status reports every 10 seconds (configurable):

```
============================================================
STATUS REPORT
============================================================
System CPU: 45.2%
System Memory: 32.1% (8.45GB / 16.00GB)
Streams: 3/3 healthy
  ✓ stream1: Uptime=120s, Errors=0, Resolution=1920x1080
  ✓ stream2: Uptime=120s, Errors=0, Resolution=1280x720
  ✓ stream3: Uptime=120s, Errors=0, Resolution=1920x1080
============================================================
```

### Log Files

Logs are saved to `logs/` directory:
- `rtsp_load_test_YYYY-MM-DD_HH-MM-SS.log` - Detailed logs
- `metrics.json` - Final test metrics

### Metrics Report

After stopping the test, a JSON report is generated:

```json
{
  "test_duration_seconds": 3600,
  "total_streams": 3,
  "streams": [
    {
      "stream_name": "stream1",
      "rtsp_url": "rtsp://localhost:8554/stream1",
      "uptime_seconds": 3598.2,
      "error_count": 0,
      "resolution": "1920x1080"
    }
  ]
}
```

## Testing Your AI Pipeline

### Example: Object Detection Pipeline

```python
import cv2
import numpy as np

def process_rtsp_stream(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    
    # Your AI model initialization
    # model = load_your_model()
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Stream ended or error")
            break
        
        # Run inference
        # detections = model.detect(frame)
        
        # Process results
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"Processed {frame_count} frames from {rtsp_url}")
        
        # Display (optional)
        cv2.imshow(f'Stream: {rtsp_url}', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Process multiple streams
from threading import Thread

streams = [
    'rtsp://localhost:8554/stream1',
    'rtsp://localhost:8554/stream2',
    'rtsp://localhost:8554/stream3'
]

threads = []
for stream_url in streams:
    t = Thread(target=process_rtsp_stream, args=(stream_url,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
```

### Example: Performance Benchmarking

```python
import cv2
import time

def benchmark_stream(rtsp_url, duration=60):
    cap = cv2.VideoCapture(rtsp_url)
    
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Your processing here
        frame_count += 1
    
    elapsed = time.time() - start_time
    fps = frame_count / elapsed
    
    print(f"Stream: {rtsp_url}")
    print(f"  Frames: {frame_count}")
    print(f"  FPS: {fps:.2f}")
    print(f"  Duration: {elapsed:.2f}s")
    
    cap.release()

benchmark_stream('rtsp://localhost:8554/stream1', duration=60)
```

## Troubleshooting

### Issue: "FFmpeg not found"

**Solution:**
```bash
# Install FFmpeg
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Verify installation
ffmpeg -version
```

### Issue: "Connection refused" or streams not accessible

**Solution:**
1. Make sure MediaMTX is running:
   ```bash
   ./mediamtx
   ```
2. Check if port 8554 is available:
   ```bash
   # Linux/macOS
   lsof -i :8554
   
   # Windows
   netstat -ano | findstr :8554
   ```

### Issue: High CPU/Memory usage

**Solution:**
1. Reduce concurrent streams in `config.yaml`
2. Use lower resolution videos
3. Adjust encoder preset to "ultrafast"
4. Lower bitrate setting

### Issue: Streams lagging or dropping frames

**Solution:**
1. Check system resources (CPU/Memory)
2. Reduce encoding bitrate
3. Use hardware acceleration if available:
   ```yaml
   publisher:
     codec: "h264_nvenc"  # NVIDIA GPU
     # or
     codec: "h264_qsv"    # Intel QuickSync
   ```

### Issue: Video files not found

**Solution:**
```bash
# Generate test videos
uv run python -m rtsp_load_tester.video_generator

# Or specify correct paths in config/config.yaml
```

## Advanced Configuration

### Custom MediaMTX Configuration

Create `mediamtx.yml`:

```yaml
paths:
  all:
    readUser: optional_username
    readPass: optional_password
```

### Network Configuration

For remote access, update `config.yaml`:

```yaml
rtsp_server:
  host: "0.0.0.0"  # Listen on all interfaces
  port: 8554
  base_url: "rtsp://YOUR_SERVER_IP:8554"
```

### Multiple Instances

Run multiple instances on different ports:

```yaml
# Instance 1 - config1.yaml
rtsp_server:
  port: 8554

# Instance 2 - config2.yaml
rtsp_server:
  port: 8555
```

```bash
uv run python -m rtsp_load_tester.main -c config/config1.yaml
uv run python -m rtsp_load_tester.main -c config/config2.yaml
```

## Project Structure

```
rtsp-load-tester/
├── README.md                    # This file
├── pyproject.toml              # Project configuration & dependencies
├── uv.lock                     # Dependency lock file
├── docker-compose.yml          # Docker compose configuration
├── Dockerfile                  # Docker image definition
│
├── src/rtsp_load_tester/       # Source code
│   ├── __init__.py
│   ├── main.py                 # Main entry point
│   ├── orchestrator.py         # Load test orchestrator
│   ├── stream_publisher.py     # Individual stream publisher
│   └── video_generator.py      # Dummy video generator
│
├── config/                     # Configuration files
│   ├── config.yaml             # Default configuration
│   └── config.docker.yaml      # Docker configuration
│
├── examples/                   # Example scripts
│   ├── consumer_example.py     # Stream consumer example
│   └── test_stream_consumer.py # Stream testing utility
│
├── scripts/                    # Setup and utility scripts
│   ├── setup.py               # Automated setup
│   └── setup.sh               # Shell setup script
│
├── docs/                       # Documentation
│   ├── QUICKSTART.md
│   ├── INSTALLATION_GUIDE.md
│   ├── DOCKER_SETUP.md
│   ├── TEST_STREAM_GUIDE.md
│   ├── CLAUDE.md
│   └── PROJECT_SUMMARY.md
│
├── videos/                     # Video files directory
│   ├── README.md              # Video setup guide
│   └── sample.mp4             # Your video file
│
└── logs/                       # Log files directory
    ├── rtsp_load_test_*.log
    └── metrics.json
```

## Performance Tips

1. **Use SSD storage** for video files
2. **Adjust encoder preset** based on CPU capability
3. **Monitor system resources** during testing
4. **Use appropriate bitrates** for your network
5. **Test incrementally** - start with few streams, scale up

## License

This project is provided as-is for testing and development purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review MediaMTX documentation
3. Check FFmpeg documentation

## Contributing

Feel free to extend this tool with:
- Additional video generators
- Custom stream patterns
- Advanced monitoring features
- Integration with monitoring tools

---

**Happy Testing! 🚀**
