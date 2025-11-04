/**
 * OCR Service
 * Handles text recognition from screenshots
 */

import TesseractOcr, { LANG_ENGLISH } from 'react-native-tesseract-ocr';
import { Image } from 'react-native';

export interface UsernameRegion {
  name: string;
  x: number; // percentage
  y: number; // percentage
  width: number; // percentage
  height: number; // percentage
}

export class OCRService {
  // Username detection regions (same as desktop version)
  private static USERNAME_REGIONS: UsernameRegion[] = [
    { name: 'opponent_top', x: 0.25, y: 0.02, width: 0.5, height: 0.08 },
    { name: 'player_topleft', x: 0.05, y: 0.05, width: 0.3, height: 0.08 },
    { name: 'player_topright', x: 0.65, y: 0.05, width: 0.3, height: 0.08 },
    { name: 'battle_start', x: 0.2, y: 0.35, width: 0.6, height: 0.15 },
  ];

  /**
   * Extract username from a screenshot
   */
  static async extractUsername(imageUri: string): Promise<string | null> {
    try {
      console.log('Extracting username from:', imageUri);

      // Try full image first for faster detection
      const fullText = await this.performOCR(imageUri);
      const username = this.cleanUsername(fullText);

      if (this.isValidUsername(username)) {
        console.log('Username detected from full image:', username);
        return username;
      }

      // Try specific regions
      for (const region of this.USERNAME_REGIONS) {
        try {
          const regionText = await this.performOCROnRegion(imageUri, region);
          const cleanedUsername = this.cleanUsername(regionText);

          if (this.isValidUsername(cleanedUsername)) {
            console.log(`Username detected from ${region.name}:`, cleanedUsername);
            return cleanedUsername;
          }
        } catch (error) {
          console.warn(`Error processing region ${region.name}:`, error);
          continue;
        }
      }

      console.warn('No valid username found');
      return null;
    } catch (error) {
      console.error('Error extracting username:', error);
      return null;
    }
  }

  /**
   * Perform OCR on full image
   */
  private static async performOCR(imageUri: string): Promise<string> {
    try {
      const text = await TesseractOcr.recognize(imageUri, LANG_ENGLISH, {
        whitelist: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-',
        blacklist: '!@#$%^&*()+=[]{}|;:,.<>?/~`\'"\\',
      });

      return text || '';
    } catch (error) {
      console.error('OCR error:', error);
      return '';
    }
  }

  /**
   * Perform OCR on a specific region of the image
   */
  private static async performOCROnRegion(
    imageUri: string,
    region: UsernameRegion
  ): Promise<string> {
    try {
      // Get image dimensions
      const { width, height } = await this.getImageDimensions(imageUri);

      // Calculate region coordinates
      const x = Math.floor(region.x * width);
      const y = Math.floor(region.y * height);
      const w = Math.floor(region.width * width);
      const h = Math.floor(region.height * height);

      // Perform OCR with region specification
      const text = await TesseractOcr.recognize(imageUri, LANG_ENGLISH, {
        whitelist: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-',
        blacklist: '!@#$%^&*()+=[]{}|;:,.<>?/~`\'"\\',
      });

      return text || '';
    } catch (error) {
      console.error('Region OCR error:', error);
      return '';
    }
  }

  /**
   * Get image dimensions
   */
  private static getImageDimensions(uri: string): Promise<{ width: number; height: number }> {
    return new Promise((resolve, reject) => {
      Image.getSize(
        uri,
        (width, height) => {
          resolve({ width, height });
        },
        error => {
          reject(error);
        }
      );
    });
  }

  /**
   * Clean OCR output to get valid username
   */
  private static cleanUsername(text: string): string {
    // Remove whitespace
    let cleaned = text.trim();

    // Remove special characters except underscore and hyphen
    cleaned = cleaned.replace(/[^a-zA-Z0-9_-]/g, '');

    // Split by newlines and take first non-empty line
    const lines = cleaned.split('\n').filter(line => line.length > 0);
    if (lines.length > 0) {
      cleaned = lines[0];
    }

    return cleaned;
  }

  /**
   * Validate if string is a valid Clash Royale username
   */
  private static isValidUsername(username: string): boolean {
    if (!username || username.length < 3 || username.length > 15) {
      return false;
    }

    // Must contain at least one alphanumeric character
    return /[a-zA-Z0-9]/.test(username);
  }

  /**
   * Detect if image shows battle start screen
   */
  static async isBattleStartScreen(imageUri: string): Promise<boolean> {
    try {
      // Simple heuristic: check if we can find a username in typical positions
      const username = await this.extractUsername(imageUri);
      return username !== null;
    } catch (error) {
      console.error('Error detecting battle start screen:', error);
      return false;
    }
  }
}
