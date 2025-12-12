# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies (2 minutes)

```bash
# Install uv (if not already installed)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install FFmpeg
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Install Python packages with uv
uv sync
```

### Step 2: Download MediaMTX (1 minute)

```bash
# Linux (amd64)
wget https://github.com/bluenviron/mediamtx/releases/download/v1.5.0/mediamtx_v1.5.0_linux_amd64.tar.gz
tar -xzf mediamtx_v1.5.0_linux_amd64.tar.gz

# macOS (Intel)
wget https://github.com/bluenviron/mediamtx/releases/download/v1.5.0/mediamtx_v1.5.0_darwin_amd64.tar.gz
tar -xzf mediamtx_v1.5.0_darwin_amd64.tar.gz

# macOS (Apple Silicon)
wget https://github.com/bluenviron/mediamtx/releases/download/v1.5.0/mediamtx_v1.5.0_darwin_arm64.tar.gz
tar -xzf mediamtx_v1.5.0_darwin_arm64.tar.gz
```

Or use automated setup:
```bash
uv run python setup.py
```

### Step 3: Generate Test Videos (1 minute)

```bash
uv run python video_generator.py
```

### Step 4: Start MediaMTX (10 seconds)

In a **separate terminal**:
```bash
./mediamtx
```

### Step 5: Run Load Test (1 minute)

```bash
uv run python main.py
```

## Using Docker (Even Faster!)

The Docker setup uses the official MediaMTX image (`bluenviron/mediamtx:latest-ffmpeg`) alongside the load tester.

```bash
# Build and run both containers
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# Stop containers
docker-compose down
```

The setup includes:
- **mediamtx**: Official MediaMTX RTSP server with FFmpeg support
- **rtsp-load-tester**: Python load testing application with uv

Note: The load tester automatically waits for MediaMTX to be ready before starting.

## Stream URLs

After starting, your streams will be available at:
- `rtsp://localhost:8554/stream1`
- `rtsp://localhost:8554/stream2`
- `rtsp://localhost:8554/stream3`

## Test Your Streams

```bash
# Using VLC
vlc rtsp://localhost:8554/stream1

# Using FFplay
ffplay rtsp://localhost:8554/stream1

# Using Python (consumer example)
uv run python consumer_example.py rtsp://localhost:8554/stream1

# Multiple streams
uv run python consumer_example.py rtsp://localhost:8554/stream1 rtsp://localhost:8554/stream2
```

## Quick Configuration Changes

Edit `config.yaml`:

```yaml
# Change number of streams
load_test:
  concurrent_streams: 5  # Increase to 5 streams

# Change duration
load_test:
  duration: 1800  # Run for 30 minutes

# Add custom video
video_sources:
  - name: "my_stream"
    video_path: "videos/my_video.mp4"
    loop: true
    fps: 30
```

## Common Issues

**Problem**: "Connection refused"
- **Solution**: Make sure MediaMTX is running first

**Problem**: "FFmpeg not found"
- **Solution**: Install FFmpeg and ensure it's in PATH

**Problem**: Videos not found
- **Solution**: Run `uv run python video_generator.py`

## Performance Tips

- Start with 3 streams, scale up gradually
- Use `preset: "ultrafast"` for lower CPU usage
- Monitor system resources in the status reports
- Use lower resolution videos if needed

## Next Steps

1. Connect your AI pipeline to the streams
2. Run performance benchmarks
3. Adjust configuration based on your needs
4. Check the full README.md for advanced features

---

That's it! You're ready to load test your AI pipeline. 🚀
