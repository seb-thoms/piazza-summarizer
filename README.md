# Piazza Insight Analyzer

A tool to scrape, analyze, and summarize student discussions from Piazza to help faculty improve their courses and assignments.

**Developed at:** Center for Advancing Teaching and Learning through Research (CATLR), Northeastern University
**Status:** This project is still being developed - MVP Phase


## Overview

Piazza Insight Analyzer helps faculty understand what students are confused about by analyzing discussion posts. The tool:

1. **Scrapes** Piazza discussions (with PII removal)
2. **Filters** posts by assignment
3. **Analyzes** common themes and confusion points using LLMs
4. **Suggests** ways to improve assignment clarity

### Use Cases

- Identify common student confusion points
- Generate FAQs from discussions
- Improve assignment instructions
- Track discussion patterns over time
- Understand student learning challenges

---

## Features

### Core Functionality

**Piazza Scraping**
- Scrape discussion posts via Piazza API
- Filter public/private posts
- Capture nested discussions (followups and replies)
- Automatic instructor/TA detection

**Privacy Protection**
- Automatic PII removal (student/instructor names)
- NER-based name detection with roster validation
- HTML entity cleaning
- Case-insensitive redaction

**Web Interface**
- User-friendly Streamlit UI
- Progress tracking during scraping
- Course data caching (no re-scraping needed)
- Assignment filtering

**LLM Analysis** (Need to automate it with the current workflow)
- Discussion summarization
- Theme clustering
- Common confusion identification
- Assignment improvement suggestions

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Piazza instructor account access
- Virtual environment (recommended)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd piazza-summarizer
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Step 3: Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Download spaCy model for PII removal
python -m spacy download en_core_web_sm
```

### Step 4: Setup UI Structure

```bash
# Make setup script executable (Linux/Mac)
chmod +x setup_ui.sh

# Run setup
./setup_ui.sh
```

### Step 5: Verify Installation

```bash
# Test spaCy
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✓ spaCy loaded')"

# Test PII removal
python test_pii_removal.py
```

---

## Quick Start

### Web Interface

```bash
# Start the Streamlit app
streamlit run ui/app.py
```

Then:
1. Click "Scrape New Course"
2. Enter course name, Network ID, and Piazza credentials
3. Set "Public posts only" ✓
4. Click "Start Scraping"
5. Analyze discussions by assignment
---

## Usage Guide

### Scraping Course Data

#### Finding Your Network ID

1. Go to your Piazza course
2. Look at the URL: `https://piazza.com/class/XXXXXXXXX`
3. The `XXXXXXXXX` is your Network ID

#### First Time Scraping

1. Launch app: `streamlit run ui/app.py`
2. Click **"Scrape New Course"**
3. Fill in the form:
   - **Course Name**: e.g., "CS 5010 Fall 2025"
   - **Network ID**: From Piazza URL
   - **Email**: Your Piazza email
   - **Password**: Your Piazza password
   - **Public posts only**: ✓ (Recommended)
   - **Limit posts**: 0 for all, or number for testing
4. Click **"Start Scraping"**
5. Wait for completion (2-5 minutes for 100+ posts)

#### Re-scraping (Updating Data)

1. From home page, click **"Re-scrape"** on existing course
2. Enter credentials
3. Data will be updated with latest posts

### Analyzing Discussions

#### Via Web Interface

1. From home page, click **"Use This Data"**
2. Select an assignment from dropdown
3. View filtered posts
4. (LLM analysis coming soon)

#### Via Command Line (For LLM Prototyping)

```bash
python extract_assignment_posts.py
```

This generates a formatted text file you can paste into Claude Chat for analysis.

**Suggested Prompt for Claude:**
```
# SYSTEM INSTRUCTIONS

You are an AI pedagogical assistant helping a professor analyze student discussions from Piazza.

**Your Task:**
Analyze the discussion posts below and identify patterns in student questions and confusion points.

**Output Requirements:**
- Provide analysis in clear, well-formatted Markdown
- Cite specific post numbers when making claims (e.g., "as seen in Post #550")
- Be objective and data-driven
- Focus on actionable insights

**Privacy Note:** Student names have been redacted as [NAME] for privacy protection.

---

# ASSIGNMENT DETAILS

[Faculty pastes assignment description, objectives, and requirements here]

---

# DISCUSSION DATA

**Analysis Scope:**
- Total Posts: {count}
- Date Range: {start_date} - {end_date}
- Public Posts: {public_count}

Below are the student discussion posts:

{formatted_posts}

---

# ANALYSIS REQUEST

Please provide the following analysis:

## 1. Executive Summary
Provide a 2-3 paragraph overview covering:
- What are the main topics students are discussing?
- What patterns do you observe in the discussions?
- Overall sentiment (e.g., confused, confident, struggling with specific concepts)
- Key takeaways for the instructor

## 2. Discussion Themes
Group similar questions and discussions into themes. For each theme:
- **Theme Name**: Clear, descriptive title
- **Description**: What this theme is about
- **Posts**: List specific post numbers (e.g., #550, #551, #555)
- **Student Impact**: How many students/posts are affected
- **Key Quotes**: Brief relevant excerpts (with post numbers)

Organize themes by prevalence (most common first).
```

### Understanding the Output

#### JSONL Structure

Each post is saved as a JSON object:

```json
{
  "post_id": "abc123",
  "post_number": 550,
  "is_public": true,
  "subject": "Lab 7 question",
  "content": "I'm working with [NAME] on this...",
  "folders": ["labs"],
  "instructor_answer": {
    "content": "Here's the answer..."
  },
  "followups": [
    {
      "content": "Thanks!",
      "author_type": "student",
      "replies": [...]
    }
  ]
}
```

#### PII Redaction

All names are replaced with `[NAME]`:
- Student names: `[NAME]`
- Instructor names: `[NAME]`
- Case-insensitive matching
- Context-aware (doesn't replace "Will you" as a name)


## Troubleshooting

### Adding Features

1. **Backend logic** → `src/piazza_summarizer/`
2. **UI pages** → `ui/pages/`
3. **Utilities** → `src/piazza_summarizer/utils/`
4. **Tests** → `tests/`

### Logging

Logs are written to `logs/` directory:
- `piazza_scraper.log` - Backend scraping logs
- `streamlit.log` - UI action logs (if enabled)

View logs:
```bash
tail -f logs/piazza_scraper.log
```

## Roadmap

### Completed

- [x] Piazza scraping with API
- [x] Public/private post filtering
- [x] Nested discussion structure
- [x] PII removal (NER + roster)
- [x] Streamlit web interface
- [x] Assignment filtering
- [x] CLI extraction tool

### In Progress

- [ ] LLM integration (Claude API)
- [ ] Discussion summarization
- [ ] Theme clustering
- [ ] Confusion point identification


---

## Acknowledgments

- **CATLR** - Center for Advancing Teaching and Learning through Research
- **Northeastern University**
- **Piazza-Scraper** - For providing the module to scrape Piazza
- **Anthropic** - For Claude AI capabilities

## Disclaimer

This tool is for educational and research purposes. Users are responsible for:
- Obtaining necessary IRB approvals
- Following university data policies
- Ensuring proper authorization to access course data
- Protecting student privacy

**Use responsibly and ethically.**