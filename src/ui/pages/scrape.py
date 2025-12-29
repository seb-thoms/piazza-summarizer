"""
Piazza Insight Analyzer - Scraping Page
Handles scraping new courses and re-scraping existing ones.
"""

import streamlit as st
from pathlib import Path
import sys
import time


# Page config
st.set_page_config(
    page_title="Scrape Course - Piazza Analyzer",
    page_icon="📊",
    layout="wide"
)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from piazza_summarizer.scrapers.piazza_scraper import PiazzaScraper
from ui.utils.file_detection import get_course_filepath


def main():
    """Main scraping page."""

    st.title("📊 Scrape Piazza Course")

    # Check if this is a re-scrape or new course
    is_rescrape = 'rescrape_course' in st.session_state

    if is_rescrape:
        display_rescrape_header()
    else:
        display_new_course_header()

    st.markdown("---")

    # Scraping form
    display_scraping_form(is_rescrape)


def display_rescrape_header():
    """Display header for re-scraping existing course."""
    metadata = st.session_state.get('course_metadata', {})
    course_name = metadata.get('display_name', 'Unknown Course')

    st.info(
        f"🔄 **Re-scraping: {course_name}**\n\n"
        f"This will update the existing data with the latest posts from Piazza."
    )


def display_new_course_header():
    """Display header for scraping new course."""
    st.markdown(
        "📥 **Scrape a new course** to download discussion posts for analysis.\n\n"
        "You'll need your Piazza credentials and the course Network ID."
    )


def display_scraping_form(is_rescrape: bool):
    """Display the scraping form with credential inputs."""

    # Get course info if re-scraping
    if is_rescrape:
        metadata = st.session_state.get('course_metadata', {})
        default_course_name = metadata.get('display_name', '')
        rescrape_file = st.session_state.get('rescrape_course', '')
    else:
        default_course_name = ''
        rescrape_file = None

    with st.form("scraping_form"):
        st.subheader("Course Information")

        col1, col2 = st.columns(2)

        with col1:
            course_name = st.text_input(
                "Course Name *",
                value=default_course_name,
                placeholder="e.g., CS5010 Fall 2025",
                help="Enter a descriptive name for this course"
            )

        with col2:
            network_id = st.text_input(
                "Piazza Network ID *",
                placeholder="e.g., abc123xyz",
                help="Find this in your Piazza course URL: piazza.com/class/[NETWORK_ID]"
            )

        st.markdown("---")
        st.subheader("Piazza Credentials")

        st.warning(
            "⚠️ **Privacy Notice:** Your credentials are only used to connect to Piazza "
            "and are never stored. You'll need to enter them each time you scrape."
        )

        col1, col2 = st.columns(2)

        with col1:
            email = st.text_input(
                "Piazza Email *",
                placeholder="your_email@northeastern.edu",
                type="default"
            )

        with col2:
            password = st.text_input(
                "Piazza Password *",
                placeholder="Enter your password",
                type="password"
            )

        st.markdown("---")
        st.subheader("Scraping Options")

        col1, col2 = st.columns(2)

        with col1:
            public_only = st.checkbox(
                "Public posts only",
                value=True,
                help="Only scrape posts visible to all students (recommended)"
            )

        with col2:
            limit = st.number_input(
                "Limit posts (0 = all)",
                min_value=0,
                value=0,
                help="For testing, you can limit the number of posts. Set to 0 to scrape all."
            )

        st.markdown("---")

        # Submit button
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            submitted = st.form_submit_button(
                "🚀 Start Scraping",
                type="primary",
                use_container_width=True
            )

    # Process form submission
    if submitted:
        # Validate inputs
        if not all([course_name, network_id, email, password]):
            st.error("❌ Please fill in all required fields (marked with *)")
            return

        # Start scraping
        start_scraping(
            course_name=course_name,
            network_id=network_id,
            email=email,
            password=password,
            public_only=public_only,
            limit=limit if limit > 0 else None,
            is_rescrape=is_rescrape,
            rescrape_file=rescrape_file
        )


def start_scraping(
        course_name: str,
        network_id: str,
        email: str,
        password: str,
        public_only: bool,
        limit: int,
        is_rescrape: bool,
        rescrape_file: str
):
    """Execute the scraping process with progress updates."""

    # Create progress containers
    progress_container = st.container()
    status_container = st.container()

    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()

    try:
        # Step 1: Initialize scraper
        status_text.text("🔌 Initializing scraper...")
        progress_bar.progress(10)
        time.sleep(0.5)

        scraper = PiazzaScraper(email=email, password=password)

        # Step 2: Login
        status_text.text("🔐 Authenticating with Piazza...")
        progress_bar.progress(20)
        scraper.login()
        time.sleep(0.5)

        # Step 3: Connect to course
        status_text.text("📚 Connecting to course...")
        progress_bar.progress(30)
        scraper.connect_to_course(network_id)

        # Show instructor info
        try:
            instructors = scraper.get_course_instructors()
            instructor_names = [i['name'] for i in instructors]
            status_container.success(
                f"✓ Connected! Found {len(instructors)} instructors: {', '.join(instructor_names[:3])}"
            )
        except:
            status_container.info("✓ Connected to course")

        time.sleep(0.5)

        # Step 4: Fetch posts
        status_text.text("📥 Fetching posts from Piazza...")
        progress_bar.progress(40)

        posts = scraper.get_all_posts(limit=limit, sleep=3, public_only=public_only)

        progress_bar.progress(80)
        time.sleep(0.5)

        # Step 5: Save to file
        status_text.text("💾 Saving to file...")
        progress_bar.progress(90)

        # Generate filename
        if is_rescrape and rescrape_file:
            output_file = get_course_filepath(rescrape_file)
        else:
            # Create filename from course name
            safe_name = course_name.replace(' ', '_').replace('/', '_')
            output_file = get_course_filepath(f"{safe_name}.jsonl")

        scraper.save_to_jsonl(posts, str(output_file))

        progress_bar.progress(100)
        status_text.text("✅ Scraping complete!")

        # Display results
        display_scraping_results(posts, output_file, public_only)

        # Clear password from memory
        password = None

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ **Scraping failed:** {str(e)}")
        st.exception(e)


def display_scraping_results(posts: list, output_file: Path, public_only: bool):
    """Display scraping results and next steps."""

    st.markdown("---")
    st.success("### ✅ Scraping Complete!")

    # Statistics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Posts", len(posts))

    with col2:
        public_count = sum(1 for p in posts if p.get('is_public', True))
        st.metric("Public Posts", public_count)

    with col3:
        private_count = len(posts) - sum(1 for p in posts if p.get('is_public', True))
        st.metric("Private Posts", f"{private_count} (excluded)" if public_only else private_count)

    # File info
    st.info(f"📁 **Saved to:** `{output_file.name}`")

    # Assignment breakdown
    folders = set()
    for post in posts:
        folders.update(post.get('folders', []))

    if folders:
        st.markdown("**Assignments found:**")
        folder_list = ', '.join(sorted(folders))
        st.markdown(f"`{folder_list}`")

    # Next steps
    st.markdown("---")
    st.markdown("### 🎯 Next Steps")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Analyze This Course", type="primary", use_container_width=True):
            # Store course info and navigate
            st.session_state['selected_course'] = output_file.name
            st.session_state['course_metadata'] = {
                'display_name': output_file.stem.replace('_', ' '),
                'total_posts': len(posts),
                'public_posts': sum(1 for p in posts if p.get('is_public', True)),
                'available_folders': sorted(list(folders))
            }
            st.switch_page("pages/2_🔍_Analyze.py")

    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            # Clear session state
            if 'rescrape_course' in st.session_state:
                del st.session_state['rescrape_course']
            st.switch_page("app.py")


if __name__ == "__main__":
    main()