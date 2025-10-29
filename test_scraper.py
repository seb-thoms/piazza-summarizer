#!/usr/bin/env python3
"""
Quick test script for Piazza scraper.
Run this to test the scraper with your credentials.
"""

import os
import sys
from dotenv import load_dotenv

from src.piazza_summarizer.scrapers.piazza_scraper import PiazzaScraper
from src.piazza_summarizer.utils.logger import setup_logger
from src.piazza_summarizer.utils.file_handler import JSONLHandler


def main():
    """Test the Piazza scraper."""

    # Load environment variables
    load_dotenv("config/.env")

    # Setup logging
    logger = setup_logger(level="INFO", log_file="logs/test_scraper.log")

    logger.info("=" * 60)
    logger.info("Starting Piazza Scraper Test")
    logger.info("=" * 60)

    # Get credentials from environment
    email = os.getenv("PIAZZA_EMAIL")
    password = os.getenv("PIAZZA_PASSWORD")
    network_id = os.getenv("PIAZZA_NETWORK_ID")

    if not all([email, password, network_id]):
        logger.error(
            "Missing credentials! Please set PIAZZA_EMAIL, PIAZZA_PASSWORD, and PIAZZA_NETWORK_ID in config/.env")
        sys.exit(1)

    try:
        # Initialize scraper
        logger.info("Initializing scraper...")
        scraper = PiazzaScraper(email=email, password=password)

        # Login
        logger.info("Logging in...")
        scraper.login()

        # Connect to course
        logger.info(f"Connecting to course: {network_id}")
        scraper.connect_to_course(network_id)

        # Fetch a limited number of posts for testing
        logger.info("Fetching first 100 posts for testing...")
        posts = scraper.get_all_posts(limit=100, sleep=3)

        # Display summary
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Successfully retrieved {len(posts)} posts")
        logger.info(f"{'=' * 60}\n")

        if posts:
            # Show first post details
            first_post = posts[0]
            logger.info("First post preview:")
            logger.info(f"  Post ID: {first_post['post_id']}")
            logger.info(f"  Subject: {first_post['subject'][:80]}...")
            logger.info(f"  Created: {first_post['created']}")
            logger.info(f"  Has student answer: {first_post['student_answer'] is not None}")
            logger.info(f"  Has instructor answer: {first_post['instructor_answer'] is not None}")
            logger.info(f"  Followups: {len(first_post['followups'])}")

        # Save to file
        output_file = "data/raw/test_posts.jsonl"
        logger.info(f"\nSaving to {output_file}...")
        scraper.save_to_jsonl(posts, output_file)

        # Verify saved file
        metadata = JSONLHandler.get_metadata(output_file)
        logger.info(f"\nFile saved successfully!")
        logger.info(f"  Path: {metadata['path']}")
        logger.info(f"  Records: {metadata['record_count']}")
        logger.info(f"  Size: {metadata['size_bytes']} bytes")

        logger.info("\nTest completed successfully!")

    except Exception as e:
        logger.error(f"\n✗ Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()