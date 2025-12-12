#!/usr/bin/env python3
"""
Simple RTSP Stream Consumer Test Script
Tests consuming streams from the RTSP load tester
"""

import cv2
import argparse
import sys
import time
from datetime import datetime


def test_single_stream(stream_url, duration=None, show_fps=True):
    """
    Test consuming a single RTSP stream

    Args:
        stream_url: RTSP URL to consume
        duration: Optional duration in seconds (None = infinite)
        show_fps: Whether to display FPS counter
    """
    print(f"\n{'='*60}")
    print(f"Testing Stream: {stream_url}")
    print(f"{'='*60}\n")

    # Open video capture
    cap = cv2.VideoCapture(stream_url)

    # Set buffer size to minimize latency
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

    if not cap.isOpened():
        print(f"❌ ERROR: Could not open stream: {stream_url}")
        return False

    # Get stream properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"✓ Stream opened successfully")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps}")
    print(f"\nPress 'q' to quit, 's' to take screenshot\n")

    start_time = time.time()
    frame_count = 0
    last_fps_time = time.time()
    fps_counter = 0
    current_fps = 0

    try:
        while True:
            # Check duration limit
            if duration and (time.time() - start_time) >= duration:
                print(f"\n✓ Duration limit reached ({duration}s)")
                break

            ret, frame = cap.read()

            if not ret:
                print("\n❌ Failed to grab frame - stream may have ended")
                break

            frame_count += 1
            fps_counter += 1

            # Calculate FPS
            if time.time() - last_fps_time >= 1.0:
                current_fps = fps_counter / (time.time() - last_fps_time)
                fps_counter = 0
                last_fps_time = time.time()

            # Add FPS overlay
            if show_fps:
                cv2.putText(
                    frame,
                    f"FPS: {current_fps:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    frame,
                    f"Frame: {frame_count}",
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

            # Display frame
            cv2.imshow(f'Stream: {stream_url}', frame)

            # Handle key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n✓ User quit")
                break
            elif key == ord('s'):
                # Take screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📸 Screenshot saved: {filename}")

    except KeyboardInterrupt:
        print("\n✓ Interrupted by user")

    finally:
        elapsed = time.time() - start_time

        # Print statistics
        print(f"\n{'='*60}")
        print(f"STATISTICS")
        print(f"{'='*60}")
        print(f"Total frames: {frame_count}")
        print(f"Duration: {elapsed:.2f}s")
        print(f"Average FPS: {frame_count/elapsed:.2f}")
        print(f"{'='*60}\n")

        cap.release()
        cv2.destroyAllWindows()

    return True


def test_multiple_streams(stream_urls, duration=None):
    """
    Test consuming multiple RTSP streams simultaneously

    Args:
        stream_urls: List of RTSP URLs to consume
        duration: Optional duration in seconds (None = infinite)
    """
    print(f"\n{'='*60}")
    print(f"Testing {len(stream_urls)} Streams Simultaneously")
    print(f"{'='*60}\n")

    captures = []

    # Open all streams
    for i, url in enumerate(stream_urls, 1):
        cap = cv2.VideoCapture(url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

        if not cap.isOpened():
            print(f"❌ ERROR: Could not open stream {i}: {url}")
            continue

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"✓ Stream {i} opened: {url} ({width}x{height})")

        captures.append({
            'cap': cap,
            'url': url,
            'frame_count': 0
        })

    if not captures:
        print("\n❌ No streams could be opened")
        return False

    print(f"\nPress 'q' to quit\n")

    start_time = time.time()

    try:
        while True:
            # Check duration limit
            if duration and (time.time() - start_time) >= duration:
                print(f"\n✓ Duration limit reached ({duration}s)")
                break

            all_ok = True

            # Read and display frames from all streams
            for i, stream in enumerate(captures, 1):
                ret, frame = stream['cap'].read()

                if not ret:
                    print(f"\n❌ Stream {i} failed to grab frame")
                    all_ok = False
                    continue

                stream['frame_count'] += 1

                # Add stream label
                cv2.putText(
                    frame,
                    f"Stream {i}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

                cv2.imshow(f'Stream {i}: {stream["url"]}', frame)

            if not all_ok:
                break

            # Handle key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n✓ User quit")
                break

    except KeyboardInterrupt:
        print("\n✓ Interrupted by user")

    finally:
        elapsed = time.time() - start_time

        # Print statistics
        print(f"\n{'='*60}")
        print(f"STATISTICS")
        print(f"{'='*60}")
        for i, stream in enumerate(captures, 1):
            avg_fps = stream['frame_count'] / elapsed if elapsed > 0 else 0
            print(f"Stream {i}:")
            print(f"  URL: {stream['url']}")
            print(f"  Frames: {stream['frame_count']}")
            print(f"  Avg FPS: {avg_fps:.2f}")
        print(f"Duration: {elapsed:.2f}s")
        print(f"{'='*60}\n")

        # Cleanup
        for stream in captures:
            stream['cap'].release()
        cv2.destroyAllWindows()

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Test RTSP stream consumption",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test single stream
  python test_stream_consumer.py rtsp://localhost:8554/stream1

  # Test with duration limit
  python test_stream_consumer.py rtsp://localhost:8554/stream1 --duration 60

  # Test multiple streams
  python test_stream_consumer.py rtsp://localhost:8554/stream1 rtsp://localhost:8554/stream2

  # Test all 3 default streams
  python test_stream_consumer.py --all

  # Test without FPS display
  python test_stream_consumer.py rtsp://localhost:8554/stream1 --no-fps
        """
    )

    parser.add_argument(
        'streams',
        nargs='*',
        help='RTSP stream URLs to test'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Test all 3 default streams (stream1, stream2, stream3)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        help='Test duration in seconds (default: infinite)'
    )
    parser.add_argument(
        '--no-fps',
        action='store_true',
        help='Disable FPS counter overlay'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='RTSP server host (default: localhost)'
    )
    parser.add_argument(
        '--port',
        default='8554',
        help='RTSP server port (default: 8554)'
    )

    args = parser.parse_args()

    # Determine streams to test
    if args.all:
        stream_urls = [
            f'rtsp://{args.host}:{args.port}/stream1',
            f'rtsp://{args.host}:{args.port}/stream2',
            f'rtsp://{args.host}:{args.port}/stream3'
        ]
    elif args.streams:
        stream_urls = args.streams
    else:
        # Default to stream1
        stream_urls = [f'rtsp://{args.host}:{args.port}/stream1']

    print("\n🎥 RTSP Stream Consumer Test")
    print(f"Testing {len(stream_urls)} stream(s)")

    # Test streams
    if len(stream_urls) == 1:
        success = test_single_stream(
            stream_urls[0],
            duration=args.duration,
            show_fps=not args.no_fps
        )
    else:
        success = test_multiple_streams(
            stream_urls,
            duration=args.duration
        )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
