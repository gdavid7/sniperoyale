# Clash Royale Deck Tracker 🎮

**Snipe your opponent's deck at the start of the game!**

An automated deck tracking application for Clash Royale players using Bluestacks emulator. Automatically detects when you enter a new battle, identifies your opponent's username, and displays their last used deck from RoyaleAPI.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

---

## 🌟 Features

- **Automatic Battle Detection** - Detects when you enter a new Clash Royale match
- **Opponent Username Recognition** - Uses OCR to extract opponent usernames from the game screen
- **Real-time Deck Lookup** - Fetches opponent's last used deck from RoyaleAPI
- **Modern GUI** - Clean, dark-themed interface built with CustomTkinter
- **Manual Lookup** - Search any player's deck by username
- **Activity Log** - Track all detections and lookups
- **Configurable Settings** - Adjust detection intervals and preferences

---

## 📋 Requirements

### System Requirements
- **Operating System**: Windows (for Bluestacks compatibility)
- **Python**: 3.8 or higher
- **Bluestacks**: Any recent version
- **Tesseract OCR**: For text recognition

### Python Dependencies
All Python dependencies are listed in `requirements.txt`

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/sniperoyale.git
cd sniperoyale
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

**Windows:**
1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer and note the installation path (default: `C:\Program Files\Tesseract-OCR`)
3. Add Tesseract to your system PATH, or configure it in the app settings

**Verify Installation:**
```bash
tesseract --version
```

### 4. (Optional) Configure Settings
Copy the example configuration file:
```bash
cp config.example.env .env
```

Edit `.env` to customize settings like Tesseract path, detection intervals, etc.

---

## 🎮 Usage

### Starting the Application

1. **Launch Bluestacks** and open Clash Royale
2. **Run the Deck Tracker**:
   ```bash
   python main.py
   ```

### Automatic Tracking

1. Click **"Start Tracking"** in the GUI
2. The app will monitor your game screen
3. When you enter a new battle, it will:
   - Detect the battle start screen
   - Extract your opponent's username
   - Look up their deck on RoyaleAPI
   - Display the cards in the GUI

### Manual Lookup

1. Enter a username in the "Manual Lookup" field
2. (Optional) Enter a clan name to filter results
3. Click **"Lookup"**
4. The deck will be displayed in the "Deck Display" tab

### Settings

Navigate to the **"Settings"** tab to:
- Enable/disable auto-detection
- Toggle notifications
- Adjust detection interval (how often to scan the screen)

---

## 📁 Project Structure

```
sniperoyale/
├── main.py                 # Main application entry point
├── gui.py                  # GUI interface (CustomTkinter)
├── screen_capture.py       # Bluestacks screen capture module
├── game_detector.py        # Game state detection
├── username_detector.py    # OCR username extraction
├── DeckbyUsername.py       # RoyaleAPI deck lookup
├── deck_to_image.py        # Card image processing
├── requirements.txt        # Python dependencies
├── config.example.env      # Example configuration
├── .gitignore             # Git ignore rules
├── LICENSE                # MIT License
└── README.md              # This file
```

---

## 🛠️ How It Works

1. **Screen Capture**: Captures the Bluestacks window using the `mss` library
2. **Game State Detection**: Analyzes colors and patterns to detect battle start screens
3. **Username Extraction**: Uses Tesseract OCR to read opponent usernames
4. **Deck Lookup**: Searches RoyaleAPI for the player's profile and deck
5. **Display**: Shows card images in the GUI

---

## 🐛 Troubleshooting

### Bluestacks Not Detected
- Ensure Bluestacks is running and visible (not minimized)
- Check that the window title contains "BlueStacks"
- Try restarting the application

### Username Not Detected
- Ensure the battle start screen is fully visible
- Try adjusting the detection regions in `username_detector.py`
- Check that Tesseract is properly installed

### No Deck Found
- Verify the username is spelled correctly
- Some players may have privacy settings enabled
- Try specifying the clan name for better filtering

### OCR Errors
- Verify Tesseract installation: `tesseract --version`
- On Windows, ensure Tesseract is in your PATH or configure the path in `.env`

---

## 📝 Configuration

### Detection Regions

Username detection regions can be adjusted in `username_detector.py`:

```python
USERNAME_REGIONS = [
    {"name": "opponent_top", "x": 0.25, "y": 0.02, "w": 0.5, "h": 0.08},
    # Add more regions as needed
]
```

### Game State Colors

Game state detection colors can be tuned in `game_detector.py`:

```python
self.color_ranges = {
    "elixir_blue": {
        "lower": np.array([100, 100, 100]),
        "upper": np.array([130, 255, 255])
    },
    # Adjust HSV ranges for your screen
}
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is for educational purposes only. Use at your own risk. The developers are not responsible for any consequences of using this application. Make sure to comply with Clash Royale's Terms of Service.

---

## 🙏 Acknowledgments

- [RoyaleAPI](https://royaleapi.com/) for providing player data
- [Bluestacks](https://www.bluestacks.com/) for the Android emulator
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text recognition
- All contributors and users of this project

---

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an issue on GitHub
3. Provide logs from `deck_tracker.log`

---

**Happy Sniping! 🎯**
