"""
Main Application - Clash Royale Deck Tracker
Orchestrates all components and provides the main entry point
"""

import logging
import time
import sys
from typing import Optional
import os

# Import our modules
from screen_capture import BluestacksCapture
from username_detector import UsernameDetector
from game_detector import GameDetector, GameState
from DeckbyUsername import findByUsername
from gui import DeckTrackerGUI

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deck_tracker.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class DeckTrackerApp:
    """Main application class"""

    def __init__(self):
        # Initialize components
        self.capture = BluestacksCapture()
        self.username_detector = UsernameDetector()
        self.game_detector = GameDetector()
        self.gui = DeckTrackerGUI()

        # State
        self.is_running = False
        self.last_detected_username = None
        self.detection_interval = 2.0  # seconds

        # Setup GUI callbacks
        self.gui.set_callbacks(
            on_start=self.start_tracking,
            on_stop=self.stop_tracking,
            on_manual_lookup=self.manual_lookup
        )

        logger.info("Deck Tracker initialized")

    def start_tracking(self):
        """Starts the automatic tracking loop"""
        logger.info("Starting automatic tracking...")
        self.is_running = True

        # Check if Bluestacks is available
        if not self.capture.find_bluestacks_window():
            error_msg = "Bluestacks window not found! Please start Bluestacks and make sure Clash Royale is visible."
            logger.error(error_msg)
            self.gui.show_error(error_msg)
            self.gui._stop_tracking()
            return

        self.gui.log_message("Connected to Bluestacks emulator", "success")

        # Main tracking loop
        self._tracking_loop()

    def stop_tracking(self):
        """Stops the automatic tracking loop"""
        logger.info("Stopping tracking...")
        self.is_running = False

    def _tracking_loop(self):
        """Main tracking loop that runs continuously"""
        consecutive_errors = 0
        max_errors = 5

        while self.is_running:
            try:
                # Get detection interval from GUI settings
                try:
                    self.detection_interval = float(self.gui.interval_var.get())
                except:
                    self.detection_interval = 2.0

                # Capture screen
                img = self.capture.capture_window()

                if img is None:
                    consecutive_errors += 1
                    logger.warning("Failed to capture screen")

                    if consecutive_errors >= max_errors:
                        error_msg = "Too many capture failures. Please check if Bluestacks is still running."
                        self.gui.show_error(error_msg)
                        self.stop_tracking()
                        self.gui._stop_tracking()
                        break

                    time.sleep(self.detection_interval)
                    continue

                # Reset error counter on success
                consecutive_errors = 0

                # Detect game state
                state = self.game_detector.detect_game_state(img)

                # Check if new battle is starting
                if self.game_detector.is_new_battle_starting(img):
                    logger.info("New battle detected! Attempting to detect username...")
                    self.gui.log_message("🎮 New battle detected! Scanning for username...", "info")

                    # Try to detect username
                    username = self.username_detector.detect_opponent_username(img)

                    if username and username != self.last_detected_username:
                        self.last_detected_username = username
                        logger.info(f"Detected username: {username}")
                        self.gui.log_message(f"✓ Username detected: {username}", "success")

                        # Lookup deck
                        self._lookup_deck(username, "")
                    elif username:
                        logger.debug(f"Username {username} already processed")
                    else:
                        logger.warning("Could not detect username from screen")
                        self.gui.log_message("⚠ Could not detect username. Try manual lookup.", "warning")

                # Sleep before next iteration
                time.sleep(self.detection_interval)

            except Exception as e:
                logger.error(f"Error in tracking loop: {e}", exc_info=True)
                consecutive_errors += 1

                if consecutive_errors >= max_errors:
                    error_msg = f"Critical error in tracking loop: {e}"
                    self.gui.show_error(error_msg)
                    self.stop_tracking()
                    self.gui._stop_tracking()
                    break

                time.sleep(self.detection_interval)

        logger.info("Tracking loop ended")

    def manual_lookup(self, username: str, clan: str = ""):
        """Performs a manual deck lookup"""
        logger.info(f"Manual lookup: {username}, clan: {clan}")
        self._lookup_deck(username, clan)

    def _lookup_deck(self, username: str, clan: str = ""):
        """Looks up a deck and displays it in the GUI"""
        try:
            self.gui.log_message(f"🔍 Searching RoyaleAPI for {username}...", "info")

            # Call the deck lookup function
            card_urls = findByUsername(username, clan)

            if card_urls and len(card_urls) > 0:
                logger.info(f"Found {len(card_urls)} cards for {username}")
                self.gui.log_message(f"✓ Found deck for {username} ({len(card_urls)} cards)", "success")

                # Display in GUI
                self.gui.display_deck(username, card_urls, clan)

            else:
                logger.warning(f"No deck found for {username}")
                self.gui.log_message(f"✗ No deck found for {username}. Check username/clan.", "warning")

        except Exception as e:
            logger.error(f"Error looking up deck: {e}", exc_info=True)
            self.gui.log_message(f"✗ Error looking up deck: {str(e)}", "error")

    def run(self):
        """Starts the application"""
        logger.info("Starting Clash Royale Deck Tracker...")

        # Check dependencies
        if not self._check_dependencies():
            logger.error("Dependency check failed. Please install all requirements.")
            sys.exit(1)

        # Welcome message
        self.gui.log_message("=" * 50, "info")
        self.gui.log_message("Welcome to Clash Royale Deck Tracker!", "success")
        self.gui.log_message("=" * 50, "info")
        self.gui.log_message("Instructions:", "info")
        self.gui.log_message("1. Make sure Bluestacks is running with Clash Royale", "info")
        self.gui.log_message("2. Click 'Start Tracking' to begin automatic detection", "info")
        self.gui.log_message("3. Start a new battle and the app will detect your opponent", "info")
        self.gui.log_message("4. Or use Manual Lookup to search for any player", "info")
        self.gui.log_message("=" * 50, "info")

        # Run GUI
        self.gui.run()

    def _check_dependencies(self) -> bool:
        """Checks if all required dependencies are available"""
        try:
            import cloudscraper
            import bs4
            import cv2
            import pytesseract
            import mss
            import customtkinter
            import PIL
            import win32gui

            logger.info("All dependencies found")
            return True

        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            print(f"\n❌ Missing dependency: {e}")
            print("\nPlease install all requirements:")
            print("pip install -r requirements.txt")
            print("\nNote: You also need to install Tesseract OCR:")
            print("https://github.com/tesseract-ocr/tesseract")
            return False


def main():
    """Main entry point"""
    try:
        app = DeckTrackerApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
