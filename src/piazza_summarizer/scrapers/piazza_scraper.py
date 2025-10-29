"""
Piazza scraper module for collecting discussion posts.
Uses the unofficial piazza-api library.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from datetime import UTC
import time

from piazza_api import Piazza
from piazza_api.exceptions import RequestError, AuthenticationError

from src.piazza_summarizer.utils.logger import get_logger
from src.piazza_summarizer.utils.file_handler import JSONLHandler

logger = get_logger(__name__)


class PiazzaScraper:
    """
    Scraper for Piazza discussion posts.

    Uses the unofficial piazza-api to authenticate and retrieve posts
    from a specific course network.
    """

    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the Piazza scraper.

        Args:
            email: Piazza account email (instructor account)
            password: Piazza account password
        """
        self.email = email
        self.password = password
        self.piazza = Piazza()
        self.network = None
        self._authenticated = False

        logger.info("PiazzaScraper initialized")

    def login(self, email: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Authenticate with Piazza.

        Args:
            email: Piazza account email (overrides __init__ email)
            password: Piazza account password (overrides __init__ password)

        Returns:
            True if authentication successful

        Raises:
            AuthenticationError: If login fails
        """
        email = email or self.email
        password = password or self.password

        if not email or not password:
            raise ValueError("Email and password are required for authentication")

        try:
            logger.info(f"Attempting to authenticate as {email}")
            self.piazza.user_login(email=email, password=password)
            self._authenticated = True
            logger.info("Authentication successful")
            return True
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise

    def get_user_courses(self) -> List[Dict[str, Any]]:
        """
        Get list of courses the authenticated user has access to.

        Returns:
            List of course dictionaries with name and network ID

        Raises:
            RuntimeError: If not authenticated
        """
        if not self._authenticated:
            raise RuntimeError("Must authenticate before getting courses")

        try:
            logger.info("Fetching user courses")
            user_profile = self.piazza.get_user_profile()
            courses = user_profile.get('all_classes', [])

            logger.info(f"Found {len(courses)} courses")
            return [
                {
                    "name": course.get('name', 'Unknown'),
                    "network_id": course.get('nid'),
                    "term": course.get('term', 'Unknown'),
                    "status": course.get('status', 'Unknown')
                }
                for course in courses
            ]
        except Exception as e:
            logger.error(f"Failed to get user courses: {e}")
            raise

    def connect_to_course(self, network_id: str) -> None:
        """
        Connect to a specific Piazza course network.

        Args:
            network_id: The course network ID (found in Piazza URL)

        Raises:
            RuntimeError: If not authenticated
        """
        if not self._authenticated:
            raise RuntimeError("Must authenticate before connecting to course")

        try:
            logger.info(f"Connecting to course network: {network_id}")
            self.network = self.piazza.network(network_id)
            logger.info("Successfully connected to course")
        except Exception as e:
            logger.error(f"Failed to connect to course {network_id}: {e}")
            raise

    def get_all_posts(
            self,
            limit: Optional[int] = None,
            sleep: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all posts from the connected course.

        Args:
            limit: Maximum number of posts to retrieve (None for all)
            sleep: To get around fetching all posts without getting banned by Piazza

        Returns:
            List of post dictionaries with structured data

        Raises:
            RuntimeError: If not connected to a course
        """
        if not self.network:
            raise RuntimeError("Must connect to a course before fetching posts")

        try:
            logger.info(f"Fetching posts (limit={limit}, sleep={sleep})")

            posts = []
            for post_meta in self.network.iter_all_posts(limit=limit, sleep=sleep):
                try:
                    # Get full post details
                    post_id = post_meta.get('id') or post_meta.get('nr')

                    if not post_id:
                        logger.warning(f"Skipping post with no ID: {post_meta}")
                        continue

                    logger.debug(f"Fetching details for post {post_id}")
                    full_post = self.network.get_post(post_id)

                    # Structure the post data
                    structured_post = self._structure_post(full_post)
                    posts.append(structured_post)

                    # Being extra cautious with Piazza
                    time.sleep(0.1)

                except Exception as e:
                    logger.error(f"Failed to fetch post {post_id}: {e}")
                    continue

            logger.info(f"Successfully retrieved {len(posts)} posts")
            return posts

        except RequestError as e:
            logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching posts: {e}")
            raise

    def get_post_by_id(self, post_id: str) -> Dict[str, Any]:
        """
        Retrieve a single post by its ID.

        Args:
            post_id: The post ID or number

        Returns:
            Structured post dictionary
        """
        if not self.network:
            raise RuntimeError("Must connect to a course before fetching posts")

        try:
            logger.info(f"Fetching post {post_id}")
            full_post = self.network.get_post(post_id)
            return self._structure_post(full_post)
        except Exception as e:
            logger.error(f"Failed to fetch post {post_id}: {e}")
            raise

    def _structure_post(self, raw_post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw Piazza API response to structured format.

        Args:
            raw_post: Raw post data from Piazza API

        Returns:
            Structured post dictionary
        """
        # Extract main post content
        history = raw_post.get('history', [])
        current_content = history[-1] if history else {}

        # Extract answers and followups
        children = raw_post.get('children', [])
        student_answer = self._extract_answer(children, 's_answer')
        instructor_answer = self._extract_answer(children, 'i_answer')
        followups = self._extract_followups_with_replies(children)

        structured = {
            "post_id": raw_post.get('id') or raw_post.get('nr'),
            "post_number": raw_post.get('nr'),
            "type": raw_post.get('type'),
            "created": raw_post.get('created'),
            "updated": raw_post.get('updated'),
            "subject": current_content.get('subject', ''),
            "content": current_content.get('content', ''),
            "folders": raw_post.get('folders', []),
            "tags": raw_post.get('tags', []),
            "num_favorites": raw_post.get('num_favorites', 0),
            "unique_views": raw_post.get('unique_views', 0),
            "student_answer": student_answer,
            "instructor_answer": instructor_answer,
            "followups": followups,
            "scraped_at": datetime.now(UTC).isoformat()
        }

        return structured

    def _extract_answer(
        self,
        children: List[Dict[str, Any]],
        answer_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract student or instructor answer from children.

        Args:
            children: List of child elements
            answer_type: Either 's_answer' or 'i_answer'

        Returns:
            Answer dictionary with content and metadata, or None
        """
        for child in children:
            if child.get('type') == answer_type:
                history = child.get('history', [])
                current = history[-1] if history else {}

                answer = {
                    "id": child.get('id'),
                    "content": current.get('content', ''),
                    "created": child.get('created'),
                    "updated": child.get('updated'),
                }

                # Add endorsement info if available
                if child.get('tag_endorse_arr'):
                    answer["endorsed_by"] = child.get('tag_endorse_arr', [])

                return answer

        return None

    def _extract_followups_with_replies(self, children: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract followup discussions with nested replies from children.

        Args:
            children: List of child elements from post

        Returns:
            List of followup dictionaries with nested replies
        """
        followups = []

        for child in children:
            if child.get('type') == 'followup':
                # Extract followup content
                followup_data = {
                    "id": child.get('id'),
                    "content": child.get('subject', ''),
                    "created": child.get('created'),
                    "updated": child.get('updated'),
                    "author_type": self._determine_author_type(child),
                    "replies": []
                }

                # Extract nested replies (feedback, etc.)
                followup_children = child.get('children', [])
                for reply in followup_children:
                    reply_type = reply.get('type')
                    if reply_type in ['feedback', 'followup']:  # Can have nested followups too
                        reply_data = {
                            "id": reply.get('id'),
                            "type": reply_type,
                            "content": reply.get('subject', ''),
                            "created": reply.get('created'),
                            "updated": reply.get('updated'),
                            "author_type": self._determine_author_type(reply)
                        }
                        followup_data["replies"].append(reply_data)

                followups.append(followup_data)

        return followups

    def _determine_author_type(self, item: Dict[str, Any]) -> str:
        """
        Determine if author is student or instructor based on available data.

        Args:
            item: Post/followup/reply item

        Returns:
            'instructor', 'student', or 'unknown'
        """
        # Check if there's tag_endorse (instructors can endorse)
        if item.get('tag_endorse') or item.get('tag_endorse_arr'):
            return 'instructor'

        # Check uid patterns or other indicators
        # Note: This is a heuristic and may need refinement
        uid = item.get('uid', '')

        # Instructors often have different uid patterns
        # This may need adjustment based on your course
        if uid.startswith('lm'):  # Example pattern observed
            return 'instructor'

        # Check anon field
        anon = item.get('anon', 'no')
        if anon == 'stud':
            return 'student'

        return 'student'  # Default assumption

    def save_to_jsonl(
        self,
        posts: List[Dict[str, Any]],
        filepath: str,
        append: bool = False
    ) -> None:
        """
        Save posts to a JSONL file.

        Args:
            posts: List of structured posts
            filepath: Output file path
            append: If True, append to existing file
        """
        logger.info(f"Saving {len(posts)} posts to {filepath}")
        JSONLHandler.write(posts, filepath, append=append)
        logger.info("Save complete")

    def scrape_and_save(
        self,
        network_id: str,
        output_file: str,
        limit: Optional[int] = None
    ) -> int:
        """
        Complete workflow: connect, scrape, and save.

        Args:
            network_id: Course network ID
            output_file: Output JSONL file path
            limit: Maximum posts to retrieve

        Returns:
            Number of posts saved
        """
        self.connect_to_course(network_id)
        posts = self.get_all_posts(limit=limit)
        self.save_to_jsonl(posts, output_file)
        return len(posts)