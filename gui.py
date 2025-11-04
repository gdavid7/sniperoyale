"""
GUI Module for Clash Royale Deck Tracker
Modern UI using customtkinter
"""

import customtkinter as ctk
from tkinter import scrolledtext
import logging
from typing import Optional, Callable, List
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading

logger = logging.getLogger(__name__)

# Set theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DeckTrackerGUI:
    """Main GUI for the Deck Tracker application"""

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Clash Royale Deck Tracker")
        self.root.geometry("800x600")

        # Callbacks
        self.on_start_callback: Optional[Callable] = None
        self.on_stop_callback: Optional[Callable] = None
        self.on_manual_lookup_callback: Optional[Callable] = None

        # State
        self.is_running = False

        self._create_widgets()

    def _create_widgets(self):
        """Creates all GUI widgets"""

        # Main container
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Header frame
        header_frame = ctk.CTkFrame(self.root)
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        title_label = ctk.CTkLabel(
            header_frame,
            text="🎮 Clash Royale Deck Tracker",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=10)

        # Control frame
        control_frame = ctk.CTkFrame(self.root)
        control_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Status indicator
        self.status_frame = ctk.CTkFrame(control_frame)
        self.status_frame.pack(side="left", padx=10, pady=10)

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="● Stopped",
            font=ctk.CTkFont(size=14),
            text_color="red"
        )
        self.status_label.pack(padx=10, pady=5)

        # Start/Stop button
        self.start_stop_btn = ctk.CTkButton(
            control_frame,
            text="Start Tracking",
            command=self._toggle_tracking,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_stop_btn.pack(side="left", padx=10, pady=10)

        # Manual lookup section
        manual_frame = ctk.CTkFrame(control_frame)
        manual_frame.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        ctk.CTkLabel(
            manual_frame,
            text="Manual Lookup:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=5)

        self.username_entry = ctk.CTkEntry(
            manual_frame,
            placeholder_text="Username",
            width=150
        )
        self.username_entry.pack(side="left", padx=5)

        self.clan_entry = ctk.CTkEntry(
            manual_frame,
            placeholder_text="Clan (optional)",
            width=150
        )
        self.clan_entry.pack(side="left", padx=5)

        self.lookup_btn = ctk.CTkButton(
            manual_frame,
            text="Lookup",
            command=self._manual_lookup,
            width=100
        )
        self.lookup_btn.pack(side="left", padx=5)

        # Main content frame with tabs
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        # Deck tab
        self.tab_deck = self.tabview.add("Deck Display")
        self.tab_deck.grid_columnconfigure(0, weight=1)
        self.tab_deck.grid_rowconfigure(0, weight=1)

        # Scrollable frame for deck cards
        self.deck_frame = ctk.CTkScrollableFrame(self.tab_deck)
        self.deck_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.deck_info_label = ctk.CTkLabel(
            self.deck_frame,
            text="No deck loaded. Start tracking or perform a manual lookup.",
            font=ctk.CTkFont(size=14)
        )
        self.deck_info_label.pack(pady=20)

        # Cards container
        self.cards_container = ctk.CTkFrame(self.deck_frame)
        self.cards_container.pack(pady=10, fill="both", expand=True)

        # Log tab
        self.tab_log = self.tabview.add("Activity Log")
        self.tab_log.grid_columnconfigure(0, weight=1)
        self.tab_log.grid_rowconfigure(0, weight=1)

        # Log text area
        self.log_text = ctk.CTkTextbox(self.tab_log, wrap="word")
        self.log_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Settings tab
        self.tab_settings = self.tabview.add("Settings")

        settings_container = ctk.CTkFrame(self.tab_settings)
        settings_container.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(
            settings_container,
            text="Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)

        # Auto-detection toggle
        self.auto_detect_var = ctk.BooleanVar(value=True)
        self.auto_detect_check = ctk.CTkCheckBox(
            settings_container,
            text="Auto-detect new battles",
            variable=self.auto_detect_var,
            font=ctk.CTkFont(size=14)
        )
        self.auto_detect_check.pack(pady=5, anchor="w")

        # Show notifications toggle
        self.show_notifications_var = ctk.BooleanVar(value=True)
        self.notifications_check = ctk.CTkCheckBox(
            settings_container,
            text="Show notifications",
            variable=self.show_notifications_var,
            font=ctk.CTkFont(size=14)
        )
        self.notifications_check.pack(pady=5, anchor="w")

        # Detection interval
        interval_frame = ctk.CTkFrame(settings_container)
        interval_frame.pack(pady=10, fill="x")

        ctk.CTkLabel(
            interval_frame,
            text="Detection interval (seconds):",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5)

        self.interval_var = ctk.StringVar(value="2")
        self.interval_entry = ctk.CTkEntry(
            interval_frame,
            textvariable=self.interval_var,
            width=80
        )
        self.interval_entry.pack(side="left", padx=5)

        # Footer
        footer_frame = ctk.CTkFrame(self.root)
        footer_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")

        footer_label = ctk.CTkLabel(
            footer_frame,
            text="Ensure Bluestacks is running and Clash Royale is visible",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        footer_label.pack(pady=5)

    def _toggle_tracking(self):
        """Toggles the tracking state"""
        if self.is_running:
            self._stop_tracking()
        else:
            self._start_tracking()

    def _start_tracking(self):
        """Starts the tracking process"""
        self.is_running = True
        self.start_stop_btn.configure(text="Stop Tracking")
        self.status_label.configure(text="● Running", text_color="green")
        self.log_message("Tracking started...")

        if self.on_start_callback:
            threading.Thread(target=self.on_start_callback, daemon=True).start()

    def _stop_tracking(self):
        """Stops the tracking process"""
        self.is_running = False
        self.start_stop_btn.configure(text="Start Tracking")
        self.status_label.configure(text="● Stopped", text_color="red")
        self.log_message("Tracking stopped.")

        if self.on_stop_callback:
            self.on_stop_callback()

    def _manual_lookup(self):
        """Performs a manual username lookup"""
        username = self.username_entry.get().strip()
        clan = self.clan_entry.get().strip()

        if not username:
            self.log_message("Error: Please enter a username", "error")
            return

        self.log_message(f"Looking up: {username}" + (f" (clan: {clan})" if clan else ""))

        if self.on_manual_lookup_callback:
            threading.Thread(
                target=self.on_manual_lookup_callback,
                args=(username, clan),
                daemon=True
            ).start()

    def log_message(self, message: str, level: str = "info"):
        """Adds a message to the log"""
        timestamp = logging.Formatter('%(asctime)s').format(logging.LogRecord(
            name="", level=0, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        ))

        color_tag = {
            "info": "white",
            "warning": "yellow",
            "error": "red",
            "success": "green"
        }.get(level, "white")

        log_entry = f"[{timestamp}] {message}\n"

        self.log_text.insert("end", log_entry)
        self.log_text.see("end")

        # Also log to logger
        getattr(logger, level if level in ["info", "warning", "error"] else "info")(message)

    def display_deck(self, username: str, card_urls: List[str], clan: str = ""):
        """Displays a deck in the GUI"""
        # Update info label
        info_text = f"Player: {username}"
        if clan:
            info_text += f" | Clan: {clan}"
        info_text += f" | Cards: {len(card_urls)}"

        self.deck_info_label.configure(text=info_text)

        # Clear previous cards
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        # Display cards in a grid
        if not card_urls:
            no_cards_label = ctk.CTkLabel(
                self.cards_container,
                text="No cards found",
                font=ctk.CTkFont(size=14)
            )
            no_cards_label.pack(pady=20)
            return

        # Create grid
        cols = 4
        for i, url in enumerate(card_urls):
            row = i // cols
            col = i % cols

            card_frame = ctk.CTkFrame(self.cards_container)
            card_frame.grid(row=row, column=col, padx=10, pady=10)

            # Load image in background thread
            self._load_card_image(card_frame, url)

        # Switch to deck tab
        self.tabview.set("Deck Display")

    def _load_card_image(self, frame: ctk.CTkFrame, url: str):
        """Loads a card image from URL and displays it"""
        def load():
            try:
                response = requests.get(url, timeout=5)
                img = Image.open(BytesIO(response.content))

                # Resize to reasonable size
                img = img.resize((120, 140), Image.Resampling.LANCZOS)

                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)

                # Update frame on main thread
                self.root.after(0, lambda: self._display_card_image(frame, photo))

            except Exception as e:
                logger.error(f"Error loading card image: {e}")
                self.root.after(0, lambda: self._display_card_error(frame))

        threading.Thread(target=load, daemon=True).start()

    def _display_card_image(self, frame: ctk.CTkFrame, photo: ImageTk.PhotoImage):
        """Displays a card image in the frame"""
        label = ctk.CTkLabel(frame, image=photo, text="")
        label.image = photo  # Keep a reference
        label.pack(padx=5, pady=5)

    def _display_card_error(self, frame: ctk.CTkFrame):
        """Displays an error message in place of a card"""
        label = ctk.CTkLabel(frame, text="Failed to\nload card", text_color="red")
        label.pack(padx=5, pady=5)

    def show_error(self, message: str):
        """Shows an error message"""
        self.log_message(f"ERROR: {message}", "error")

    def set_callbacks(self, on_start: Callable, on_stop: Callable, on_manual_lookup: Callable):
        """Sets callback functions"""
        self.on_start_callback = on_start
        self.on_stop_callback = on_stop
        self.on_manual_lookup_callback = on_manual_lookup

    def run(self):
        """Starts the GUI main loop"""
        self.root.mainloop()


if __name__ == "__main__":
    # Test GUI
    logging.basicConfig(level=logging.INFO)

    def test_start():
        print("Start callback")

    def test_stop():
        print("Stop callback")

    def test_lookup(username, clan):
        print(f"Lookup: {username}, {clan}")

    gui = DeckTrackerGUI()
    gui.set_callbacks(test_start, test_stop, test_lookup)
    gui.log_message("GUI initialized", "success")
    gui.run()
