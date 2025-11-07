"""
Piazza Summarizer - A tool for scraping and summarizing Piazza discussions.
"""

__version__ = "0.1.0"
__author__ = "Sebastian"

from .scrapers.piazza_scraper import PiazzaScraper
from .utils.logger import setup_logger, get_logger
from .utils.file_handler import JSONLHandler

__all__ = [
    "PiazzaScraper",
    "setup_logger",
    "get_logger",
    "JSONLHandler",
]