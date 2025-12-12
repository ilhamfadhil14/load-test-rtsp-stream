#!/usr/bin/env python3
"""
Setup Script for RTSP Load Tester
Automates the setup process
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from loguru import logger


class SetupManager:
    """Manages setup and installation"""
    
    def __init__(self):
        self.system = platform.system()
        self.python_version = sys.version_info
        
    def check_python_version(self):
        """Check if Python version is adequate"""
        logger.info(f"Checking Python version: {self.python_version.major}.{self.python_version.minor}")
        
        if self.python_version.major < 3 or (self.python_version.major == 3 and self.python_version.minor < 8):
            logger.error("Python 3.8 or higher is required")
            return False
        
        logger.info("✓ Python version is adequate")
        return True
    
    def check_ffmpeg(self):
        """Check if FFmpeg is installed"""
        logger.info("Checking for FFmpeg...")
        
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            logger.info("✓ FFmpeg is installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("✗ FFmpeg is not installed")
            self._print_ffmpeg_install_instructions()
            return False
    
    def _print_ffmpeg_install_instructions(self):
        """Print FFmpeg installation instructions"""
        logger.info("\nFFmpeg Installation Instructions:")
        
        if self.system == "Linux":
            logger.info("  Ubuntu/Debian:")
            logger.info("    sudo apt-get update")
            logger.info("    sudo apt-get install ffmpeg")
            logger.info("\n  Fedora/RHEL:")
            logger.info("    sudo dnf install ffmpeg")
        elif self.system == "Darwin":
            logger.info("  macOS (using Homebrew):")
            logger.info("    brew install ffmpeg")
        elif self.system == "Windows":
            logger.info("  Windows:")
            logger.info("    1. Download from: https://ffmpeg.org/download.html")
            logger.info("    2. Extract to C:\\ffmpeg")
            logger.info("    3. Add C:\\ffmpeg\\bin to PATH")
        
        logger.info("")
    
    def install_python_packages(self):
        """Install Python dependencies"""
        logger.info("Installing Python packages...")
        
        requirements_file = Path("requirements.txt")
        if not requirements_file.exists():
            logger.error("requirements.txt not found")
            return False
        
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True
            )
            logger.info("✓ Python packages installed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install packages: {e}")
            return False
    
    def create_directories(self):
        """Create necessary directories"""
        logger.info("Creating directories...")
        
        directories = ["videos", "logs"]
        
        for directory in directories:
            path = Path(directory)
            path.mkdir(exist_ok=True)
            logger.info(f"  ✓ Created: {directory}/")
        
        return True
    
    def check_mediamtx(self):
        """Check for MediaMTX"""
        logger.info("\nChecking for MediaMTX...")
        
        # Check common locations
        locations = [
            Path("./mediamtx"),
            Path("./mediamtx.exe"),
            Path("../mediamtx"),
            Path("../mediamtx.exe"),
        ]
        
        found = False
        for location in locations:
            if location.exists():
                logger.info(f"✓ Found MediaMTX at: {location}")
                found = True
                break
        
        if not found:
            logger.warning("✗ MediaMTX not found in common locations")
            self._print_mediamtx_instructions()
        
        return True
    
    def _print_mediamtx_instructions(self):
        """Print MediaMTX download instructions"""
        logger.info("\nMediaMTX Download Instructions:")
        logger.info("  1. Visit: https://github.com/bluenviron/mediamtx/releases")
        logger.info("  2. Download the appropriate version for your system:")
        
        if self.system == "Linux":
            logger.info("     - mediamtx_vX.X.X_linux_amd64.tar.gz")
        elif self.system == "Darwin":
            logger.info("     - mediamtx_vX.X.X_darwin_amd64.tar.gz (Intel)")
            logger.info("     - mediamtx_vX.X.X_darwin_arm64.tar.gz (Apple Silicon)")
        elif self.system == "Windows":
            logger.info("     - mediamtx_vX.X.X_windows_amd64.zip")
        
        logger.info("  3. Extract the archive")
        logger.info("  4. Place the mediamtx binary in this directory or add to PATH")
        logger.info("")
    
    def generate_test_videos(self):
        """Generate test videos"""
        logger.info("\nGenerating test videos...")
        
        response = input("Generate test videos now? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            try:
                from video_generator import DummyVideoGenerator
                generator = DummyVideoGenerator()
                generator.generate_all_test_videos()
                logger.info("✓ Test videos generated")
                return True
            except Exception as e:
                logger.error(f"Failed to generate videos: {e}")
                return False
        else:
            logger.info("Skipping video generation")
            return True
    
    def run_setup(self):
        """Run complete setup"""
        logger.info("=" * 60)
        logger.info("RTSP Load Tester - Setup")
        logger.info("=" * 60)
        logger.info("")
        
        steps = [
            ("Python Version", self.check_python_version),
            ("FFmpeg", self.check_ffmpeg),
            ("Python Packages", self.install_python_packages),
            ("Directories", self.create_directories),
            ("MediaMTX", self.check_mediamtx),
            ("Test Videos", self.generate_test_videos),
        ]
        
        results = []
        
        for step_name, step_func in steps:
            try:
                result = step_func()
                results.append((step_name, result))
                logger.info("")
            except Exception as e:
                logger.error(f"Error in {step_name}: {e}")
                results.append((step_name, False))
                logger.info("")
        
        # Print summary
        logger.info("=" * 60)
        logger.info("Setup Summary")
        logger.info("=" * 60)
        
        for step_name, result in results:
            status = "✓" if result else "✗"
            logger.info(f"  {status} {step_name}")
        
        logger.info("=" * 60)
        
        all_passed = all(result for _, result in results)
        
        if all_passed:
            logger.info("\n✓ Setup completed successfully!")
            logger.info("\nNext steps:")
            logger.info("  1. Start MediaMTX: ./mediamtx (or mediamtx.exe on Windows)")
            logger.info("  2. Run the load test: python main.py")
            logger.info("")
        else:
            logger.warning("\n⚠ Setup completed with some issues")
            logger.warning("Please resolve the issues marked with ✗ before running the load test")
            logger.info("")
        
        return all_passed


def main():
    """Main entry point"""
    setup = SetupManager()
    success = setup.run_setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
