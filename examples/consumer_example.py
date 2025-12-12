"""
Example RTSP Stream Consumer
Demonstrates how to consume RTSP streams for AI pipeline testing
"""

import cv2
import time
import argparse
from threading import Thread, Event
from loguru import logger


class RTSPConsumer:
    """Simple RTSP stream consumer for testing"""
    
    def __init__(self, rtsp_url: str, display: bool = True):
        """
        Initialize RTSP consumer
        
        Args:
            rtsp_url: RTSP stream URL
            display: Whether to display video window
        """
        self.rtsp_url = rtsp_url
        self.display = display
        self.running = Event()
        self.frame_count = 0
        self.error_count = 0
        self.start_time = None
        
    def consume(self, duration: int = 0):
        """
        Consume stream for specified duration
        
        Args:
            duration: Duration in seconds (0 = infinite)
        """
        logger.info(f"Connecting to: {self.rtsp_url}")
        
        cap = cv2.VideoCapture(self.rtsp_url)
        
        if not cap.isOpened():
            logger.error(f"Failed to open stream: {self.rtsp_url}")
            return
        
        # Get stream properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        logger.info(f"Stream opened: {width}x{height} @ {fps}fps")
        
        self.running.set()
        self.start_time = time.time()
        
        last_report = time.time()
        report_interval = 5  # Report every 5 seconds
        
        try:
            while self.running.is_set():
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning("Failed to read frame")
                    self.error_count += 1
                    
                    if self.error_count > 10:
                        logger.error("Too many errors, stopping")
                        break
                    
                    time.sleep(0.1)
                    continue
                
                self.frame_count += 1
                
                # Add frame info overlay
                if self.display:
                    elapsed = time.time() - self.start_time
                    current_fps = self.frame_count / elapsed if elapsed > 0 else 0
                    
                    info_text = f"Frame: {self.frame_count} | FPS: {current_fps:.1f} | Errors: {self.error_count}"
                    cv2.putText(
                        frame, info_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                    )
                    
                    cv2.imshow(f'RTSP Stream: {self.rtsp_url}', frame)
                    
                    # Exit on 'q' key
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        logger.info("User requested exit")
                        break
                
                # Periodic status report
                current_time = time.time()
                if current_time - last_report >= report_interval:
                    elapsed = current_time - self.start_time
                    current_fps = self.frame_count / elapsed if elapsed > 0 else 0
                    
                    logger.info(
                        f"Status: Frames={self.frame_count}, "
                        f"FPS={current_fps:.2f}, "
                        f"Errors={self.error_count}, "
                        f"Elapsed={elapsed:.1f}s"
                    )
                    last_report = current_time
                
                # Check duration limit
                if duration > 0 and (time.time() - self.start_time) >= duration:
                    logger.info(f"Duration limit reached ({duration}s)")
                    break
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error consuming stream: {e}")
        finally:
            cap.release()
            if self.display:
                cv2.destroyAllWindows()
            
            self._print_summary()
    
    def _print_summary(self):
        """Print consumption summary"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        logger.info("=" * 60)
        logger.info("CONSUMPTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Stream URL: {self.rtsp_url}")
        logger.info(f"Total Frames: {self.frame_count}")
        logger.info(f"Total Errors: {self.error_count}")
        logger.info(f"Duration: {elapsed:.2f}s")
        logger.info(f"Average FPS: {avg_fps:.2f}")
        logger.info("=" * 60)
    
    def stop(self):
        """Stop consuming stream"""
        self.running.clear()


class MultiStreamConsumer:
    """Consume multiple RTSP streams in parallel"""
    
    def __init__(self, stream_urls: list, display: bool = True):
        """
        Initialize multi-stream consumer
        
        Args:
            stream_urls: List of RTSP stream URLs
            display: Whether to display video windows
        """
        self.stream_urls = stream_urls
        self.display = display
        self.consumers = []
        self.threads = []
    
    def start(self, duration: int = 0):
        """
        Start consuming all streams
        
        Args:
            duration: Duration in seconds (0 = infinite)
        """
        logger.info(f"Starting consumption of {len(self.stream_urls)} streams")
        
        for url in self.stream_urls:
            consumer = RTSPConsumer(url, self.display)
            thread = Thread(target=consumer.consume, args=(duration,), daemon=True)
            
            self.consumers.append(consumer)
            self.threads.append(thread)
            
            thread.start()
            time.sleep(0.5)  # Small delay between starts
        
        logger.info("All consumers started")
        
        # Wait for all threads
        try:
            for thread in self.threads:
                thread.join()
        except KeyboardInterrupt:
            logger.info("Stopping all consumers...")
            self.stop()
    
    def stop(self):
        """Stop all consumers"""
        for consumer in self.consumers:
            consumer.stop()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="RTSP Stream Consumer - Test your RTSP streams"
    )
    parser.add_argument(
        "urls",
        nargs="+",
        help="RTSP stream URLs to consume"
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Don't display video windows"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=0,
        help="Duration in seconds (0 = infinite)"
    )
    
    args = parser.parse_args()
    
    display = not args.no_display
    
    if len(args.urls) == 1:
        # Single stream
        consumer = RTSPConsumer(args.urls[0], display)
        consumer.consume(duration=args.duration)
    else:
        # Multiple streams
        consumer = MultiStreamConsumer(args.urls, display)
        consumer.start(duration=args.duration)


if __name__ == "__main__":
    main()
