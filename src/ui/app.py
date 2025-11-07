"""
Piazza Insight Analyzer - Landing Page
Main entry point for the Streamlit application.
"""

import streamlit as st
from pathlib import Path
import sys

# Page configuration - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Piazza Insight Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ui.utils.file_detection import detect_existing_courses, get_course_metadata


def main():
    """Main landing page for Piazza Insight Analyzer."""

    # Header
    st.title("📊 Piazza Insight Analyzer")
    st.markdown("### Understand student discussions and improve your assignments")
    st.markdown("---")

    # Detect existing courses
    existing_courses = detect_existing_courses()

    if existing_courses:
        display_existing_courses(existing_courses)
    else:
        display_no_courses_message()

    # Always show option to scrape new course
    st.markdown("---")
    display_new_course_option()


def display_existing_courses(courses):
    """Display list of existing course data with metadata."""

    st.subheader("📁 Existing Course Data")
    st.markdown("Select a course to analyze or re-scrape to update the data.")

    # Create columns for better layout
    for course_file, metadata in courses.items():
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"**{metadata['display_name']}**")
                st.caption(
                    f"📅 Last scraped: {metadata['last_scraped_display']}\n\n"
                    f"📊 {metadata['total_posts']} posts "
                    f"({metadata['public_posts']} public)"
                )

            with col2:
                if st.button("📖 Use This Data", key=f"use_{course_file}"):
                    # Store selected course in session state
                    st.session_state['selected_course'] = course_file
                    st.session_state['course_metadata'] = metadata
                    # Navigate to analysis page
                    st.switch_page("pages/analyze.py")

            with col3:
                if st.button("🔄 Re-scrape", key=f"rescrape_{course_file}"):
                    # Store course to re-scrape
                    st.session_state['rescrape_course'] = course_file
                    st.session_state['course_metadata'] = metadata
                    # Navigate to scrape page
                    st.switch_page("pages/scrape.py")

            st.markdown("---")


def display_no_courses_message():
    """Display message when no courses are found."""

    st.info(
        "👋 **Welcome!** No course data found yet.\n\n"
        "Get started by scraping your first Piazza course below."
    )


def display_new_course_option():
    """Display button to scrape a new course."""

    st.subheader("➕ Scrape New Course")
    st.markdown(
        "Connect to a Piazza course to download and analyze discussion posts."
    )

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        if st.button("🚀 Scrape New Course", type="primary", use_container_width=True):
            # Clear any previous scrape state
            if 'rescrape_course' in st.session_state:
                del st.session_state['rescrape_course']
            # Navigate to scrape page
            st.switch_page("pages/scrape.py")


def display_sidebar():
    """Display sidebar with information and settings."""

    with st.sidebar:
        st.markdown("### ℹ️ About")
        st.markdown(
            "This tool analyzes Piazza discussion posts to help faculty:\n"
            "- Identify common student confusions\n"
            "- Generate FAQs from discussions\n"
            "- Improve assignment clarity\n"
            "- Track discussion patterns"
        )

        st.markdown("---")

        st.markdown("### 🔒 Privacy")
        st.markdown(
            "- Credentials are never stored\n"
            "- Only public posts are analyzed\n"
            "- Data stays on your local machine\n"
        )

        st.markdown("---")

if __name__ == "__main__":
    main()
    display_sidebar()