import os
import re
import pandas as pd
from openai import OpenAI

# API key (replace with your actual key)
openai_api_key = "your-openai-api-key-here"
client = OpenAI(api_key=openai_api_key)

def call_openai_chat(messages, max_tokens=2000):
    """Calls OpenAI API for chat completion."""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=max_tokens,
            stream=False
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ API Error: {e}")
        return ""

def extract_video_transcripts(file_path):
    """Extracts individual video transcripts from a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = r'====\s*Video\s*\d+(?:\s*\([^)]*\))?\s*===='
    transcripts = [t.strip() for t in re.split(pattern, content) if t.strip()]
    return transcripts

def extract_facts(transcript, locality):
    """Extracts real estate facts from a transcript."""
    messages = [
        {
            "role": "system",
            "content": (
                f"Extract key real estate facts from the following YouTube video transcript about the {locality} market. "
                f"Focus on concise, engaging insights specific to {locality} that will excite readers, categorized as follows:\n"
                "1. **Market Gossip & Buzz**: Hot rumors, insider chatter, or trending opinions about {locality}’s real estate scene.\n"
                "2. **New Projects Launched**: Name of project, location within {locality}, builder, price range, unit sizes, amenities.\n"
                "3. **Upcoming Projects**: Planned developments or teased projects in {locality}, including rumored builders or timelines.\n"
                "4. **Price Changes in Existing Projects & Localities**: Areas or projects in {locality} with price increases or decreases (include percentages if available).\n"
                "5. **Infrastructure Developments**: New roads, metro lines, expressways, SEZs, or commercial hubs boosting {locality}’s real estate.\n"
                "6. **Government Policies & Regulations**: New policies, tax benefits, zoning changes, or infrastructure plans impacting {locality}.\n"
                "7. **Builder & Developer News**: Land acquisitions, major builder updates, or significant moves in {locality}.\n"
                "8. **Housing Trends (Luxury vs. Affordable)**: Demand shifts, buyer preferences, and investment potential in {locality}.\n"
                "9. **Market Overview & Comparisons**: How {locality} stacks up against nearby markets (e.g., Gurgaon, NCR) in demand, supply, and growth.\n"
                "10. **Expert Opinions & Market Predictions**: Forecasts, investor sentiment (including NRI interest), or future outlooks for {locality}.\n"
                "Keep each fact concise (2-3 sentences max) and captivating. Label speculative or unverified info as 'Rumor' or 'Opinion'. "
                "Correct spelling errors and adapt to Indian real estate terms (e.g., developer/project names may vary slightly). "
                f"Ignore generic real estate info not tied to {locality}. Leave categories empty if no relevant data is found."
            )
        },
        {"role": "user", "content": transcript}
    ]
    return call_openai_chat(messages, max_tokens=5000)

def generate_blog(extracted_facts_text, locality, last_no_of_days):
    """Generates a blog post from real estate facts."""
    messages = [
        {"role": "system", "content": "You are a real estate market expert skilled at crafting engaging, informative blog posts."},
        {
            "role": "user",
            "content": (
                f"Using the extracted real estate facts below, write a detailed, exciting blog post analyzing the {locality} real estate market over the last {last_no_of_days} days. "
                f"Do not use words/context/sentence which does not make sense logically. **** keep it professional **** . Make it captivating for readers by blending buzz, facts, and future outlooks:\n\n"
                f"{extracted_facts_text}\n\n"
                "Structure it as follows:\n"
                "### 1. Introduction\n- Kick off with a lively summary of {locality}’s real estate scene, highlighting key trends and buzz over the last {last_no_of_days} days.\n"
                "### 2. Market Gossip & Buzz\n- Share the hottest rumors and chatter about {locality}’s market; note if nothing juicy surfaced.\n"
                "### 3. New Projects Launched\n- List recently launched projects in {locality} with key details; if none, mention the quiet spell.\n"
                "### 4. Upcoming Projects\n- Tease planned or rumored developments in {locality}; note if no whispers emerged.\n"
                "### 5. Price Changes in Existing Projects & Localities\n- Detail price shifts in {locality}; if stable, discuss what’s keeping it steady.\n"
                "### 6. Infrastructure Developments\n- Highlight new infrastructure boosting {locality}’s appeal; infer impact if data is sparse.\n"
                "### 7. Government Policies & Regulations\n- Summarize policies or regulations affecting {locality}; note if no updates exist.\n"
                "### 8. Builder & Developer News\n- Spotlight big moves by builders in {locality}; mention if it’s business as usual.\n"
                "### 9. Housing Trends (Luxury vs. Affordable)\n- Explore demand shifts and buyer vibes in {locality}; provide general sentiment if specifics are missing.\n"
                "### 10. Market Overview & Comparisons\n- Compare {locality}’s market to nearby areas; highlight its edge or challenges.\n"
                "### 11. Expert Opinions & Market Predictions\n- Wrap up with forecasts and investor sentiment for {locality}; speculate lightly if no opinions were shared.\n"
                "### 12. Conclusion\n- Sum up {locality}’s real estate highlights and offer practical tips for buyers or investors.\n"
                "***Keep it brief(very large with lots of details) yet thrilling***. Use all provided facts without adding unverified info beyond what’s labeled 'Rumor' or 'Opinion'. "
                "If any section lacks data, acknowledge it creatively (e.g., 'The rumor mill’s quiet for now!') rather than skipping it."
            )
        }
    ]
    return call_openai_chat(messages, max_tokens=16000)

def main():
    """Processes translated transcripts to generate real estate blogs."""
    csv_path = "city_locality_list.csv"
    extracted_facts_dir = "extracted_facts"
    final_blog_dir = "final_blog"
    os.makedirs(extracted_facts_dir, exist_ok=True)
    os.makedirs(final_blog_dir, exist_ok=True)

    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return
    df = pd.read_csv(csv_path)
    required_columns = {"city", "days", "translated_path"}
    if not required_columns.issubset(df.columns):
        print(f"❌ CSV must contain {required_columns}.")
        return

    extracted_facts_paths = []
    final_blog_paths = []
    for index, row in df.iterrows():
        city = row["city"]
        days = row["days"]
        translated_path = row["translated_path"]

        if not translated_path or not os.path.exists(translated_path):
            print(f"⚠️ Skipping row {index}: Translated path '{translated_path}' invalid.")
            extracted_facts_paths.append("")
            final_blog_paths.append("")
            continue

        transcripts = extract_video_transcripts(translated_path)
        if not transcripts:
            print(f"❌ No valid transcripts found for {city}.")
            extracted_facts_paths.append("")
            final_blog_paths.append("")
            continue

        final_transcripts = []
        for idx, transcript in enumerate(transcripts, start=1):
            print(f"▶ Processing Video {idx} for {city}...")
            facts = extract_facts(transcript, city)
            final_transcripts.append(f"==== Video {idx} Facts ====\n{facts}\n")

        extracted_facts_text = "\n".join(final_transcripts)
        transcript_filename = os.path.basename(translated_path).replace("_transcript.txt", "")
        facts_path = os.path.join(extracted_facts_dir, f"{transcript_filename}_facts.txt")
        with open(facts_path, "w", encoding="utf-8") as f:
            f.write(extracted_facts_text)
        print(f"✅ Saved facts to: {facts_path}")

        print(f"▶ Generating blog for {city}...")
        final_blog = generate_blog(extracted_facts_text, city, days)
        blog_path = os.path.join(final_blog_dir, f"{transcript_filename}_blog.txt")
        with open(blog_path, "w", encoding="utf-8") as f:
            f.write(final_blog)
        print(f"✅ Saved blog to: {blog_path}")

        extracted_facts_paths.append(facts_path)
        final_blog_paths.append(blog_path)

    df["extracted_facts_path"] = extracted_facts_paths
    df["final_blog_path"] = final_blog_paths
    df.to_csv(csv_path, index=False)
    print(f"✅ Updated CSV with new paths: {csv_path}")

if __name__ == "__main__":
    main()
