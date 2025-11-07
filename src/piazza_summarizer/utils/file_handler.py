"""
File handling utilities for JSONL operations.
"""

import jsonlines
from pathlib import Path
from typing import List, Dict, Any, Generator
from datetime import datetime

from piazza_summarizer.utils.logger import get_logger

logger = get_logger(__name__)


class JSONLHandler:
    """Handler for reading and writing JSONL files."""

    @staticmethod
    def write(data: List[Dict[str, Any]], filepath: str, append: bool = False) -> None:
        """
        Write data to a JSONL file.

        Args:
            data: List of dictionaries to write
            filepath: Output file path
            append: If True, append to existing file; if False, overwrite
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        mode = 'a' if append else 'w'

        try:
            with jsonlines.open(filepath, mode=mode) as writer:
                for item in data:
                    writer.write(item)

            logger.info(f"Wrote {len(data)} records to {filepath}")
        except Exception as e:
            logger.error(f"Failed to write to {filepath}: {e}")
            raise

    @staticmethod
    def write_single(data: Dict[str, Any], filepath: str) -> None:
        """
        Append a single record to a JSONL file.

        Args:
            data: Dictionary to write
            filepath: Output file path
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            with jsonlines.open(filepath, mode='a') as writer:
                writer.write(data)

            logger.debug(f"Appended 1 record to {filepath}")
        except Exception as e:
            logger.error(f"Failed to append to {filepath}: {e}")
            raise

    @staticmethod
    def read(filepath: str) -> List[Dict[str, Any]]:
        """
        Read all records from a JSONL file.

        Args:
            filepath: Input file path

        Returns:
            List of dictionaries
        """
        filepath = Path(filepath)

        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return []

        try:
            with jsonlines.open(filepath) as reader:
                data = list(reader)

            logger.info(f"Read {len(data)} records from {filepath}")
            return data
        except Exception as e:
            logger.error(f"Failed to read from {filepath}: {e}")
            raise

    @staticmethod
    def read_iter(filepath: str) -> Generator[Dict[str, Any], None, None]:
        """
        Read records from a JSONL file one at a time (memory efficient).

        Args:
            filepath: Input file path

        Yields:
            Dictionary records one at a time
        """
        filepath = Path(filepath)

        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return

        try:
            with jsonlines.open(filepath) as reader:
                for item in reader:
                    yield item
        except Exception as e:
            logger.error(f"Failed to read from {filepath}: {e}")
            raise

    @staticmethod
    def get_metadata(filepath: str) -> Dict[str, Any]:
        """
        Get metadata about a JSONL file.

        Args:
            filepath: Input file path

        Returns:
            Dictionary with file metadata
        """
        filepath = Path(filepath)

        if not filepath.exists():
            return {"exists": False}

        record_count = sum(1 for _ in JSONLHandler.read_iter(str(filepath)))

        return {
            "exists": True,
            "path": str(filepath),
            "size_bytes": filepath.stat().st_size,
            "record_count": record_count,
            "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
        }