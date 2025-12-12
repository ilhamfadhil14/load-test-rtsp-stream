# Stream Consumer Test Guide

## Overview

`test_stream_consumer.py` is a simple Python script to test consuming RTSP streams from the load tester using OpenCV.

## Prerequisites

Make sure you have the streams running:

```bash
# Start the Docker containers
docker-compose up -d

# Or run locally
uv run python main.py
```

## Installation

The script uses OpenCV which is already in the project dependencies:

```bash
uv sync  # If not already done
```

## Basic Usage

### Test Single Stream

```bash
# Test stream1 (default)
uv run python test_stream_consumer.py

# Test specific stream
uv run python test_stream_consumer.py rtsp://localhost:8554/stream2

# Test with custom RTSP URL
uv run python test_stream_consumer.py rtsp://192.168.1.100:8554/stream1
```

### Test Multiple Streams Simultaneously

```bash
# Test 2 streams
uv run python test_stream_consumer.py \
    rtsp://localhost:8554/stream1 \
    rtsp://localhost:8554/stream2

# Test all 3 default streams
uv run python test_stream_consumer.py --all
```

### Test with Duration Limit

```bash
# Run for 60 seconds then stop
uv run python test_stream_consumer.py rtsp://localhost:8554/stream1 --duration 60

# Test all streams for 30 seconds
uv run python test_stream_consumer.py --all --duration 30
```

### Disable FPS Display

```bash
# Test without FPS overlay
uv run python test_stream_consumer.py rtsp://localhost:8554/stream1 --no-fps
```

### Custom Host/Port

```bash
# Test stream from different host
uv run python test_stream_consumer.py --host 192.168.1.100 --port 8554 --all
```

## Features

### Real-time Display
- Opens video window showing the stream
- Displays FPS counter (can be disabled with `--no-fps`)
- Shows frame counter

### Keyboard Controls
- **q**: Quit the test
- **s**: Take screenshot (saved as `screenshot_YYYYMMDD_HHMMSS.jpg`)

### Statistics
After the test completes, you'll see:
- Total frames received
- Test duration
- Average FPS

Example output:
```
============================================================
STATISTICS
============================================================
Total frames: 1247
Duration: 30.05s
Average FPS: 41.50
============================================================
```

## Usage Examples

### Example 1: Quick Stream Test

Test stream1 for 10 seconds:

```bash
uv run python test_stream_consumer.py rtsp://localhost:8554/stream1 --duration 10
```

Expected output:
```
🎥 RTSP Stream Consumer Test
Testing 1 stream(s)

============================================================
Testing Stream: rtsp://localhost:8554/stream1
============================================================

✓ Stream opened successfully
  Resolution: 1920x1080
  FPS: 30.0

Press 'q' to quit, 's' to take screenshot
```

### Example 2: Load Test Multiple Streams

Test all 3 streams for 60 seconds:

```bash
uv run python test_stream_consumer.py --all --duration 60
```

This will open 3 video windows simultaneously, showing all streams.

### Example 3: Performance Benchmark

Test how many frames you can receive:

```bash
uv run python test_stream_consumer.py rtsp://localhost:8554/stream1 --duration 60 --no-fps
```

The statistics at the end will show your actual FPS, which you can compare against the stream's nominal FPS (30fps by default).

### Example 4: Take Screenshots

```bash
# Start the stream test
uv run python test_stream_consumer.py rtsp://localhost:8554/stream1

# While running, press 's' to capture screenshots
# Press 'q' to quit
```

Screenshots are saved as `screenshot_20251119_120530.jpg` in the current directory.

## Troubleshooting

### "Could not open stream" Error

**Cause**: Streams are not running or RTSP server is not accessible

**Solution**:
```bash
# Check if containers are running
docker-compose ps

# Start containers if needed
docker-compose up -d

# Check logs
docker-compose logs rtsp-load-tester
```

### "Connection refused" Error

**Cause**: MediaMTX is not running

**Solution**:
```bash
# Restart containers
docker-compose restart

# Or check MediaMTX logs
docker-compose logs mediamtx
```

### Low FPS / Frame Drops

**Cause**: System resources, network latency, or encoding settings

**Solutions**:
1. Reduce concurrent streams in config
2. Use faster encoding preset: `preset: "ultrafast"`
3. Lower bitrate: `bitrate: "1M"`
4. Close other applications

### Video Window Not Appearing

**Cause**: Display environment issues (especially in Docker/SSH)

**Solution**:
- Run on local machine with display
- Or use headless mode (modify script to save frames instead of displaying)

## Integration with Your AI Pipeline

Use this script as a template for your AI processing:

```python
import cv2
import time

def process_stream_for_ai(stream_url):
    """Process RTSP stream with AI model"""
    cap = cv2.VideoCapture(stream_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

    if not cap.isOpened():
        print(f"Error: Could not open {stream_url}")
        return

    # Load your AI model here
    # model = load_your_model()

    frame_count = 0
    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Run AI inference
            # results = model.predict(frame)
            # process_results(results)

            # Simulate AI processing time
            # time.sleep(0.01)

            if frame_count % 100 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"Processed {frame_count} frames at {fps:.2f} FPS")

    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        cap.release()

# Test your AI pipeline
process_stream_for_ai('rtsp://localhost:8554/stream1')
```

## Command Reference

```
usage: test_stream_consumer.py [-h] [--all] [--duration DURATION] [--no-fps]
                                [--host HOST] [--port PORT]
                                [streams ...]

positional arguments:
  streams              RTSP stream URLs to test

optional arguments:
  -h, --help           show this help message and exit
  --all                Test all 3 default streams (stream1, stream2, stream3)
  --duration DURATION  Test duration in seconds (default: infinite)
  --no-fps             Disable FPS counter overlay
  --host HOST          RTSP server host (default: localhost)
  --port PORT          RTSP server port (default: 8554)
```

## Performance Tips

1. **Use TCP transport** for more reliable streaming:
   ```python
   # Modify the script or use environment variable
   os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
   ```

2. **Adjust buffer size** for lower latency:
   ```python
   cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimum latency
   ```

3. **Monitor system resources** during tests:
   ```bash
   # In another terminal
   docker stats
   ```

## Next Steps

Once you've verified the streams work with this test script:
1. Integrate with your AI processing pipeline
2. Add your model inference code
3. Implement result handling and storage
4. Scale up to process multiple streams in parallel

Happy testing! 🎥
