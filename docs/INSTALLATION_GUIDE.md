# RTSP Load Tester - Complete Installation & Usage Guide

## 📦 What You've Received

A complete, production-ready RTSP load testing system with:
- ✅ Multiple concurrent stream publisher
- ✅ Automatic video looping
- ✅ Built-in test video generator
- ✅ System resource monitoring
- ✅ Docker support
- ✅ Comprehensive logging
- ✅ Example consumer scripts

## 🚀 Quick Installation (4 Steps)

### Step 1: Install uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Or via pip:**
```bash
pip install uv
```

### Step 2: Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH

### Step 3: Install Python Dependencies

```bash
cd rtsp_load_tester
uv sync
```

Or use the automated setup:
```bash
# Unix/Linux/macOS
chmod +x setup.sh
./setup.sh

# Windows/Any OS
uv run python setup.py
```

### Step 4: Download MediaMTX

**Linux (amd64):**
```bash
wget https://github.com/bluenviron/mediamtx/releases/download/v1.5.0/mediamtx_v1.5.0_linux_amd64.tar.gz
tar -xzf mediamtx_v1.5.0_linux_amd64.tar.gz
```

**macOS (Intel):**
```bash
wget https://github.com/bluenviron/mediamtx/releases/download/v1.5.0/mediamtx_v1.5.0_darwin_amd64.tar.gz
tar -xzf mediamtx_v1.5.0_darwin_amd64.tar.gz
```

**macOS (Apple Silicon):**
```bash
wget https://github.com/bluenviron/mediamtx/releases/download/v1.5.0/mediamtx_v1.5.0_darwin_arm64.tar.gz
tar -xzf mediamtx_v1.5.0_darwin_arm64.tar.gz
```

**Windows:**
Download from https://github.com/bluenviron/mediamtx/releases and extract

## 🎬 First Run

### Generate Test Videos (First Time Only)
```bash
uv run python video_generator.py
```

### Start MediaMTX Server (Separate Terminal)
```bash
# Unix/Linux/macOS
./mediamtx

# Windows
mediamtx.exe
```

### Run the Load Tester
```bash
uv run python main.py
```

You should see:
```
╔═══════════════════════════════════════════════════════╗
║         RTSP Load Tester for AI Pipelines            ║
║              Multiple Stream Publisher                ║
╚═══════════════════════════════════════════════════════╝

✓ FFmpeg is installed
✓ All video files exist

RTSP STREAM URLS
================================================================
Your AI pipeline can connect to these streams:

  1. rtsp://localhost:8554/stream1
  2. rtsp://localhost:8554/stream2
  3. rtsp://localhost:8554/stream3
```

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
# Number of concurrent streams
load_test:
  concurrent_streams: 5  # Change this

# Test duration
load_test:
  duration: 3600  # seconds (0 = infinite)

# Add your own videos
video_sources:
  - name: "my_stream"
    video_path: "videos/my_video.mp4"
    loop: true
    fps: 30
```

## 💻 Using the Streams in Your AI Pipeline

### Python Example
```python
import cv2

# Connect to stream
cap = cv2.VideoCapture('rtsp://localhost:8554/stream1')

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Your AI processing here
    # result = model.predict(frame)
    
    cv2.imshow('AI Pipeline', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
```

### Test Stream Consumer
```bash
# Single stream
uv run python consumer_example.py rtsp://localhost:8554/stream1

# Multiple streams
uv run python consumer_example.py rtsp://localhost:8554/stream1 rtsp://localhost:8554/stream2

# No display (headless)
uv run python consumer_example.py rtsp://localhost:8554/stream1 --no-display

# Limited duration
uv run python consumer_example.py rtsp://localhost:8554/stream1 --duration 60
```

### VLC/FFplay
```bash
# VLC
vlc rtsp://localhost:8554/stream1

# FFplay
ffplay rtsp://localhost:8554/stream1
```

## 🐳 Docker Deployment

The Docker setup uses a multi-container architecture with the official MediaMTX image.

### Architecture
- **mediamtx**: Official `bluenviron/mediamtx:latest-ffmpeg` image
- **rtsp-load-tester**: Custom Python application built with uv

### Quick Start
```bash
# Build and run both containers
docker-compose up --build

# Run in detached mode (background)
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Configuration
The Docker setup uses `config.docker.yaml` which points to the `mediamtx` container hostname.

### Accessing Streams
Streams are available on the host at:
- `rtsp://localhost:8554/stream1`
- `rtsp://localhost:8554/stream2`
- `rtsp://localhost:8554/stream3`

### Additional Ports
- `8554`: RTSP port
- `8888`: WebRTC port (MediaMTX)
- `8889`: HLS port (MediaMTX)

## 📊 Monitoring

The system automatically provides:

### Real-Time Status (Every 10 seconds)
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
- Location: `logs/rtsp_load_test_*.log`
- Metrics: `logs/metrics.json`

### Final Report
```json
{
  "test_duration_seconds": 3600,
  "total_streams": 3,
  "streams": [...]
}
```

## 🎯 Common Use Cases

### 1. Basic Load Test
```bash
uv run python main.py
# Default: 3 streams, infinite duration
```

### 2. High Load Test
```yaml
# config.yaml
load_test:
  concurrent_streams: 20
```

### 3. Timed Test
```yaml
# config.yaml
load_test:
  duration: 1800  # 30 minutes
```

### 4. Custom Videos
```bash
# 1. Place your video in videos/
cp my_video.mp4 videos/

# 2. Update config.yaml
video_sources:
  - name: "custom"
    video_path: "videos/my_video.mp4"
    loop: true
    fps: 30

# 3. Run
uv run python main.py
```

### 5. Performance Benchmarking
```bash
# Test stream consumption rate
uv run python consumer_example.py rtsp://localhost:8554/stream1 --duration 60
```

## 🔍 Troubleshooting

### Issue: "FFmpeg not found"
```bash
# Verify installation
ffmpeg -version

# If not found, install:
# Ubuntu: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
```

### Issue: "Connection refused"
**Solution:** Start MediaMTX first in a separate terminal
```bash
./mediamtx
```

### Issue: High CPU usage
**Solutions:**
1. Reduce concurrent streams
2. Use faster preset:
```yaml
publisher:
  preset: "ultrafast"
```
3. Lower bitrate:
```yaml
publisher:
  bitrate: "1M"
```

### Issue: Videos not found
```bash
# Generate test videos
uv run python video_generator.py
```

### Issue: Streams lagging
**Solutions:**
1. Check system resources
2. Reduce video resolution
3. Lower bitrate
4. Reduce concurrent streams

## 📁 Project Files

```
rtsp_load_tester/
├── main.py                   # Main application
├── orchestrator.py           # Stream manager
├── stream_publisher.py       # Individual stream handler
├── video_generator.py        # Test video creator
├── consumer_example.py       # Stream consumer example
├── setup.py                  # Automated setup
├── setup.sh                  # Unix setup script
├── config.yaml              # Configuration
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker container
├── docker-compose.yml       # Docker Compose
├── README.md                # Full documentation
├── QUICKSTART.md            # Quick guide
└── PROJECT_SUMMARY.md       # Project overview
```

## 🎓 Advanced Features

### Custom Encoding Settings
```yaml
publisher:
  codec: "libx264"
  preset: "medium"  # ultrafast, fast, medium, slow
  bitrate: "4M"
  pixel_format: "yuv420p"
```

### Resource Limits
```yaml
limits:
  max_streams: 50
  max_memory_percent: 80
  max_cpu_percent: 90
```

### Different Resolutions
```bash
# Generate custom resolution video
from video_generator import DummyVideoGenerator
gen = DummyVideoGenerator()
gen.generate_color_bars_video("custom.mp4", width=3840, height=2160)  # 4K
```

### Hardware Encoding (if available)
```yaml
publisher:
  codec: "h264_nvenc"  # NVIDIA GPU
  # or
  codec: "h264_qsv"    # Intel QuickSync
```

## 📈 Performance Tips

1. **Start Small**: Begin with 3 streams
2. **Scale Gradually**: Increase by 5 streams at a time
3. **Monitor Resources**: Watch CPU/Memory
4. **Use SSD**: For video file storage
5. **Optimize Preset**: Balance quality vs. performance
6. **Test Network**: Ensure adequate bandwidth

## 🎪 Example Scenarios

### Scenario 1: Test Object Detection Pipeline
```python
import cv2
from your_model import ObjectDetector

detector = ObjectDetector()
cap = cv2.VideoCapture('rtsp://localhost:8554/stream1')

while True:
    ret, frame = cap.read()
    detections = detector.detect(frame)
    # Process detections...
```

### Scenario 2: Multi-Stream Processing
```python
from threading import Thread

def process_stream(url):
    cap = cv2.VideoCapture(url)
    while True:
        ret, frame = cap.read()
        # Process frame...

streams = ['rtsp://localhost:8554/stream1', 
           'rtsp://localhost:8554/stream2']

threads = [Thread(target=process_stream, args=(url,)) for url in streams]
for t in threads: t.start()
```

### Scenario 3: Stress Test
```yaml
# config.yaml - 20 streams for 2 hours
load_test:
  concurrent_streams: 20
  duration: 7200
```

## 🌐 Network Configuration

### Remote Access
```yaml
# config.yaml
rtsp_server:
  host: "0.0.0.0"  # Listen on all interfaces
  base_url: "rtsp://YOUR_SERVER_IP:8554"
```

### Firewall Rules
```bash
# Allow RTSP port
sudo ufw allow 8554/tcp
```

## 📞 Support & Documentation

- **Full README**: `README.md`
- **Quick Start**: `QUICKSTART.md`
- **Project Summary**: `PROJECT_SUMMARY.md`
- **MediaMTX Docs**: https://github.com/bluenviron/mediamtx
- **FFmpeg Docs**: https://ffmpeg.org/documentation.html

## ✅ Quick Validation

Test your setup:
```bash
# 1. Check uv
uv --version

# 2. Check FFmpeg
ffmpeg -version

# 3. Check Python packages
uv pip list | grep -E "opencv|numpy|ffmpeg"

# 4. Validate setup
uv run python main.py --validate

# 5. Generate test videos
uv run python video_generator.py

# 6. Test a stream
# Terminal 1: ./mediamtx
# Terminal 2: uv run python main.py
# Terminal 3: vlc rtsp://localhost:8554/stream1
```

## 🚦 System Requirements

**Minimum:**
- Python 3.8+
- 4GB RAM
- 2 CPU cores
- FFmpeg

**Recommended:**
- Python 3.10+
- 8GB+ RAM
- 4+ CPU cores
- SSD storage
- FFmpeg with hardware encoding

**For High Load (20+ streams):**
- 16GB+ RAM
- 8+ CPU cores
- GPU with hardware encoding
- High-speed storage

---

## 🎉 You're Ready!

1. Install dependencies ✅
2. Start MediaMTX ✅
3. Run load test ✅
4. Connect your AI pipeline ✅

**Happy Testing! 🚀**

For questions or issues, check the troubleshooting section or review the comprehensive README.md.
