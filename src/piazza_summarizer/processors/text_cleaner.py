"""
Text cleaning utilities for processing Piazza post content.
Handles HTML entity decoding and text normalization.
"""

import html
import re
from typing import Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


def clean_html_entities(text: Optional[str]) -> str:
    """
    Convert HTML entities to their corresponding characters.

    Examples:
        &#39; → '
        &lt; → <
        &gt; → >
        &amp; → &
        &quot; → "

    Args:
        text: Text containing HTML entities

    Returns:
        Text with entities decoded
    """
    if not text:
        return ""

    try:
        # Decode HTML entities
        decoded = html.unescape(text)
        return decoded
    except Exception as e:
        logger.warning(f"Failed to decode HTML entities: {e}")
        return text


def clean_extra_whitespace(text: Optional[str]) -> str:
    """
    Clean up excessive whitespace in text.

    Args:
        text: Text with potential extra whitespace

    Returns:
        Text with normalized whitespace
    """
    if not text:
        return ""

    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)

    # Replace multiple newlines with double newline
    text = re.sub(r'\n\n+', '\n\n', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def clean_text(text: Optional[str]) -> str:
    """
    Apply all text cleaning operations.

    Args:
        text: Raw text from Piazza

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Decode HTML entities
    text = clean_html_entities(text)

    # Clean whitespace
    text = clean_extra_whitespace(text)

    return text