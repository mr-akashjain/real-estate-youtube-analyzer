# Real Estate YouTube Analyzer

## What It Is

The `real-estate-youtube-analyzer` is a machine learning-powered pipeline designed to automate real estate market analysis by processing YouTube videos. It scrapes videos based on city-specific real estate keywords, transcribes audio into text using Vosk, translates non-English transcripts to English with Chrome automation, extracts key real estate facts using OpenAI's GPT-4o, and generates detailed market analysis blog posts. This project showcases ML and NLP skills, making it a valuable addition to job applications while offering a practical tool for real estate enthusiasts, researchers, and content creators.

Originally built to streamline real estate research, it processes hours of video content into structured insights in minutes. Beyond real estate, it’s adaptable for any topic (e.g., tech trends, health tips) by adjusting the GPT-4o prompts, turning it into a versatile video-to-content converter.

### Key Features
- **Video Scraping & Transcription**: Downloads YouTube videos with `yt-dlp` and transcribes them using Vosk in one workflow, supporting English, Hindi, Telugu, and Gujarati.
- **Translation**: Automatically translates transcripts to English via Chrome and Selenium.
- **Fact Extraction**: Uses GPT-4o to pull categorized real estate insights (e.g., new projects, price changes).
- **Blog Generation**: Creates professional, structured blog posts with market analysis.

### Why I Built It
I wanted to save time researching real estate trends across cities by automating the process of extracting insights from YouTube videos. This tool combines open-source ML models (Vosk, SpeechBrain) with powerful APIs (OpenAI) to deliver a full pipeline from raw video to polished content, showcasing my ability to solve real-world problems with ML.

## Installation

To get started, clone this repository and set up the dependencies and tools as follows:

### 1. Clone the Repository:
```bash
git clone https://github.com/yourusername/real-estate-youtube-analyzer
cd real-estate-youtube-analyzer
```

### 2. Install Python Dependencies:
Install all required packages, including `yt-dlp`, with one command:
```bash
pip install -r requirements.txt
```

### 3. Install Google Chrome:
Required for translation. Download and install from [here](https://www.google.com/chrome/).

### 4. Download Vosk Models:
This project uses small Vosk models for efficiency in four languages:
- **English**: `vosk-model-small-en-in-0.4`
- **Hindi**: `vosk-model-small-hi-0.22`
- **Telugu**: `vosk-model-small-te-0.42`
- **Gujarati**: `vosk-model-small-gu-0.42`

Extract these to a folder (e.g., `C:\Vosk\Models`) and update the paths in `transcription.py`:
```python
VOSK_MODEL_EN = "C:/Vosk/Models/vosk-model-small-en-in-0.4"
VOSK_MODEL_HI = "C:/Vosk/Models/vosk-model-small-hi-0.22"
VOSK_MODEL_TE = "C:/Vosk/Models/vosk-model-small-te-0.42"
VOSK_MODEL_GU = "C:/Vosk/Models/vosk-model-small-gu-0.42"
```

### 5. Set Up OpenAI API Key:
Get your key from OpenAI.

Edit `blog_generation.py` and replace `"your-openai-api-key-here"` with your key:
```python
openai_api_key = "your-actual-openai-api-key"
```

## How to Use It
This tool is designed to be straightforward—just provide a CSV and run three scripts:

### 1. Prepare Input CSV:
Create a file named `city_locality_list.csv` in the project folder with two columns:
```csv
city,days
Mumbai,30
Delhi,45
```
- `city`: Name of the city (e.g., "Mumbai").
- `days`: Number of days to filter videos by recency (e.g., 30 for the last month).

### 2. Run the Pipeline:
Execute the scripts in sequence from your terminal:
```bash
python transcription.py
python translation.py
python blog_generation.py
```

### 3. Check Outputs:
- `transcripts/`: Multilingual transcripts (e.g., `Mumbai_real_estate_market_transcript.txt`).
- `translated/`: English translations.
- `extracted_facts/`: Categorized real estate facts.
- `final_blog/`: Full blog posts.

## Tweaking for General Purpose
While built for real estate, this pipeline is highly adaptable for any topic by modifying the GPT-4o prompts in `blog_generation.py`.

### Step 1: Adjust the Search Keyword
In `transcription.py`, change the keyword from `city + " real estate market"` to your desired topic:
```python
city = row["city"]  # Remove " real estate market" and use "city" as a general topic
```
Update your CSV to use topics instead of cities:
```csv
city,days
Machine Learning Trends,30
Healthy Cooking Recipes,45
```

### Step 2: Modify Fact Extraction Prompt
Edit `extract_facts` in `blog_generation.py` to match your topic:
```python
def extract_facts(transcript, locality):
    messages = [
        {
            "role": "system",
            "content": (
                f"Extract key facts from this YouTube video transcript about {locality}. "
                "Focus on concise insights specific to {locality}, categorized as follows:\n"
                "1. **Latest Developments**\n"
                "2. **Expert Insights**\n"
                "3. **Trends**\n"
            )
        },
        {"role": "user", "content": transcript}
    ]
    return call_openai_chat(messages, max_tokens=5000)
```

### Step 3: Update Blog Generation Prompt
Modify `generate_blog` to reflect your new structure:
```python
def generate_blog(extracted_facts_text, locality, last_no_of_days):
    messages = [
        {"role": "system", "content": "You are an expert writer crafting engaging blog posts."},
        {
            "role": "user",
            "content": (
                f"Write a blog post about {locality} over the last {last_no_of_days} days using these facts:\n"
                f"{extracted_facts_text}\n"
                "### 1. Introduction\n"
                "### 2. Latest Developments\n"
                "### 3. Expert Insights\n"
                "### 4. Trends\n"
                "### 5. Conclusion\n"
            )
        }
    ]
    return call_openai_chat(messages, max_tokens=16000)
```

## Tech Stack
- **Python, pandas**: Core scripting and data handling.
- **yt-dlp**: Video scraping and audio downloading.
- **Vosk**: Speech-to-text transcription.
- **SpeechBrain**: Language detection.
- **Selenium, pyautogui**: Browser automation for translation.
- **OpenAI GPT-4o**: Fact extraction and blog generation.

## License
MIT License

