# Docker Setup Guide

## Quick Start

### 1. Prepare Your Video File

Place your video file in the `videos/` directory:

```bash
# Create videos directory if it doesn't exist
mkdir -p videos

# Copy your video file
cp /path/to/your/video.mp4 videos/sample.mp4
```

### 2. Verify Configuration

The default `config.docker.yaml` expects a video at `videos/sample.mp4`. If your video has a different name, update the config:

```yaml
video:
  path: "videos/your-video-name.mp4"  # Change this
  loop: true
  fps: 30

load_test:
  concurrent_streams: 3  # Number of streams to create from the same video
```

### 3. Build and Run

```bash
# Build and start both containers
docker-compose up --build

# Or run in background (detached mode)
docker-compose up -d --build
```

### 4. Access the Streams

Your RTSP streams will be available at:
- `rtsp://localhost:8554/stream1`
- `rtsp://localhost:8554/stream2`
- `rtsp://localhost:8554/stream3`
- ... (based on `concurrent_streams` setting)

### 5. View Logs

```bash
# View all logs
docker-compose logs -f

# View only load tester logs
docker-compose logs -f rtsp-load-tester

# View only MediaMTX logs
docker-compose logs -f mediamtx
```

### 6. Stop the Containers

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Architecture

The Docker setup uses two containers:

1. **mediamtx** (Official `bluenviron/mediamtx:latest-ffmpeg`)
   - RTSP server
   - Ports: 8554 (RTSP), 8888 (WebRTC), 8889 (HLS)

2. **rtsp-load-tester** (Custom Python app with uv)
   - Publishes video streams to MediaMTX
   - Uses video files from mounted `./videos` directory
   - Logs saved to `./logs` directory

## Configuration Options

### Change Number of Streams

Edit `config.docker.yaml`:

```yaml
load_test:
  concurrent_streams: 5  # Creates stream1 through stream5
```

### Change Test Duration

```yaml
load_test:
  duration: 3600  # Run for 1 hour (0 = infinite)
```

### Adjust Video Settings

```yaml
video:
  fps: 25  # Change frame rate
  loop: true  # Enable/disable looping

publisher:
  codec: "libx264"
  preset: "ultrafast"  # ultrafast, fast, medium, slow
  bitrate: "2M"  # Video bitrate
```

## Testing Streams

### Using VLC

```bash
vlc rtsp://localhost:8554/stream1
```

### Using FFplay

```bash
ffplay rtsp://localhost:8554/stream1
```

### Using Python (OpenCV)

```python
import cv2

cap = cv2.VideoCapture('rtsp://localhost:8554/stream1')
while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
```

## Troubleshooting

### Container Exits Immediately

Check logs for errors:
```bash
docker-compose logs rtsp-load-tester
```

Common issues:
- Video file not found (make sure `videos/sample.mp4` exists)
- Config path mismatch (verify `video.path` in config.docker.yaml)

### Streams Not Accessible

1. Check MediaMTX is running:
   ```bash
   docker-compose logs mediamtx
   ```

2. Verify ports are exposed:
   ```bash
   docker ps
   ```

3. Test MediaMTX directly:
   ```bash
   curl http://localhost:8888
   ```

### High CPU Usage

Reduce load by:
1. Decreasing `concurrent_streams`
2. Using faster encoder preset: `preset: "ultrafast"`
3. Lowering bitrate: `bitrate: "1M"`

## Advanced Usage

### Override Config File

Uncomment the config mount in `docker-compose.yml`:

```yaml
volumes:
  - ./videos:/app/videos
  - ./logs:/app/logs
  - ./config.yaml:/app/config.yaml  # Uncomment this
```

Then use your own config.yaml (make sure to use `mediamtx` as hostname).

### Custom Video Path

If your videos are in a different location:

```yaml
# docker-compose.yml
volumes:
  - /custom/path/to/videos:/app/videos
  - ./logs:/app/logs
```

### Run Without Logs Volume

Remove logs volume if you don't need persistent logs:

```yaml
volumes:
  - ./videos:/app/videos
  # - ./logs:/app/logs  # Comment this out
```

## Cleanup

Remove all containers, networks, and images:

```bash
# Stop and remove containers
docker-compose down

# Remove the built image
docker rmi load-test-rtsp-stream-rtsp-load-tester

# Remove MediaMTX image (optional)
docker rmi bluenviron/mediamtx:latest-ffmpeg
```

## Notes

- Videos are mounted from host, not copied during build
- No video generation in Docker - provide your own videos
- The load tester waits 5 seconds for MediaMTX to start
- All streams use the same video file specified in config
- Container uses `uv` for fast Python dependency management
