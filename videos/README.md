# Videos Directory

## Required Setup

Place your video file(s) in this directory before running the RTSP load tester.

### For Docker Setup

1. **Place your video file here:**
   ```bash
   cp /path/to/your/video.mp4 videos/sample.mp4
   ```

2. **Update config.docker.yaml** if needed:
   ```yaml
   video:
     path: "videos/sample.mp4"  # Make sure this matches your file name
     loop: true
     fps: 30
   ```

3. **Run Docker Compose:**
   ```bash
   docker-compose up --build
   ```

### For Local Development

1. **Place your video file here:**
   ```bash
   cp /path/to/your/video.mp4 videos/sample.mp4
   ```

2. **Update config.yaml** if needed:
   ```yaml
   video:
     path: "videos/sample.mp4"  # Make sure this matches your file name
     loop: true
     fps: 30
   ```

3. **Run the application:**
   ```bash
   uv run python main.py
   ```

## Video Requirements

- **Format:** Any format supported by FFmpeg (MP4, AVI, MKV, etc.)
- **Recommended:** MP4 with H.264 codec for best compatibility
- **Size:** Any size, but consider your system resources for high-resolution videos

## Multiple Streams from Single Video

The application can create multiple RTSP streams from a single video file. Configure the number of streams in your config file:

```yaml
load_test:
  concurrent_streams: 3  # Creates stream1, stream2, stream3
```

All streams will use the same video file specified in the `video.path` configuration.

## Example Video Sources

If you need test videos, you can:
- Use your own video files
- Download sample videos from: https://sample-videos.com/
- Generate dummy videos using: `uv run python video_generator.py` (local only)

## Note

This directory is mounted as a volume in Docker, so any files you place here will be accessible to the containerized application.
