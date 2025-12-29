#!/usr/bin/env python3
"""
Test script for PII removal functionality.
Tests name detection and redaction.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from piazza_summarizer.processors.pii_remover import PIIRemover
from piazza_summarizer.processors.name_detector import NameDetector
from piazza_summarizer.processors.text_cleaner import clean_text


def test_text_cleaner():
    """Test HTML entity cleaning."""
    print("=" * 60)
    print("Testing Text Cleaner")
    print("=" * 60)

    test_cases = [
        "I&#39;m confused about this",
        "The &lt;template&gt; tag",
        "Smith &amp; Jones (2020)",
        "Use &quot;quotes&quot; here"
    ]

    for text in test_cases:
        cleaned = clean_text(text)
        print(f"Original: {text}")
        print(f"Cleaned:  {cleaned}")
        print()


def test_name_detector():
    """Test name detection with sample roster."""
    print("=" * 60)
    print("Testing Name Detector")
    print("=" * 60)

    # Sample roster
    sample_users = [
        {'name': 'Sarah Johnson', 'role': 'student'},
        {'name': 'John Smith', 'role': 'student'},
        {'name': 'Michael Lee', 'role': 'ta'},
        {'name': 'Prof. Grace Kim', 'role': 'instructor'},
    ]

    detector = NameDetector(sample_users)

    test_texts = [
        "I worked with Sarah on this assignment.",
        "John mentioned this in class.",
        "Will you help me with this?",  # Should NOT match
        "I hope this works correctly.",  # Should NOT match
        "Prof. Kim explained it well.",
        "sarah and john collaborated on the project.",  # Lowercase
    ]

    for text in test_texts:
        names = detector.find_names_in_text(text)
        redacted = detector.redact_names(text)
        print(f"Original:  {text}")
        print(f"Found:     {names}")
        print(f"Redacted:  {redacted}")
        print()


def test_pii_remover():
    """Test full PII removal on structured post."""
    print("=" * 60)
    print("Testing PIIRemover")
    print("=" * 60)

    # Sample roster
    sample_users = [
        {'name': 'Sarah Johnson', 'role': 'student'},
        {'name': 'John Smith', 'role': 'student'},
        {'name': 'Prof. Kim', 'role': 'instructor'},
    ]

    # Sample post structure
    sample_post = {
        'post_id': 'test123',
        'subject': 'Question about Lab 7',
        'content': "I&#39;m working with Sarah on this. Will you help?",
        'instructor_answer': {
            'content': 'John asked about this earlier. Here&#39;s the answer.'
        },
        'followups': [
            {
                'content': 'Thanks! Sarah and I figured it out.',
                'replies': [
                    {
                        'content': 'Great! Prof. Kim will be happy to hear that.'
                    }
                ]
            }
        ]
    }

    remover = PIIRemover(sample_users)
    cleaned = remover.clean_post(sample_post)

    print("ORIGINAL POST:")
    print(f"Subject: {sample_post['subject']}")
    print(f"Content: {sample_post['content']}")
    print(f"Answer:  {sample_post['instructor_answer']['content']}")
    print(f"Followup: {sample_post['followups'][0]['content']}")
    print(f"Reply:   {sample_post['followups'][0]['replies'][0]['content']}")
    print()

    print("CLEANED POST:")
    print(f"Subject: {cleaned['subject']}")
    print(f"Content: {cleaned['content']}")
    print(f"Answer:  {cleaned['instructor_answer']['content']}")
    print(f"Followup: {cleaned['followups'][0]['content']}")
    print(f"Reply:   {cleaned['followups'][0]['replies'][0]['content']}")
    print()


if __name__ == "__main__":
    print("\n")
    print("*" * 60)
    print("PII REMOVAL TEST SUITE")
    print("*" * 60)
    print("\n")

    try:
        test_text_cleaner()
        test_name_detector()
        test_pii_remover()

        print("=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()