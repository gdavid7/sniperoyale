# Clash Royale Deck Tracker 📱⚔️

**Snipe your opponent's deck at the start of the game - on mobile!**

A React Native mobile application for Android and iOS that automatically detects when you enter a new Clash Royale battle, identifies your opponent's username, and displays their last used deck from RoyaleAPI.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Android%20%7C%20iOS-blue.svg)
![React Native](https://img.shields.io/badge/React%20Native-0.73-61dafb.svg)

---

## 🌟 Features

- **📱 Mobile Native App** - Works directly on Android and iOS devices
- **🎯 Automatic Battle Detection** - Detects when you enter a new Clash Royale match via screenshots
- **🔍 Username Recognition** - Uses OCR to extract opponent usernames from screenshots
- **⚡ Real-time Deck Lookup** - Fetches opponent's last used deck from RoyaleAPI
- **📊 Android Overlay** - Floating window displays opponent's deck over the game
- **🎨 Modern Dark UI** - Clean, gaming-friendly interface
- **🔧 Manual Lookup** - Search any player's deck by username
- **📝 Activity Log** - Track all detections and lookups
- **⚙️ Configurable Settings** - Adjust detection and preferences

---

## 📋 Requirements

### For Android
- **Android**: 7.0 (API 24) or higher
- **Permissions**: Overlay, Camera, Storage
- **RAM**: 2GB minimum
- **Clash Royale**: Installed and playable

### For iOS
- **iOS**: 13.0 or higher
- **Permissions**: Camera, Photo Library
- **RAM**: 2GB minimum
- **Clash Royale**: Installed and playable

### Development Requirements
- **Node.js**: 18 or higher
- **npm**: 8 or higher
- **React Native CLI**: Latest version
- **Android Studio** (for Android development)
- **Xcode** (for iOS development, macOS only)

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/sniperoyale.git
cd sniperoyale
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Install Pods (iOS only)
```bash
cd ios && pod install && cd ..
```

### 4. Setup Tesseract OCR

**Android:**
- Tesseract training data is automatically included via `react-native-tesseract-ocr`

**iOS:**
- Run `pod install` to get Tesseract dependencies

### 5. Run the App

**Android:**
```bash
npm run android
```

**iOS:**
```bash
npm run ios
```

---

## 🎮 Usage

### First Time Setup

1. **Launch the app** on your device
2. **Grant permissions** when prompted:
   - Android: Overlay, Camera, Storage
   - iOS: Camera, Photo Library
3. The app will guide you through the setup

### Automatic Tracking (How It Works)

#### On Android:
1. Open the Deck Tracker app
2. Tap **"Start Tracking"**
3. A floating overlay appears on your screen
4. **Take a screenshot** when you enter a Clash Royale battle (Power + Volume Down)
5. The app detects the screenshot automatically
6. Opponent's deck appears in the overlay!

#### On iOS:
1. Open the Deck Tracker app
2. Tap **"Start Tracking"**
3. **Take a screenshot** when you enter a Clash Royale battle (Side Button + Volume Up)
4. **Return to the Deck Tracker app**
5. The deck will be displayed in the app

### Manual Lookup

1. Open the app
2. Navigate to **Manual Lookup** section
3. Enter the opponent's **username**
4. (Optional) Enter their **clan name** for better filtering
5. Tap **"Search"**
6. View their deck!

---

## 📁 Project Structure

```
sniperoyale/
├── android/                    # Android native code
│   ├── app/
│   │   ├── src/main/java/.../
│   │   │   ├── OverlayModule.java    # Overlay functionality
│   │   │   └── OverlayPackage.java
│   │   └── AndroidManifest.xml       # Permissions
│   └── build.gradle
├── ios/                        # iOS native code
│   └── ClashRoyaleDeckTracker/
│       └── Info.plist          # Permissions
├── src/
│   ├── components/             # React components
│   │   ├── DeckDisplay.tsx
│   │   ├── StatusIndicator.tsx
│   │   ├── ManualLookup.tsx
│   │   └── ActivityLog.tsx
│   └── services/               # Core services
│       ├── PermissionsService.ts     # Permission handling
│       ├── OverlayService.ts         # Android overlay
│       ├── ScreenshotService.ts      # Screenshot detection
│       ├── OCRService.ts             # Text recognition
│       ├── DeckService.ts            # API calls
│       └── TrackingService.ts        # Main orchestrator
├── App.tsx                     # Main app component
├── index.js                    # Entry point
├── package.json                # Dependencies
└── README.md                   # This file
```

---

## 🛠️ How It Works

### Android Flow:
1. User starts tracking → Overlay window appears
2. User takes screenshot of battle start screen
3. `ScreenshotService` detects new screenshot via MediaStore
4. `OCRService` extracts opponent username using Tesseract
5. `DeckService` queries RoyaleAPI for the player's deck
6. Deck cards are displayed in floating overlay

### iOS Flow:
1. User starts tracking
2. User takes screenshot and returns to app
3. `OCRService` processes the latest screenshot
4. Username is extracted and deck is fetched
5. Deck is displayed in the app

---

## 🐛 Troubleshooting

### Android Issues

**Overlay Not Showing:**
- Go to Settings → Apps → CR Deck Tracker → Display over other apps
- Enable the permission
- Restart the app

**Screenshots Not Detected:**
- Check storage permission is granted
- Try taking screenshot again
- Ensure screenshot is in `/Pictures/Screenshots/` directory

**OCR Not Working:**
- Check camera permission is granted
- Ensure screenshot is clear and readable
- Battle start screen must be fully visible

### iOS Issues

**Permissions Denied:**
- Go to Settings → Privacy → Photos → CR Deck Tracker → Enable
- Go to Settings → Privacy → Camera → CR Deck Tracker → Enable
- Restart the app

**No Deck Found:**
- Ensure you took screenshot at battle start (when opponent name is visible)
- Return to the app after taking screenshot
- Username must be clearly visible in screenshot

### General Issues

**No Deck Found:**
- Verify the username is spelled correctly
- Some players may have privacy settings enabled
- Try manual lookup with clan name

**API Errors:**
- Check internet connection
- RoyaleAPI might be rate-limiting requests
- Wait a few seconds and try again

---

## 📱 Platform-Specific Notes

### Android
- **Minimum SDK**: 24 (Android 7.0)
- **Target SDK**: 33 (Android 13)
- **Overlay Feature**: Uses `SYSTEM_ALERT_WINDOW` permission
- **Best Experience**: Android 10+ for seamless screenshot detection

### iOS
- **Minimum Version**: iOS 13.0
- **Limitation**: Cannot draw overlay over other apps (iOS restriction)
- **Workaround**: User must return to app to see detected deck
- **Best Experience**: Use split-screen if available (iPad)

---

## 🔐 Permissions Explained

### Android
- **Overlay**: Display floating window over Clash Royale
- **Storage**: Detect and read screenshots
- **Camera**: OCR processing
- **Internet**: Fetch deck data from RoyaleAPI

### iOS
- **Camera**: Screenshot processing and OCR
- **Photo Library**: Access screenshots
- **Internet**: Fetch deck data from RoyaleAPI

---

## ⚙️ Configuration

### Adjust OCR Regions

Edit `src/services/OCRService.ts`:

```typescript
private static USERNAME_REGIONS: UsernameRegion[] = [
  { name: 'opponent_top', x: 0.25, y: 0.02, width: 0.5, height: 0.08 },
  // Add custom regions based on your device screen
];
```

### Detection Interval

In the app settings, adjust how often to check for new screenshots (default: 2 seconds).

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

**Note:** This app does NOT modify Clash Royale or provide any unfair advantages. It only analyzes publicly available information.

---

## 🙏 Acknowledgments

- [RoyaleAPI](https://royaleapi.com/) for providing player data
- [React Native](https://reactnative.dev/) for the mobile framework
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text recognition
- The React Native community for amazing libraries
- All contributors and users of this project

---

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [Platform-Specific Notes](#-platform-specific-notes)
3. Open an issue on GitHub with:
   - Device model and OS version
   - Steps to reproduce
   - Screenshots if applicable

---

## 🗺️ Roadmap

- [ ] Add deck statistics and win rates
- [ ] Support for more card information
- [ ] Historical deck tracking
- [ ] Cloud sync across devices
- [ ] Widget support
- [ ] Dark/Light theme toggle
- [ ] Multiple language support

---

**Happy Sniping! 🎯📱**
