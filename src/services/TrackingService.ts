/**
 * Tracking Service
 * Orchestrates screenshot monitoring, OCR, and deck lookup
 */

import { ScreenshotService, ScreenshotData } from './ScreenshotService';
import { OCRService } from './OCRService';
import { DeckService, PlayerDeck } from './DeckService';

export interface TrackingCallbacks {
  onBattleDetected?: () => void;
  onUsernameDetected?: (username: string) => void;
  onDeckFound?: (username: string, deck: PlayerDeck) => void;
  onError?: (error: string) => void;
}

export class TrackingService {
  private static isActive = false;
  private static callbacks: TrackingCallbacks = {};
  private static lastProcessedUsername: string | null = null;

  /**
   * Start tracking
   */
  static async startTracking(callbacks: TrackingCallbacks): Promise<boolean> {
    if (this.isActive) {
      console.warn('Tracking already active');
      return true;
    }

    try {
      this.callbacks = callbacks;
      this.lastProcessedUsername = null;

      // Start screenshot monitoring
      const started = await ScreenshotService.startMonitoring(
        this.handleNewScreenshot.bind(this)
      );

      if (started) {
        this.isActive = true;
        console.log('Tracking started successfully');
        return true;
      } else {
        console.error('Failed to start screenshot monitoring');
        return false;
      }
    } catch (error) {
      console.error('Error starting tracking:', error);
      this.callbacks.onError?.(`Failed to start tracking: ${error}`);
      return false;
    }
  }

  /**
   * Stop tracking
   */
  static async stopTracking(): Promise<void> {
    this.isActive = false;
    ScreenshotService.stopMonitoring();
    this.callbacks = {};
    this.lastProcessedUsername = null;
    console.log('Tracking stopped');
  }

  /**
   * Handle new screenshot detected
   */
  private static async handleNewScreenshot(screenshot: ScreenshotData): Promise<void> {
    if (!this.isActive) {
      return;
    }

    try {
      console.log('New screenshot detected:', screenshot.uri);

      // Check if it's a battle start screen
      const isBattle = await OCRService.isBattleStartScreen(screenshot.uri);

      if (!isBattle) {
        console.log('Not a battle start screen, ignoring');
        return;
      }

      console.log('Battle start screen detected!');
      this.callbacks.onBattleDetected?.();

      // Extract username
      const username = await OCRService.extractUsername(screenshot.uri);

      if (!username) {
        console.warn('Could not extract username');
        this.callbacks.onError?.('Could not detect username from screenshot');
        return;
      }

      // Check if we already processed this username recently
      if (username === this.lastProcessedUsername) {
        console.log('Username already processed, skipping');
        return;
      }

      console.log('Username detected:', username);
      this.callbacks.onUsernameDetected?.(username);

      // Lookup deck
      await this.lookupAndNotify(username);

      this.lastProcessedUsername = username;
    } catch (error) {
      console.error('Error processing screenshot:', error);
      this.callbacks.onError?.(`Error processing screenshot: ${error}`);
    }
  }

  /**
   * Lookup deck for a username
   */
  static async lookupDeck(username: string, clan?: string): Promise<PlayerDeck | null> {
    try {
      const deck = await DeckService.findDeckByUsername(username, clan || '');
      return deck;
    } catch (error) {
      console.error('Error looking up deck:', error);
      return null;
    }
  }

  /**
   * Lookup deck and notify callbacks
   */
  private static async lookupAndNotify(username: string, clan?: string): Promise<void> {
    try {
      const deck = await this.lookupDeck(username, clan);

      if (deck) {
        this.callbacks.onDeckFound?.(username, deck);
      } else {
        this.callbacks.onError?.(`No deck found for ${username}`);
      }
    } catch (error) {
      console.error('Error in lookupAndNotify:', error);
      this.callbacks.onError?.(`Error looking up deck: ${error}`);
    }
  }

  /**
   * Get tracking status
   */
  static getStatus() {
    return {
      isActive: this.isActive,
      lastProcessedUsername: this.lastProcessedUsername,
    };
  }

  /**
   * Manually process a screenshot
   */
  static async processScreenshot(uri: string): Promise<void> {
    const screenshot: ScreenshotData = {
      uri,
      timestamp: Date.now(),
      width: 0,
      height: 0,
    };

    await this.handleNewScreenshot(screenshot);
  }
}
