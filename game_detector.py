"""
Game State Detection Module
Detects when a Clash Royale match starts or is in progress
"""

import cv2
import numpy as np
import logging
from typing import Optional, Dict
from enum import Enum

logger = logging.getLogger(__name__)


class GameState(Enum):
    """Possible game states"""
    UNKNOWN = 0
    MENU = 1
    LOADING = 2
    BATTLE_START = 3  # Battle starting screen with opponent info
    IN_BATTLE = 4     # Active battle
    BATTLE_END = 5    # Battle ending screen


class GameDetector:
    """Detects the current game state from screenshots"""

    def __init__(self):
        # Color ranges for different game elements (in HSV)
        self.color_ranges = {
            # Blue elixir bar (key indicator of active battle)
            "elixir_blue": {
                "lower": np.array([100, 100, 100]),
                "upper": np.array([130, 255, 255])
            },
            # Purple/pink battle start screen background
            "battle_start_bg": {
                "lower": np.array([140, 50, 50]),
                "upper": np.array([170, 255, 255])
            },
            # Orange/yellow victory/defeat screen
            "battle_end_gold": {
                "lower": np.array([15, 100, 100]),
                "upper": np.array([35, 255, 255])
            }
        }

        # Regions to check for game state indicators (as percentage of screen)
        self.check_regions = {
            "elixir_bar": {"x": 0.3, "y": 0.85, "w": 0.4, "h": 0.1},  # Bottom center
            "top_center": {"x": 0.25, "y": 0.0, "w": 0.5, "h": 0.2},  # Top center
            "center": {"x": 0.2, "y": 0.3, "w": 0.6, "h": 0.4},       # Center
        }

        self.last_state = GameState.UNKNOWN
        self.state_confidence = 0.0

    def extract_region(self, img: np.ndarray, region: dict) -> np.ndarray:
        """Extracts a region from the image based on percentage coordinates"""
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

    def calculate_color_percentage(self, img: np.ndarray, color_range: dict) -> float:
        """
        Calculates the percentage of pixels in an image that fall within a color range
        """
        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Create mask
        mask = cv2.inRange(hsv, color_range["lower"], color_range["upper"])

        # Calculate percentage
        total_pixels = mask.size
        colored_pixels = cv2.countNonZero(mask)

        if total_pixels == 0:
            return 0.0

        percentage = (colored_pixels / total_pixels) * 100
        return percentage

    def detect_battle_active(self, img: np.ndarray) -> float:
        """
        Detects if a battle is currently active
        Returns confidence score (0.0 to 1.0)
        """
        # Check for elixir bar at the bottom
        elixir_region = self.extract_region(img, self.check_regions["elixir_bar"])
        elixir_percentage = self.calculate_color_percentage(
            elixir_region,
            self.color_ranges["elixir_blue"]
        )

        # If we detect blue elixir bar, we're likely in battle
        # Typical threshold: >5% of the region should be blue
        confidence = min(elixir_percentage / 10.0, 1.0)

        logger.debug(f"Battle active confidence: {confidence:.2f} (elixir: {elixir_percentage:.1f}%)")
        return confidence

    def detect_battle_start(self, img: np.ndarray) -> float:
        """
        Detects the battle start screen (with opponent info)
        Returns confidence score (0.0 to 1.0)
        """
        # Check center region for battle start colors
        center_region = self.extract_region(img, self.check_regions["center"])
        purple_percentage = self.calculate_color_percentage(
            center_region,
            self.color_ranges["battle_start_bg"]
        )

        # Battle start screen typically has purple/pink background
        confidence = min(purple_percentage / 20.0, 1.0)

        logger.debug(f"Battle start confidence: {confidence:.2f} (purple: {purple_percentage:.1f}%)")
        return confidence

    def detect_battle_end(self, img: np.ndarray) -> float:
        """
        Detects the battle end screen
        Returns confidence score (0.0 to 1.0)
        """
        # Check center region for victory/defeat colors
        center_region = self.extract_region(img, self.check_regions["center"])
        gold_percentage = self.calculate_color_percentage(
            center_region,
            self.color_ranges["battle_end_gold"]
        )

        confidence = min(gold_percentage / 15.0, 1.0)

        logger.debug(f"Battle end confidence: {confidence:.2f} (gold: {gold_percentage:.1f}%)")
        return confidence

    def detect_game_state(self, img: np.ndarray) -> GameState:
        """
        Detects the current game state from a screenshot
        Returns the most likely game state
        """
        if img is None or img.size == 0:
            return GameState.UNKNOWN

        try:
            # Calculate confidence for each state
            battle_active_conf = self.detect_battle_active(img)
            battle_start_conf = self.detect_battle_start(img)
            battle_end_conf = self.detect_battle_end(img)

            # Determine state based on highest confidence
            confidences = {
                GameState.IN_BATTLE: battle_active_conf,
                GameState.BATTLE_START: battle_start_conf,
                GameState.BATTLE_END: battle_end_conf,
            }

            max_state = max(confidences, key=confidences.get)
            max_conf = confidences[max_state]

            # Threshold for detection (minimum confidence)
            MIN_CONFIDENCE = 0.3

            if max_conf < MIN_CONFIDENCE:
                state = GameState.MENU
            else:
                state = max_state

            self.state_confidence = max_conf

            # Only log state changes
            if state != self.last_state:
                logger.info(f"Game state changed: {self.last_state.name} -> {state.name} (confidence: {max_conf:.2f})")
                self.last_state = state

            return state

        except Exception as e:
            logger.error(f"Error detecting game state: {e}")
            return GameState.UNKNOWN

    def is_new_battle_starting(self, img: np.ndarray) -> bool:
        """
        Specifically checks if a new battle is starting
        This is the trigger for username detection
        """
        state = self.detect_game_state(img)
        return state == GameState.BATTLE_START and self.state_confidence > 0.4

    def get_state_info(self) -> Dict:
        """Returns information about the current detected state"""
        return {
            "state": self.last_state.name,
            "confidence": self.state_confidence
        }


def test_game_detector():
    """Test function to verify game state detection"""
    logging.basicConfig(level=logging.INFO)

    detector = GameDetector()

    # Test with a sample image if it exists
    import os
    if os.path.exists("test_capture.png"):
        img = cv2.imread("test_capture.png")
        print("Testing game state detection on test_capture.png...")

        state = detector.detect_game_state(img)
        info = detector.get_state_info()

        print(f"\nDetected state: {info['state']}")
        print(f"Confidence: {info['confidence']:.2f}")

        if detector.is_new_battle_starting(img):
            print("\n✓ New battle detected! Time to lookup opponent deck.")
        else:
            print("\n✗ No new battle detected.")

        # Save debug visualization
        h, w = img.shape[:2]
        for name, region in detector.check_regions.items():
            x = int(region["x"] * w)
            y = int(region["y"] * h)
            width = int(region["w"] * w)
            height = int(region["h"] * h)
            cv2.rectangle(img, (x, y), (x+width, y+height), (0, 255, 0), 2)
            cv2.putText(img, name, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imwrite("test_game_state.png", img)
        print("\nDebug image saved to test_game_state.png")

    else:
        print("No test_capture.png found. Run screen_capture.py first to create a test image.")


if __name__ == "__main__":
    test_game_detector()
