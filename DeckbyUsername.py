"""
Deck Lookup Module
Searches for a player by username and retrieves their deck from RoyaleAPI
"""

import cloudscraper
from bs4 import BeautifulSoup
import random
import time
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def findByUsername(username: str, clan: str = "") -> List[str]:
    """
    Finds a player's deck by searching for their username on RoyaleAPI

    Args:
        username: The player's Clash Royale username
        clan: Optional clan name to filter results

    Returns:
        List of card image URLs, or empty list if not found
    """
    try:
        # Input validation
        if not username or not isinstance(username, str):
            logger.error("Invalid username provided")
            return []

        username = username.strip()
        if not username:
            logger.error("Empty username after stripping")
            return []

        # Lists to store results
        profilelinks = []
        cardslist = []

        # Format username for URL (replace spaces with +)
        formatted_username = username.replace(" ", "+")

        logger.info(f"Searching for username: {username}" + (f" in clan: {clan}" if clan else ""))

        # Create scraper with random delay for anti-bot protection
        scraper = cloudscraper.create_scraper(delay=random.randint(10, 100))

        # Make the GET request with retry logic
        max_retries = 3
        retry_count = 0
        searchresults = None

        while retry_count < max_retries:
            try:
                search_url = f'https://royaleapi.com/player/search/results?q={formatted_username}'
                logger.debug(f"Requesting: {search_url}")

                searchresults = scraper.get(search_url, timeout=10)

                if searchresults.status_code == 200:
                    break
                else:
                    logger.warning(f"Got status code {searchresults.status_code}, retrying...")
                    retry_count += 1
                    time.sleep(1)

            except Exception as e:
                logger.warning(f"Request failed (attempt {retry_count + 1}): {e}")
                retry_count += 1
                time.sleep(1)

        if searchresults is None or searchresults.status_code != 200:
            logger.error(f"Failed to get search results after {max_retries} attempts")
            return []

        # Parse the HTML to find player profiles
        soup = BeautifulSoup(searchresults.text, "html.parser")
        myheaders = soup.find_all("a", {"class": "header"})

        # Skip first 2 headers (they are navigation elements)
        links = myheaders[2:] if len(myheaders) > 2 else []

        if not links:
            logger.warning(f"No profiles found for username: {username}")
            return []

        logger.info(f"Found {len(links)} potential profiles")

        # Extract profile links
        for link in links:
            href = link.get("href")
            if href:
                profilelinks.append(href)

        if not profilelinks:
            logger.warning("No valid profile links found")
            return []

        # Check each profile
        for i, profile in enumerate(profilelinks):
            try:
                profile_url = f"https://royaleapi.com{profile}"
                logger.debug(f"Checking profile {i+1}/{len(profilelinks)}: {profile_url}")

                getProfiles = scraper.get(profile_url, timeout=10).text

                # Parse the profile HTML
                profilesoup = BeautifulSoup(getProfiles, "html.parser")

                # If clan is specified, check if it matches
                if clan:
                    if profilesoup.find(text=clan) is None:
                        logger.debug(f"Clan '{clan}' not found in profile, skipping...")
                        continue
                    else:
                        logger.info(f"Found matching clan: {clan}")

                # Find the deck cards
                cards = profilesoup.find_all(class_="deck_card ui image")

                if not cards:
                    logger.debug("No cards found in this profile")
                    continue

                # Extract card image URLs
                for card in cards:
                    try:
                        src = card.get("src")
                        if src:
                            # Remove query parameters
                            clean_url = src.split('?')[0]
                            cardslist.append(clean_url)
                    except Exception as e:
                        logger.warning(f"Error extracting card URL: {e}")
                        continue

                if cardslist:
                    logger.info(f"Successfully found {len(cardslist)} cards for {username}")
                    return cardslist

            except Exception as e:
                logger.error(f"Error processing profile {profile}: {e}")
                continue

        # No matching profile found
        logger.warning(f"No deck found for username: {username}" + (f" with clan: {clan}" if clan else ""))
        return []

    except Exception as e:
        logger.error(f"Unexpected error in findByUsername: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    # Test the function
    logging.basicConfig(level=logging.INFO)

    test_username = input("Enter username to search: ")
    test_clan = input("Enter clan (optional, press Enter to skip): ")

    result = findByUsername(test_username, test_clan)

    if result:
        print(f"\n✓ Found {len(result)} cards:")
        for url in result:
            print(f"  - {url}")
    else:
        print("\n✗ No cards found")
