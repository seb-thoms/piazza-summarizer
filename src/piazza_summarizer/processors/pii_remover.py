"""
PII (Personally Identifiable Information) removal for Piazza posts.
Removes student and instructor names from post content.
"""

from typing import Dict, Any, List, Optional

from .name_detector import NameDetector
from .text_cleaner import clean_text
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PIIRemover:
    """
    Removes PII from structured Piazza posts.
    Cleans HTML entities and redacts names.
    """

    def __init__(self, all_users: List[Dict[str, Any]]):
        """
        Initialize PII remover with course roster.

        Args:
            all_users: List of all users (students + instructors) from course
        """
        self.name_detector = NameDetector(all_users)
        logger.info("PIIRemover initialized with name detection")

    def clean_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove PII from a structured post.

        Args:
            post: Structured post dictionary

        Returns:
            Post with PII removed
        """
        # Create a copy to avoid modifying original
        cleaned_post = post.copy()

        # Clean subject
        cleaned_post['subject'] = self._clean_field(post.get('subject', ''))

        # Clean main content
        cleaned_post['content'] = self._clean_field(post.get('content', ''))

        # Clean student answer
        if post.get('student_answer'):
            cleaned_post['student_answer'] = self._clean_answer(post['student_answer'])

        # Clean instructor answer
        if post.get('instructor_answer'):
            cleaned_post['instructor_answer'] = self._clean_answer(post['instructor_answer'])

        # Clean followups (with nested replies)
        if post.get('followups'):
            cleaned_post['followups'] = self._clean_followups(post['followups'])

        logger.debug(f"Cleaned post {post.get('post_id')}")

        return cleaned_post

    def _clean_field(self, text: Optional[str]) -> str:
        """
        Clean a single text field: decode HTML + redact names.

        Args:
            text: Raw text field

        Returns:
            Cleaned text with PII removed
        """
        if not text:
            return ""

        # First, clean HTML entities
        cleaned = clean_text(text)

        # Then, redact names
        redacted = self.name_detector.redact_names(cleaned)

        return redacted

    def _clean_answer(self, answer: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Clean an answer dictionary (student or instructor answer).

        Args:
            answer: Answer dictionary with 'content' field

        Returns:
            Cleaned answer dictionary
        """
        if not answer:
            return None

        cleaned_answer = answer.copy()
        cleaned_answer['content'] = self._clean_field(answer.get('content', ''))

        return cleaned_answer

    def _clean_followups(self, followups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean followup discussions including nested replies.

        Args:
            followups: List of followup dictionaries

        Returns:
            List of cleaned followups
        """
        cleaned_followups = []

        for followup in followups:
            cleaned_followup = followup.copy()

            # Clean followup content
            cleaned_followup['content'] = self._clean_field(followup.get('content', ''))

            # Clean nested replies
            if followup.get('replies'):
                cleaned_replies = []
                for reply in followup['replies']:
                    cleaned_reply = reply.copy()
                    cleaned_reply['content'] = self._clean_field(reply.get('content', ''))
                    cleaned_replies.append(cleaned_reply)

                cleaned_followup['replies'] = cleaned_replies

            cleaned_followups.append(cleaned_followup)

        return cleaned_followups

    def clean_posts_batch(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean multiple posts in batch.

        Args:
            posts: List of structured posts

        Returns:
            List of cleaned posts
        """
        logger.info(f"Cleaning PII from {len(posts)} posts")

        cleaned_posts = []
        for i, post in enumerate(posts, 1):
            try:
                cleaned = self.clean_post(post)
                cleaned_posts.append(cleaned)

                if i % 10 == 0:
                    logger.debug(f"Cleaned {i}/{len(posts)} posts")

            except Exception as e:
                logger.error(f"Failed to clean post {post.get('post_id')}: {e}")
                # Still include the post, even if cleaning failed
                cleaned_posts.append(post)

        logger.info(f"Successfully cleaned {len(cleaned_posts)} posts")
        return cleaned_posts