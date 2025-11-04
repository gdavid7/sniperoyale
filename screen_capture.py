"""
Screen Capture Module for Bluestacks Emulator
Handles capturing the emulator window and processing the image
"""

import mss
import mss.tools
import cv2
import numpy as np
import logging
from typing import Optional, Tuple
import win32gui
import win32ui
import win32con
from PIL import Image

logger = logging.getLogger(__name__)


class BluestacksCapture:
    """Handles screen capture from Bluestacks emulator"""

    def __init__(self):
        self.window_title = "BlueStacks"
        self.hwnd = None
        self.sct = mss.mss()

    def find_bluestacks_window(self) -> bool:
        """
        Finds the Bluestacks window handle
        Returns True if found, False otherwise
        """
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "BlueStacks" in title or "Bluestacks" in title:
                    windows.append((hwnd, title))
            return True

        windows = []
        win32gui.EnumWindows(callback, windows)

        if windows:
            self.hwnd = windows[0][0]
            logger.info(f"Found Bluestacks window: {windows[0][1]}")
            return True
        else:
            logger.warning("Bluestacks window not found")
            return False

    def get_window_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Gets the window rectangle coordinates
        Returns (left, top, right, bottom) or None if window not found
        """
        if not self.hwnd:
            if not self.find_bluestacks_window():
                return None

        try:
            rect = win32gui.GetWindowRect(self.hwnd)
            return rect
        except Exception as e:
            logger.error(f"Error getting window rect: {e}")
            return None

    def capture_window(self) -> Optional[np.ndarray]:
        """
        Captures the Bluestacks window
        Returns image as numpy array (OpenCV format) or None if failed
        """
        rect = self.get_window_rect()
        if not rect:
            logger.error("Cannot capture: window not found")
            return None

        left, top, right, bottom = rect
        width = right - left
        height = bottom - top

        try:
            # Use mss for efficient screen capture
            monitor = {
                "top": top,
                "left": left,
                "width": width,
                "height": height
            }

            screenshot = self.sct.grab(monitor)

            # Convert to numpy array
            img = np.array(screenshot)

            # Convert BGRA to BGR (OpenCV format)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            logger.debug(f"Captured window: {width}x{height}")
            return img

        except Exception as e:
            logger.error(f"Error capturing window: {e}")
            return None

    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        """
        Captures a specific region of the Bluestacks window
        Coordinates are relative to the window's top-left corner
        Returns image as numpy array or None if failed
        """
        rect = self.get_window_rect()
        if not rect:
            return None

        window_left, window_top, _, _ = rect

        try:
            monitor = {
                "top": window_top + y,
                "left": window_left + x,
                "width": width,
                "height": height
            }

            screenshot = self.sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            return img

        except Exception as e:
            logger.error(f"Error capturing region: {e}")
            return None

    def save_screenshot(self, filename: str) -> bool:
        """
        Saves a screenshot to file
        Returns True if successful, False otherwise
        """
        img = self.capture_window()
        if img is None:
            return False

        try:
            cv2.imwrite(filename, img)
            logger.info(f"Screenshot saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving screenshot: {e}")
            return False


def test_capture():
    """Test function to verify screen capture works"""
    logging.basicConfig(level=logging.INFO)

    capture = BluestacksCapture()

    if capture.find_bluestacks_window():
        print("✓ Bluestacks window found")

        img = capture.capture_window()
        if img is not None:
            print(f"✓ Captured image: {img.shape}")
            capture.save_screenshot("test_capture.png")
            print("✓ Screenshot saved to test_capture.png")
        else:
            print("✗ Failed to capture image")
    else:
        print("✗ Bluestacks window not found. Make sure Bluestacks is running.")


if __name__ == "__main__":
    test_capture()
