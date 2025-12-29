"""
Name detection using NER (Named Entity Recognition) and course roster.
Identifies person names in text and cross-references with course participants.
"""

import spacy
from typing import List, Set, Optional, Dict, Any
import re

from ..utils.logger import get_logger

logger = get_logger(__name__)


class NameDetector:
    """
    Detects person names in text using NER and validates against course roster.
    """

    def __init__(self, all_users: List[Dict[str, Any]]):
        """
        Initialize name detector with course roster.

        Args:
            all_users: List of user dictionaries from Piazza
                Each dict should have: {'name': str, 'role': str, ...}
        """
        # Load spaCy NER model
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy NER model successfully")
        except OSError:
            logger.error(
                "spaCy model not found. Please run: "
                "python -m spacy download en_core_web_sm"
            )
            raise

        # Extract names from roster
        self.roster_names = self._extract_roster_names(all_users)
        logger.info(f"Loaded {len(self.roster_names)} names from course roster")

    def _extract_roster_names(self, users: List[Dict[str, Any]]) -> Set[str]:
        """
        Extract all name variations from user list.

        Args:
            users: List of user dictionaries

        Returns:
            Set of names (first names, last names, full names) - all lowercase
        """
        names = set()

        for user in users:
            full_name = user.get('name', '').strip()

            if not full_name:
                continue

            # Add full name (lowercase for case-insensitive matching)
            names.add(full_name.lower())

            # Split into parts and add each
            name_parts = full_name.split()
            for part in name_parts:
                if len(part) > 1:  # Skip single letters
                    names.add(part.lower())

        return names

    def find_names_in_text(self, text: Optional[str]) -> List[str]:
        """
        Find all person names in text that match course roster.

        Uses NER to identify potential names, then validates against roster.

        Args:
            text: Text to search for names

        Returns:
            List of unique names found (as they appear in text, with original case)
        """
        if not text:
            return []

        found_names = []

        try:
            # Use NER to find PERSON entities
            doc = self.nlp(text)

            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text.strip()

                    # Check if this name (or any part) is in roster
                    if self._is_roster_name(name):
                        found_names.append(name)
                        logger.debug(f"Found roster name in text: '{name}'")

        except Exception as e:
            logger.error(f"Error in NER processing: {e}")

        # Return unique names while preserving original case
        return list(set(found_names))

    def _is_roster_name(self, name: str) -> bool:
        """
        Check if a name (or any part of it) exists in course roster.
        Case-insensitive comparison.

        Args:
            name: Name to check (e.g., "John Smith", "John", "Smith")

        Returns:
            True if name or any part is in roster
        """
        name_lower = name.lower()

        # Check full name
        if name_lower in self.roster_names:
            return True

        # Check individual parts
        parts = name_lower.split()
        for part in parts:
            if part in self.roster_names:
                return True

        return False

    def redact_names(self, text: Optional[str], placeholder: str = "[NAME]") -> str:
        """
        Replace all detected names with placeholder.

        Args:
            text: Text containing names
            placeholder: Replacement string (default: "[NAME]")

        Returns:
            Text with names replaced
        """
        if not text:
            return ""

        # Find all names
        names_to_redact = self.find_names_in_text(text)

        if not names_to_redact:
            return text

        # Sort by length (longest first) to avoid partial replacements
        # e.g., replace "John Smith" before "John"
        names_to_redact.sort(key=len, reverse=True)

        redacted_text = text

        for name in names_to_redact:
            # Use word boundaries and case-insensitive replacement
            pattern = re.compile(re.escape(name), re.IGNORECASE)
            redacted_text = pattern.sub(placeholder, redacted_text)
            logger.debug(f"Redacted name: '{name}' → '{placeholder}'")

        return redacted_text