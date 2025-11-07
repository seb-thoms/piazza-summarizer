"""
File detection utilities for finding and reading existing course JSONL files.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from piazza_summarizer.utils.file_handler import JSONLHandler

# Data directory path
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "courses"


def detect_existing_courses() -> Dict[str, Dict[str, Any]]:
    """
    Detect all existing course JSONL files in the data directory.

    Returns:
        Dictionary mapping filename to course metadata
        Example: {
            'CS5010_fall2025.jsonl': {
                'filepath': Path(...),
                'display_name': 'CS5010 Fall 2025',
                'last_scraped': datetime(...),
                'last_scraped_display': 'Nov 6, 2025 at 2:30 PM',
                'total_posts': 120,
                'public_posts': 105,
                'private_posts': 15,
                'available_folders': ['labs', 'homework', ...]
            }
        }
    """
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    courses = {}

    # Find all JSONL files
    for jsonl_file in DATA_DIR.glob("*.jsonl"):
        try:
            metadata = get_course_metadata(jsonl_file)
            if metadata:
                courses[jsonl_file.name] = metadata
        except Exception as e:
            print(f"Error reading {jsonl_file}: {e}")
            continue

    return courses


def get_course_metadata(filepath: Path) -> Optional[Dict[str, Any]]:
    """
    Extract metadata from a course JSONL file.

    Args:
        filepath: Path to the JSONL file

    Returns:
        Dictionary with course metadata, or None if file is invalid
    """
    if not filepath.exists():
        return None

    try:
        # Get file modification time
        mod_time = datetime.fromtimestamp(filepath.stat().st_mtime)

        # Read all posts to gather statistics
        posts = JSONLHandler.read(str(filepath))

        if not posts:
            return None

        # Count public vs private posts
        public_posts = sum(1 for p in posts if p.get('is_public', True))
        private_posts = len(posts) - public_posts

        # Extract unique folders (assignments)
        folders = set()
        for post in posts:
            folders.update(post.get('folders', []))

        # Generate display name from filename
        # Format: CourseName_term.jsonl -> "CourseName Term"
        display_name = generate_display_name(filepath.stem)

        return {
            'filepath': filepath,
            'display_name': display_name,
            'last_scraped': mod_time,
            'last_scraped_display': format_datetime(mod_time),
            'total_posts': len(posts),
            'public_posts': public_posts,
            'private_posts': private_posts,
            'available_folders': sorted(list(folders))
        }

    except Exception as e:
        print(f"Error extracting metadata from {filepath}: {e}")
        return None


def generate_display_name(stem: str) -> str:
    """
    Generate a display-friendly course name from filename stem.

    Args:
        stem: Filename without extension (e.g., 'CS5010_fall2025')

    Returns:
        Display name (e.g., 'CS5010 Fall 2025')
    """
    parts = stem.split('_')

    if len(parts) >= 2:
        course_code = parts[0]
        term = parts[1].capitalize() if len(parts) > 1 else ''
        year = parts[2] if len(parts) > 2 else ''

        return f"{course_code} {term} {year}".strip()

    return stem


def format_datetime(dt: datetime) -> str:
    """
    Format datetime for display.

    Args:
        dt: Datetime object

    Returns:
        Formatted string (e.g., 'Nov 6, 2025 at 2:30 PM')
    """
    return dt.strftime("%b %d, %Y at %I:%M %p")


def get_course_posts(course_file: str) -> list:
    """
    Load all posts from a course JSONL file.

    Args:
        course_file: Filename of the course JSONL

    Returns:
        List of post dictionaries
    """
    filepath = DATA_DIR / course_file

    if not filepath.exists():
        raise FileNotFoundError(f"Course file not found: {course_file}")

    return JSONLHandler.read(str(filepath))


def get_course_filepath(course_file: str) -> Path:
    """
    Get the full path for a course file.

    Args:
        course_file: Filename of the course

    Returns:
        Full path to the course JSONL file
    """
    return DATA_DIR / course_file


def course_exists(course_file: str) -> bool:
    """
    Check if a course file exists.

    Args:
        course_file: Filename to check

    Returns:
        True if file exists, False otherwise
    """
    return (DATA_DIR / course_file).exists()