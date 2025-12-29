"""
Piazza Insight Analyzer - Analysis Page
Placeholder - Will be implemented next.
"""

import streamlit as st
from pathlib import Path
import sys

# Page config
st.set_page_config(
    page_title="Analyze - Piazza Analyzer",
    page_icon="🔍",
    layout="wide"
)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ui.utils.file_detection import get_course_posts


def main():
    """Analysis page placeholder."""

    st.title("🔍 Analyze Discussions")

    # Check if course is selected
    if 'selected_course' not in st.session_state:
        st.warning("⚠️ No course selected. Please select a course from the home page.")
        if st.button("🏠 Go to Home"):
            st.switch_page("app.py")
        return

    # Get selected course info
    course_file = st.session_state['selected_course']
    metadata = st.session_state.get('course_metadata', {})

    st.success(f"📚 **Selected Course:** {metadata.get('display_name', course_file)}")
    st.info(
        f"📊 **Total Posts:** {metadata.get('total_posts', 'Unknown')} | "
        f"**Public Posts:** {metadata.get('public_posts', 'Unknown')}"
    )

    st.markdown("---")

    # Load posts
    try:
        posts = get_course_posts(course_file)

        # Extract available folders (assignments)
        folders = set()
        for post in posts:
            folders.update(post.get('folders', []))

        folders = sorted(list(folders))

        st.subheader("Select Assignment")

        if not folders:
            st.warning("No assignment folders found in the posts.")
        else:
            selected_folder = st.selectbox(
                "Choose an assignment to analyze:",
                options=['All Assignments'] + folders,
                help="Select which assignment's discussions to analyze"
            )

            # Filter posts by selected folder
            if selected_folder == 'All Assignments':
                filtered_posts = posts
            else:
                filtered_posts = [
                    p for p in posts
                    if selected_folder in p.get('folders', [])
                ]

            st.info(f"📝 **{len(filtered_posts)} posts** selected for analysis")

            st.markdown("---")

            # Placeholder for analysis features
            st.subheader("🚧 Analysis Features (Coming Soon)")

            st.markdown("""
            The following analysis features will be implemented:

            1. **📋 Discussion Summary** - High-level overview of all discussions
            2. **🎯 Common Themes** - Group similar questions and topics together
            3. **❓ Unanswered Questions** - Identify posts needing instructor attention
            4. **💡 Assignment Suggestions** - Recommendations for improving assignment clarity
            5. **📈 Timeline Analysis** - When do students ask questions?

            ---

            **For now, here's a preview of your data:**
            """)

            # Show sample posts
            st.subheader("Sample Posts")

            for i, post in enumerate(filtered_posts[:5]):
                with st.expander(
                        f"Post #{post.get('post_number', i + 1)}: {post.get('subject', 'No subject')[:60]}..."):
                    st.markdown(f"**Type:** {post.get('type', 'unknown')}")
                    st.markdown(f"**Created:** {post.get('created', 'unknown')}")
                    st.markdown(f"**Public:** {'Yes' if post.get('is_public') else 'No'}")
                    st.markdown(f"**Folders:** {', '.join(post.get('folders', []))}")

                    if post.get('content'):
                        st.markdown("**Content:**")
                        st.markdown(
                            post['content'][:300] + "..." if len(post.get('content', '')) > 300 else post.get('content',
                                                                                                              ''))

                    if post.get('instructor_answer'):
                        st.success("✓ Has instructor answer")

                    if post.get('student_answer'):
                        st.info("✓ Has student answer")

                    if post.get('followups'):
                        st.markdown(f"💬 {len(post['followups'])} followup(s)")

            if len(filtered_posts) > 5:
                st.info(f"Showing 5 of {len(filtered_posts)} posts. Full analysis coming soon!")

    except Exception as e:
        st.error(f"Error loading posts: {e}")
        st.exception(e)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.switch_page("app.py")

    with col2:
        if st.button("📊 Re-scrape Course", use_container_width=True):
            st.session_state['rescrape_course'] = course_file
            st.switch_page("pages/1_📊_Scrape.py")


if __name__ == "__main__":
    main()