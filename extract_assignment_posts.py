#!/usr/bin/env python3
"""
Extract posts from a specific assignment folder for LLM prototyping.
Console-based script to filter JSONL by assignment.
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from piazza_summarizer.utils.file_handler import JSONLHandler


def list_jsonl_files():
    """List all available JSONL files in data/courses/."""
    data_dir = Path("src/data/courses")

    if not data_dir.exists():
        print("❌ Error: data/courses/ directory not found")
        return []

    jsonl_files = list(data_dir.glob("*.jsonl"))

    if not jsonl_files:
        print("❌ Error: No JSONL files found in data/courses/")
        return []

    return jsonl_files


def get_available_folders(posts):
    """Extract unique folder names from posts."""
    folders = set()
    for post in posts:
        folders.update(post.get('folders', []))

    return sorted(list(folders))


def filter_posts_by_folder(posts, folder_name):
    """Filter posts that belong to a specific folder."""
    filtered = [
        post for post in posts
        if folder_name.lower() in [f.lower() for f in post.get('folders', [])]
    ]
    return filtered


def format_post_for_llm(post):
    """Format a single post in a readable way for LLM input."""
    lines = []

    # Header
    lines.append("=" * 80)
    lines.append(f"POST #{post.get('post_number', 'N/A')} - {post.get('subject', 'No Subject')}")
    lines.append("=" * 80)

    # Metadata
    lines.append(f"Type: {post.get('type', 'unknown')}")
    # lines.append(f"Created: {post.get('created', 'unknown')}")
    # lines.append(f"Public: {'Yes' if post.get('is_public') else 'No'}")
    # lines.append(f"Folders: {', '.join(post.get('folders', []))}")
    # lines.append(f"Views: {post.get('unique_views', 0)}")
    lines.append("")

    # Main content
    lines.append("QUESTION:")
    lines.append(post.get('content', 'No content'))
    lines.append("")

    # Student answer
    if post.get('student_answer'):
        lines.append("STUDENT ANSWER:")
        lines.append(post['student_answer'].get('content', 'No content'))
        lines.append("")

    # Instructor answer
    if post.get('instructor_answer'):
        lines.append("INSTRUCTOR ANSWER:")
        lines.append(post['instructor_answer'].get('content', 'No content'))
        lines.append("")

    # Followups
    if post.get('followups'):
        lines.append(f"FOLLOWUP DISCUSSIONS ({len(post['followups'])}):")
        for i, followup in enumerate(post['followups'], 1):
            lines.append(f"\n  Followup #{i} (by {followup.get('author_type', 'unknown')}):")
            lines.append(f"  {followup.get('content', 'No content')}")

            # Replies to followup
            if followup.get('replies'):
                for j, reply in enumerate(followup['replies'], 1):
                    lines.append(f"\n    Reply #{j} (by {reply.get('author_type', 'unknown')}):")
                    lines.append(f"    {reply.get('content', 'No content')}")
        lines.append("")

    lines.append("\n")

    return "\n".join(lines)


def save_formatted_posts(posts, output_file):
    """Save formatted posts to a text file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        for post in posts:
            formatted = format_post_for_llm(post)
            f.write(formatted)
            f.write("\n")

    print(f"✅ Saved formatted posts to: {output_file}")


def main():
    """Main function."""
    print("\n" + "=" * 80)
    print("PIAZZA POST EXTRACTOR - For LLM Prototyping")
    print("=" * 80 + "\n")

    # Step 1: List available JSONL files
    jsonl_files = list_jsonl_files()

    if not jsonl_files:
        return

    print("📁 Available course files:")
    for i, file in enumerate(jsonl_files, 1):
        print(f"  {i}. {file.name}")

    # Step 2: Select file
    print()
    try:
        file_choice = int(input("Select file number: ")) - 1
        if file_choice < 0 or file_choice >= len(jsonl_files):
            print("❌ Invalid selection")
            return

        selected_file = jsonl_files[file_choice]
    except (ValueError, KeyboardInterrupt):
        print("\n❌ Invalid input")
        return

    print(f"\n📖 Loading posts from: {selected_file.name}")

    # Step 3: Load posts
    try:
        posts = JSONLHandler.read(str(selected_file))
        print(f"✅ Loaded {len(posts)} posts")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return

    # Step 4: Show available folders
    folders = get_available_folders(posts)

    if not folders:
        print("❌ No assignment folders found in posts")
        return

    print(f"\n📂 Available assignments:")
    for i, folder in enumerate(folders, 1):
        # Count posts in this folder
        count = len([p for p in posts if folder in p.get('folders', [])])
        print(f"  {i}. {folder} ({count} posts)")

    # Step 5: Select folder
    print()
    try:
        folder_input = input("Enter assignment name or number: ").strip()

        # Check if it's a number
        if folder_input.isdigit():
            folder_choice = int(folder_input) - 1
            if folder_choice < 0 or folder_choice >= len(folders):
                print("❌ Invalid selection")
                return
            selected_folder = folders[folder_choice]
        else:
            # It's a name - find closest match
            selected_folder = folder_input
            if selected_folder not in folders:
                # Try case-insensitive match
                matches = [f for f in folders if f.lower() == selected_folder.lower()]
                if matches:
                    selected_folder = matches[0]
                else:
                    print(f"❌ Assignment '{selected_folder}' not found")
                    return

    except (KeyboardInterrupt):
        print("\n❌ Cancelled")
        return

    # Step 6: Filter posts
    print(f"\n🔍 Filtering posts for assignment: {selected_folder}")
    filtered_posts = filter_posts_by_folder(posts, selected_folder)

    if not filtered_posts:
        print(f"❌ No posts found for assignment: {selected_folder}")
        return

    print(f"✅ Found {len(filtered_posts)} posts")

    # Step 7: Show summary
    print(f"\n📊 Summary:")
    print(f"  Total posts: {len(filtered_posts)}")
    public_count = sum(1 for p in filtered_posts if p.get('is_public'))
    print(f"  Public posts: {public_count}")
    answered_count = sum(1 for p in filtered_posts if p.get('instructor_answer'))
    print(f"  Posts with instructor answer: {answered_count}")

    # Step 8: Save options
    print("\n💾 Save options:")
    print("  1. Save as formatted text (for pasting into Claude)")
    print("  2. Save as JSON (structured data)")
    print("  3. Both")
    print("  4. Display in console only")

    try:
        save_choice = input("\nSelect option (1-4): ").strip()
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
        return

    output_base = f"output_{selected_folder.replace(' ', '_')}"

    if save_choice in ['1', '3']:
        # Save formatted text
        output_file = f"{output_base}.txt"
        save_formatted_posts(filtered_posts, output_file)
        print(f"\n📄 You can now copy {output_file} and paste into Claude Chat!")

    if save_choice in ['2', '3']:
        # Save JSON
        output_file = f"{output_base}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_posts, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved JSON to: {output_file}")

    if save_choice == '4':
        # Display in console
        print("\n" + "=" * 80)
        print("DISPLAYING POSTS IN CONSOLE")
        print("=" * 80 + "\n")
        for post in filtered_posts:
            print(format_post_for_llm(post))

    # Step 9: Statistics for LLM prompt
    print("\n" + "=" * 80)
    print("📋 SUGGESTED PROMPT FOR CLAUDE:")
    print("=" * 80)
    print(f"""
I have {len(filtered_posts)} discussion posts from a {selected_folder} assignment in my software engineering course. 
Please analyze these discussions and provide:

1. **Summary**: A brief overview of the main topics discussed
2. **Common Questions**: What are students most confused about?
3. **FAQ**: Top 5-10 frequently asked questions with answers
4. **Themes**: Group similar questions/issues together
5. **Suggestions**: How can the assignment instructions be improved?

Here are the posts:
[Paste the contents of {output_base}.txt here]
""")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(0)