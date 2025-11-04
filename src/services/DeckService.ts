/**
 * Deck Service
 * Handles API calls to RoyaleAPI for deck lookup
 */

import axios from 'axios';

export interface Card {
  name: string;
  imageUrl: string;
}

export interface PlayerDeck {
  username: string;
  clan?: string;
  cards: Card[];
  cardUrls: string[];
}

export class DeckService {
  private static readonly BASE_URL = 'https://royaleapi.com';
  private static readonly TIMEOUT = 10000;

  /**
   * Find a player's deck by username
   */
  static async findDeckByUsername(
    username: string,
    clan: string = ''
  ): Promise<PlayerDeck | null> {
    try {
      console.log(`Looking up deck for: ${username}${clan ? ` (clan: ${clan})` : ''}`);

      // Format username for URL
      const formattedUsername = username.replace(/ /g, '+');

      // Search for player
      const searchUrl = `${this.BASE_URL}/player/search/results?q=${formattedUsername}`;

      const response = await axios.get(searchUrl, {
        timeout: this.TIMEOUT,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        },
      });

      if (response.status !== 200) {
        console.error('Search request failed:', response.status);
        return null;
      }

      // Parse HTML to find profile links
      const html = response.data;
      const profileLinks = this.extractProfileLinks(html);

      if (profileLinks.length === 0) {
        console.warn('No profiles found');
        return null;
      }

      console.log(`Found ${profileLinks.length} potential profiles`);

      // Check each profile
      for (const profileLink of profileLinks) {
        try {
          const deck = await this.fetchDeckFromProfile(profileLink, clan);

          if (deck) {
            console.log(`Found deck for ${username}`);
            return {
              username,
              clan,
              ...deck,
            };
          }
        } catch (error) {
          console.warn(`Error fetching profile ${profileLink}:`, error);
          continue;
        }
      }

      console.warn('No matching deck found');
      return null;
    } catch (error) {
      console.error('Error in findDeckByUsername:', error);
      return null;
    }
  }

  /**
   * Extract profile links from search results HTML
   */
  private static extractProfileLinks(html: string): string[] {
    try {
      // Simple regex to find profile links
      const regex = /href="(\/player\/[A-Z0-9]+)"/g;
      const links: string[] = [];
      let match;

      while ((match = regex.exec(html)) !== null) {
        if (!links.includes(match[1])) {
          links.push(match[1]);
        }
      }

      return links.slice(0, 10); // Limit to first 10 profiles
    } catch (error) {
      console.error('Error extracting profile links:', error);
      return [];
    }
  }

  /**
   * Fetch deck from a specific profile
   */
  private static async fetchDeckFromProfile(
    profilePath: string,
    clan: string
  ): Promise<{ cards: Card[]; cardUrls: string[] } | null> {
    try {
      const profileUrl = `${this.BASE_URL}${profilePath}`;

      const response = await axios.get(profileUrl, {
        timeout: this.TIMEOUT,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        },
      });

      const html = response.data;

      // If clan specified, check if it matches
      if (clan && !html.includes(clan)) {
        console.log('Clan not found in profile, skipping');
        return null;
      }

      // Extract card images
      const cardUrls = this.extractCardUrls(html);

      if (cardUrls.length === 0) {
        console.warn('No cards found in profile');
        return null;
      }

      const cards: Card[] = cardUrls.map(url => ({
        name: this.getCardNameFromUrl(url),
        imageUrl: url,
      }));

      return { cards, cardUrls };
    } catch (error) {
      console.error('Error fetching profile:', error);
      return null;
    }
  }

  /**
   * Extract card image URLs from profile HTML
   */
  private static extractCardUrls(html: string): string[] {
    try {
      // Look for deck_card class
      const regex = /<img[^>]+class="[^"]*deck_card[^"]*"[^>]+src="([^"]+)"/g;
      const urls: string[] = [];
      let match;

      while ((match = regex.exec(html)) !== null) {
        let url = match[1];

        // Remove query parameters
        url = url.split('?')[0];

        // Ensure it's a full URL
        if (url.startsWith('//')) {
          url = 'https:' + url;
        } else if (url.startsWith('/')) {
          url = this.BASE_URL + url;
        }

        if (!urls.includes(url)) {
          urls.push(url);
        }
      }

      return urls.slice(0, 8); // Deck has 8 cards
    } catch (error) {
      console.error('Error extracting card URLs:', error);
      return [];
    }
  }

  /**
   * Get card name from image URL
   */
  private static getCardNameFromUrl(url: string): string {
    try {
      const parts = url.split('/');
      const filename = parts[parts.length - 1];
      const name = filename.replace('.png', '').replace(/-/g, ' ');
      return name.charAt(0).toUpperCase() + name.slice(1);
    } catch (error) {
      return 'Unknown';
    }
  }

  /**
   * Download card image
   */
  static async downloadCardImage(url: string): Promise<string | null> {
    try {
      // Return URL directly - React Native Image component can load from URL
      return url;
    } catch (error) {
      console.error('Error downloading card image:', error);
      return null;
    }
  }
}
