#!/usr/bin/env python3
import argparse
import time
from pathlib import Path

import cv2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record from webcam for a fixed duration and save to a folder."
    )
    parser.add_argument(
        "--duration-seconds",
        type=float,
        required=True,
        help="Recording duration in seconds.",
    )
    parser.add_argument(
        "--device-index",
        type=int,
        default=0,
        help="Webcam device index (default: 0).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("videos/webcam"),
        help="Directory to store the recorded video.",
    )
    parser.add_argument(
        "--filename",
        type=str,
        default=None,
        help="Optional output filename (default: auto timestamp).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.duration_seconds <= 0:
        raise ValueError("--duration-seconds must be greater than 0")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(args.device_index)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open webcam device {args.device_index}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 1:
        fps = 30.0

    if args.filename:
        filename = args.filename
    else:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"webcam_{timestamp}.mp4"

    output_path = args.output_dir / filename

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Webcam Preview", frame)
        writer.write(frame)
        if time.time() - start_time >= args.duration_seconds:
            break
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    writer.release()
    cv2.destroyAllWindows()

    print(f"Saved recording to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
