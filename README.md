# Real Estate YouTube Analyzer

## What It Is

The `real-estate-youtube-analyzer` is a machine learning-powered pipeline designed to automate real estate market analysis by processing YouTube videos. It helps real estate agents and companies stay informed about local market discussions—often presented by brokers or realtors on YouTube—without spending hours watching videos. By transcribing and translating these videos automatically, it transforms them into structured, readable insights that can be quickly reviewed and shared.

Although it focuses on real estate use cases, it's easy to extend or modify for other domains (e.g., technology, cooking, fitness). Instead of painstakingly watching videos on a topic, you can automate the process from transcription to final summary or blog post.

## Why It Matters
- **Saves Time**: Local brokers and experts often discuss market changes on YouTube, but watching all these videos is time-consuming. This pipeline transcribes and extracts the important details, saving hours.
- **Structured Analysis**: Summaries and fact extraction transform messy video content into organized insights.
- **Multilingual Support**: Handles English, Hindi, Telugu, and Gujarati, and can be extended to more languages.
- **Easily Extensible**: Replace the open-source models with paid APIs (e.g., Whisper, AssemblyAI, or ElevenLabs) or change the translation method (e.g., Google Cloud Translate, AWS Translate) for higher accuracy or different cost/performance trade-offs.

## Key Features
- **Video Scraping & Transcription**: Downloads YouTube videos with `yt-dlp` and transcribes them using Vosk.
- **Translation**: Automatically translates non-English transcripts using Selenium and Chrome.
- **Fact Extraction**: Uses GPT-4o (or any other language model) to pull relevant facts (e.g., local broker insights, market changes).
- **Blog Generation**: Creates structured blog posts summarizing the collected insights.

## Installation

To get started, clone this repository and set up the dependencies:

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/real-estate-youtube-analyzer
cd real-estate-youtube-analyzer
```

### 2. Install Python Dependencies
All required packages, including `yt-dlp`, `vosk`, `pydub`, `speechbrain`, `huggingface_hub`, `torchaudio`, `soundfile`, `pyautogui`, `selenium`, and `webdriver_manager`, are listed in `requirements.txt`. Simply run:
```bash
pip install -r requirements.txt
```

### Windows Users
- **General Compatibility**: After running `pip install -r requirements.txt`, most dependencies work fine on Windows.
- **torchaudio**: This library is included for audio processing/resampling. By default, it installs CPU support. If you want GPU acceleration, make sure you have the matching CUDA version installed. For example (CUDA 11.8):

  ```bash
  pip install torch==2.0.1+cu118 torchaudio==2.0.2+cu118 \
      -f https://download.pytorch.org/whl/torch_stable.html
  ```
- **soundfile**: Requires `libsndfile`. If you encounter errors, download the binaries from an official source and add them to your PATH.
- **Chrome**: Ensure Google Chrome is installed at its default location (e.g., `C:\Program Files\Google\Chrome`).

### 3. Download Vosk Models
This project uses small Vosk models for efficiency in four languages:
- **English**: `vosk-model-small-en-in-0.4`
- **Hindi**: `vosk-model-small-hi-0.22`
- **Telugu**: `vosk-model-small-te-0.42`
- **Gujarati**: `vosk-model-small-gu-0.42`

Download the models from [Vosk Models](https://alphacephei.com/vosk/models), extract them to a folder (e.g., `C:\Vosk\Models`), and update paths in `transcription.py`:
```python
VOSK_MODEL_EN = "C:/Vosk/Models/vosk-model-small-en-in-0.4"
VOSK_MODEL_HI = "C:/Vosk/Models/vosk-model-small-hi-0.22"
VOSK_MODEL_TE = "C:/Vosk/Models/vosk-model-small-te-0.42"
VOSK_MODEL_GU = "C:/Vosk/Models/vosk-model-small-gu-0.42"
```

### 4. Set Up OpenAI API Key (Optional)
If you use GPT-4o or any OpenAI model, get your key from OpenAI and edit `blog_generation.py`, replacing `"your-openai-api-key-here"` with your own:
```python
openai_api_key = "your-actual-openai-api-key"
```

If you prefer a different LLM, integrate that accordingly (e.g., local model, Hugging Face, etc.).

## How to Use It

### 1. Prepare an Input CSV
Create a file named `city_locality_list.csv` in the project folder with two columns:
```csv
city,days
Mumbai,30
Delhi,45
```
- **city**: Name of the city or topic.
- **days**: Number of days to filter videos by recency.

### 2. Run the Pipeline
```bash
python transcription.py   # Scrapes and transcribes videos
python translation.py     # Translates transcripts to English
python blog_generation.py # Extracts facts and generates blog summaries
```

### 3. Check Outputs
- **transcripts/**: Contains multilingual transcripts (e.g., `Mumbai_real_estate_market_transcript.txt`).
- **translated/**: Contains English translations.
- **extracted_facts/**: Contains summarized real estate facts.
- **final_blog/**: Contains final blog posts.

## Adapting to Other Topics
You can tweak the prompts in `blog_generation.py` to focus on different insights—cooking recipes, tech trends, fitness, etc. Similarly, you can switch transcription from Vosk to a paid API (Whisper, AssemblyAI, etc.), or translation from Selenium+Chrome to Google Cloud, AWS Translate, or other services.

## Practical Benefits
- **Real Estate Professionals**: Quickly get local broker insights without watching hours of YouTube videos.
- **Researchers/Analysts**: Gather and summarize unstructured video content for data-driven studies.
- **Content Creators/Bloggers**: Generate summarized articles across diverse topics automatically.

## License
MIT License

This `README.md` highlights the project's practicality for real estate market insights, while also explaining how to adapt it for other domains. By using open-source or paid solutions for transcription, translation, and fact extraction, you can tailor the pipeline to your accuracy, speed, or budget needs.

