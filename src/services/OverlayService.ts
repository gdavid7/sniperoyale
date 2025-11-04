/**
 * Overlay Service
 * Manages the floating overlay window (Android only)
 */

import { Platform, NativeModules } from 'react-native';

const { OverlayModule } = NativeModules;

export interface DeckData {
  username: string;
  cards: string[];
  clan?: string;
}

export class OverlayService {
  private static isVisible = false;
  private static currentDeck: DeckData | null = null;

  /**
   * Show the overlay window
   */
  static async showOverlay(): Promise<boolean> {
    if (Platform.OS !== 'android') {
      console.warn('Overlay only supported on Android');
      return false;
    }

    try {
      // Check if overlay permission is granted
      const hasPermission = await this.checkOverlayPermission();

      if (!hasPermission) {
        await this.requestOverlayPermission();
        return false;
      }

      // Show overlay through native module
      if (OverlayModule && OverlayModule.showOverlay) {
        await OverlayModule.showOverlay();
        this.isVisible = true;
        return true;
      } else {
        console.warn('OverlayModule not available');
        return false;
      }
    } catch (error) {
      console.error('Error showing overlay:', error);
      return false;
    }
  }

  /**
   * Hide the overlay window
   */
  static async hideOverlay(): Promise<void> {
    if (Platform.OS !== 'android') {
      return;
    }

    try {
      if (OverlayModule && OverlayModule.hideOverlay) {
        await OverlayModule.hideOverlay();
        this.isVisible = false;
      }
    } catch (error) {
      console.error('Error hiding overlay:', error);
    }
  }

  /**
   * Update the deck displayed in the overlay
   */
  static async updateDeck(deck: DeckData): Promise<void> {
    if (Platform.OS !== 'android') {
      return;
    }

    try {
      this.currentDeck = deck;

      if (OverlayModule && OverlayModule.updateDeck) {
        await OverlayModule.updateDeck(JSON.stringify(deck));
      }
    } catch (error) {
      console.error('Error updating overlay deck:', error);
    }
  }

  /**
   * Check if overlay permission is granted
   */
  static async checkOverlayPermission(): Promise<boolean> {
    if (Platform.OS !== 'android') {
      return false;
    }

    try {
      if (OverlayModule && OverlayModule.checkPermission) {
        return await OverlayModule.checkPermission();
      }
      return false;
    } catch (error) {
      console.error('Error checking overlay permission:', error);
      return false;
    }
  }

  /**
   * Request overlay permission
   */
  static async requestOverlayPermission(): Promise<void> {
    if (Platform.OS !== 'android') {
      return;
    }

    try {
      if (OverlayModule && OverlayModule.requestPermission) {
        await OverlayModule.requestPermission();
      }
    } catch (error) {
      console.error('Error requesting overlay permission:', error);
    }
  }

  /**
   * Get current overlay state
   */
  static getState() {
    return {
      isVisible: this.isVisible,
      currentDeck: this.currentDeck,
    };
  }
}
