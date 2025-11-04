"""
Deck Image Creation Module
Downloads card images and creates a composite deck image
"""

import requests
from PIL import Image
import logging
from typing import List, Optional
from io import BytesIO

logger = logging.getLogger(__name__)


def returnCard(link: str, timeout: int = 10) -> Optional[Image.Image]:
    """
    Downloads a card image from a URL

    Args:
        link: URL of the card image
        timeout: Request timeout in seconds

    Returns:
        PIL Image object, or None if failed
    """
    try:
        logger.debug(f"Downloading card from: {link}")

        response = requests.get(link, stream=True, timeout=timeout)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content))
        return img

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download card from {link}: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to open card image: {e}")
        return None


def create_image(cardList: List[str], save_path: Optional[str] = None) -> Optional[Image.Image]:
    """
    Creates a composite image from a list of card URLs

    Args:
        cardList: List of card image URLs
        save_path: Optional path to save the image

    Returns:
        PIL Image object of the composite deck, or None if failed
    """
    try:
        if not cardList:
            logger.warning("Empty card list provided")
            return None

        logger.info(f"Creating deck image from {len(cardList)} cards")

        # Download all card images
        card_images = []
        for i, url in enumerate(cardList):
            logger.debug(f"Downloading card {i+1}/{len(cardList)}")
            img = returnCard(url)

            if img is None:
                logger.warning(f"Skipping card {i+1} due to download failure")
                continue

            card_images.append(img)

        if not card_images:
            logger.error("Failed to download any card images")
            return None

        logger.info(f"Successfully downloaded {len(card_images)}/{len(cardList)} cards")

        # Calculate total width
        totalWidth = sum(card.width for card in card_images)
        maxHeight = max(card.height for card in card_images)

        # Create composite image
        dst = Image.new('RGB', (totalWidth, maxHeight))

        # Paste cards side by side
        x_offset = 0
        for i, card in enumerate(card_images):
            dst.paste(card, (x_offset, 0))
            x_offset += card.width
            logger.debug(f"Pasted card {i+1} at offset {x_offset}")

        # Save if path provided
        if save_path:
            try:
                dst.save(save_path)
                logger.info(f"Saved deck image to: {save_path}")
            except Exception as e:
                logger.error(f"Failed to save image: {e}")

        # Display the image
        try:
            dst.show()
        except Exception as e:
            logger.warning(f"Could not display image: {e}")

        return dst

    except Exception as e:
        logger.error(f"Error creating composite image: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    # Test the functions
    logging.basicConfig(level=logging.INFO)

    # Test with some example card URLs (these may or may not work)
    test_urls = [
        "https://cdn.royaleapi.com/static/img/cards/knight.png",
        "https://cdn.royaleapi.com/static/img/cards/archers.png",
        "https://cdn.royaleapi.com/static/img/cards/giant.png",
        "https://cdn.royaleapi.com/static/img/cards/goblin.png",
    ]

    print("Testing deck image creation...")
    result = create_image(test_urls, save_path="test_deck.png")

    if result:
        print("✓ Deck image created successfully!")
    else:
        print("✗ Failed to create deck image")

