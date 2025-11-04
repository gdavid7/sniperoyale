"""
Username Detection Module
Uses OCR to detect usernames from Clash Royale game screen
"""

import cv2
import numpy as np
import pytesseract
import logging
import re
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)


class UsernameDetector:
    """Detects usernames from Clash Royale game screenshots"""

    # Common regions where usernames appear (as percentage of screen)
    # These will need adjustment based on actual Bluestacks resolution
    USERNAME_REGIONS = [
        # Top player name (opponent) - centered at top
        {"name": "opponent_top", "x": 0.25, "y": 0.02, "w": 0.5, "h": 0.08},
        # Top left player name
        {"name": "player_topleft", "x": 0.05, "y": 0.05, "w": 0.3, "h": 0.08},
        # Top right player name
        {"name": "player_topright", "x": 0.65, "y": 0.05, "w": 0.3, "h": 0.08},
        # Battle start screen - larger central username
        {"name": "battle_start", "x": 0.2, "y": 0.35, "w": 0.6, "h": 0.15},
    ]

    def __init__(self):
        # Configure tesseract for better username detection
        self.tesseract_config = '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-'

    def preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """
        Preprocesses image for better OCR results
        - Converts to grayscale
        - Applies thresholding
        - Enhances contrast
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Apply bilateral filter to reduce noise while keeping edges sharp
        filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        return thresh

    def extract_region(self, img: np.ndarray, region: dict) -> np.ndarray:
        """
        Extracts a region from the image based on percentage coordinates
        """
        h, w = img.shape[:2]

        x = int(region["x"] * w)
        y = int(region["y"] * h)
        width = int(region["w"] * w)
        height = int(region["h"] * h)

        # Ensure coordinates are within bounds
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        width = min(width, w - x)
        height = min(height, h - y)

        return img[y:y+height, x:x+width]

    def clean_username(self, text: str) -> str:
        """
        Cleans OCR output to get a valid username
        - Removes special characters
        - Strips whitespace
        - Validates length
        """
        # Remove whitespace
        text = text.strip()

        # Remove any non-alphanumeric except underscore and hyphen
        text = re.sub(r'[^a-zA-Z0-9_-]', '', text)

        return text

    def is_valid_username(self, username: str) -> bool:
        """
        Validates if a string looks like a valid Clash Royale username
        - Length between 3-15 characters
        - Contains alphanumeric characters
        """
        if not username:
            return False

        if len(username) < 3 or len(username) > 15:
            return False

        # Must contain at least one alphanumeric character
        if not re.search(r'[a-zA-Z0-9]', username):
            return False

        return True

    def detect_username_from_region(self, img: np.ndarray, region: dict) -> Optional[str]:
        """
        Attempts to detect a username from a specific region of the image
        """
        try:
            # Extract region
            region_img = self.extract_region(img, region)

            if region_img.size == 0:
                return None

            # Preprocess
            processed = self.preprocess_image(region_img)

            # Try OCR with original
            text1 = pytesseract.image_to_string(processed, config=self.tesseract_config)
            username1 = self.clean_username(text1)

            # Also try inverted (white text on dark background)
            inverted = cv2.bitwise_not(processed)
            text2 = pytesseract.image_to_string(inverted, config=self.tesseract_config)
            username2 = self.clean_username(text2)

            # Choose the better result
            candidates = [username1, username2]
            valid_candidates = [u for u in candidates if self.is_valid_username(u)]

            if valid_candidates:
                # Return the longest valid username (usually more accurate)
                result = max(valid_candidates, key=len)
                logger.info(f"Detected username from {region['name']}: {result}")
                return result

            return None

        except Exception as e:
            logger.error(f"Error detecting username from {region['name']}: {e}")
            return None

    def detect_all_usernames(self, img: np.ndarray) -> List[Tuple[str, str]]:
        """
        Attempts to detect usernames from all known regions
        Returns list of (region_name, username) tuples
        """
        results = []

        for region in self.USERNAME_REGIONS:
            username = self.detect_username_from_region(img, region)
            if username:
                results.append((region["name"], username))

        return results

    def detect_opponent_username(self, img: np.ndarray) -> Optional[str]:
        """
        Specifically tries to detect the opponent's username
        Checks multiple regions and returns the most likely result
        """
        usernames = self.detect_all_usernames(img)

        if not usernames:
            logger.warning("No usernames detected")
            return None

        # Priority order: battle_start > opponent_top > others
        priority = ["battle_start", "opponent_top", "player_topleft", "player_topright"]

        for region_name in priority:
            for detected_region, username in usernames:
                if detected_region == region_name:
                    logger.info(f"Selected username: {username} from {region_name}")
                    return username

        # If no priority match, return first detected
        return usernames[0][1]


def test_detector():
    """Test function to verify username detection"""
    logging.basicConfig(level=logging.INFO)

    detector = UsernameDetector()

    # Test with a sample image if it exists
    import os
    if os.path.exists("test_capture.png"):
        img = cv2.imread("test_capture.png")
        print("Testing username detection on test_capture.png...")

        usernames = detector.detect_all_usernames(img)
        print(f"\nDetected usernames: {usernames}")

        opponent = detector.detect_opponent_username(img)
        print(f"\nSelected opponent username: {opponent}")
    else:
        print("No test_capture.png found. Run screen_capture.py first to create a test image.")


if __name__ == "__main__":
    test_detector()
