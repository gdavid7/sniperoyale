/**
 * Screenshot Service
 * Handles capturing and monitoring screenshots
 */

import { Platform, NativeModules } from 'react-native';
import RNFS from 'react-native-fs';

const { ScreenshotDetector } = NativeModules;

export interface ScreenshotData {
  uri: string;
  timestamp: number;
  width: number;
  height: number;
}

export class ScreenshotService {
  private static listeners: ((screenshot: ScreenshotData) => void)[] = [];
  private static isMonitoring = false;
  private static detectorSubscription: any = null;

  /**
   * Start monitoring for new screenshots
   */
  static async startMonitoring(
    callback: (screenshot: ScreenshotData) => void
  ): Promise<boolean> {
    if (this.isMonitoring) {
      console.warn('Screenshot monitoring already active');
      return true;
    }

    try {
      this.listeners.push(callback);

      if (Platform.OS === 'android') {
        return await this.startAndroidMonitoring();
      } else {
        return await this.startIOSMonitoring();
      }
    } catch (error) {
      console.error('Error starting screenshot monitoring:', error);
      return false;
    }
  }

  /**
   * Stop monitoring screenshots
   */
  static stopMonitoring(): void {
    this.isMonitoring = false;
    this.listeners = [];

    if (this.detectorSubscription) {
      this.detectorSubscription.remove();
      this.detectorSubscription = null;
    }
  }

  /**
   * Android-specific screenshot monitoring
   */
  private static async startAndroidMonitoring(): Promise<boolean> {
    try {
      // Use MediaStore observer to detect new screenshots
      if (ScreenshotDetector && ScreenshotDetector.startDetection) {
        this.isMonitoring = true;

        // Poll screenshots directory
        this.pollScreenshotsDirectory();

        return true;
      }

      console.warn('ScreenshotDetector not available, using fallback');
      return false;
    } catch (error) {
      console.error('Error in Android screenshot monitoring:', error);
      return false;
    }
  }

  /**
   * iOS-specific screenshot monitoring
   */
  private static async startIOSMonitoring(): Promise<boolean> {
    try {
      // iOS doesn't allow automatic screenshot detection
      // User must manually trigger analysis
      console.log('iOS: Manual screenshot analysis mode');
      this.isMonitoring = true;
      return true;
    } catch (error) {
      console.error('Error in iOS screenshot monitoring:', error);
      return false;
    }
  }

  /**
   * Poll screenshots directory for new files
   */
  private static pollScreenshotsDirectory(): void {
    const screenshotsPath =
      Platform.OS === 'android'
        ? `${RNFS.ExternalStorageDirectoryPath}/Pictures/Screenshots`
        : `${RNFS.DocumentDirectoryPath}/Screenshots`;

    let lastCheckTime = Date.now();

    const checkInterval = setInterval(async () => {
      if (!this.isMonitoring) {
        clearInterval(checkInterval);
        return;
      }

      try {
        const files = await RNFS.readDir(screenshotsPath);

        // Find screenshots created after last check
        const newScreenshots = files
          .filter(file => {
            const mtime = new Date(file.mtime).getTime();
            return mtime > lastCheckTime && file.name.toLowerCase().includes('screenshot');
          })
          .sort((a, b) => new Date(b.mtime).getTime() - new Date(a.mtime).getTime());

        if (newScreenshots.length > 0) {
          const latest = newScreenshots[0];

          const screenshotData: ScreenshotData = {
            uri: `file://${latest.path}`,
            timestamp: new Date(latest.mtime).getTime(),
            width: 0,
            height: 0,
          };

          // Notify all listeners
          this.listeners.forEach(callback => callback(screenshotData));

          lastCheckTime = Date.now();
        }
      } catch (error) {
        console.error('Error polling screenshots:', error);
      }
    }, 2000); // Check every 2 seconds
  }

  /**
   * Take a screenshot programmatically (requires native module)
   */
  static async captureScreen(): Promise<ScreenshotData | null> {
    try {
      if (ScreenshotDetector && ScreenshotDetector.captureScreen) {
        const result = await ScreenshotDetector.captureScreen();
        return result;
      }

      console.warn('Screen capture not available');
      return null;
    } catch (error) {
      console.error('Error capturing screen:', error);
      return null;
    }
  }

  /**
   * Analyze an existing screenshot
   */
  static async analyzeScreenshot(uri: string): Promise<ScreenshotData> {
    try {
      const stats = await RNFS.stat(uri);

      return {
        uri,
        timestamp: new Date(stats.mtime).getTime(),
        width: 0,
        height: 0,
      };
    } catch (error) {
      console.error('Error analyzing screenshot:', error);
      throw error;
    }
  }
}
