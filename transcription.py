import os
import json
import subprocess
import datetime
from datetime import timedelta
import wave
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
import torch
import soundfile as sf
from speechbrain.pretrained import EncoderClassifier
from huggingface_hub import hf_hub_download
import re
import pandas as pd

# Configurable Vosk model paths (users set these)
VOSK_MODEL_EN = "path/to/vosk-model-small-en-in-0.4"  # English (small model)
VOSK_MODEL_HI = "path/to/vosk-model-small-hi-0.22"    # Hindi (small model)
VOSK_MODEL_TE = "path/to/vosk-model-small-te-0.42"    # Telugu (small model)
VOSK_MODEL_GU = "path/to/vosk-model-small-gu-0.42"    # Gujarati (small model)

def update_yt_dlp():
    """Updates yt-dlp to the latest version."""
    print("🔄 Updating yt-dlp...")
    try:
        subprocess.run(["yt-dlp", "-U"], check=True)
        print("✅ yt-dlp updated successfully!")
    except subprocess.CalledProcessError:
        print("⚠️ Could not update yt-dlp. Continuing...")

def search_youtube(keyword, max_results=10):
    """Searches YouTube for videos based on a keyword."""
    print(f"🔎 Searching YouTube for '{keyword}' (max {max_results} results)...")
    cmd = ["yt-dlp", "--dump-json", f"ytsearch{max_results}:{keyword}"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split("\n")
        videos = [json.loads(line) for line in lines]
        print(f"✅ Found {len(videos)} results.")
        return videos
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running yt-dlp search: {e}")
        return []

def filter_videos(video_list, days, min_duration=120):
    """Filters videos by upload date and minimum duration."""
    cutoff_date = datetime.datetime.now() - timedelta(days=days)
    cutoff_str = cutoff_date.strftime("%Y%m%d")
    cutoff_int = int(cutoff_str)
    filtered = []
    for vid in video_list:
        upload_date_str = vid.get("upload_date")
        duration = vid.get("duration", 0)
        if not upload_date_str or duration < min_duration:
            continue
        try:
            upload_date_int = int(upload_date_str)
            if upload_date_int >= cutoff_int:
                filtered.append(vid)
        except ValueError:
            continue
    print(f"✅ Filtered to {len(filtered)} videos (longer than {min_duration}s, within last {days} days).")
    return filtered

def sanitize_filename(title):
    """Sanitizes a title for use as a filename."""
    return re.sub(r'[<>:"/\\|?*’!]', '', title).replace(" ", "_")

def download_audio(video_data, output_dir="downloads"):
    """Downloads audio from a YouTube video."""
    os.makedirs(output_dir, exist_ok=True)
    video_title = sanitize_filename(video_data.get("title", "audio"))
    output_template = os.path.join(output_dir, f"{video_title}.mp3")
    webpage_url = video_data.get("webpage_url")
    if not webpage_url:
        print("❌ No webpage_url found; skipping.")
        return None
    try:
        print(f"📥 Downloading audio for {video_data.get('title')}...")
        cmd = [
            "yt-dlp", "-f", "bestaudio",
            "--extract-audio", "--audio-format", "mp3",
            "-o", output_template,
            webpage_url
        ]
        subprocess.run(cmd, check=True)
        if os.path.exists(output_template):
            print(f"✅ Audio downloaded: {output_template}")
            return output_template
    except subprocess.CalledProcessError as e:
        print(f"❌ Download failed: {e}")
        return None

def convert_to_wav(input_path, wav_path):
    """Converts MP3 to WAV format (16kHz, mono, PCM s16le)."""
    try:
        print(f"🔄 Converting {input_path} to WAV...")
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(wav_path, format="wav", codec="pcm_s16le")
        print(f"✅ Conversion completed: {wav_path}")
        return wav_path
    except Exception as e:
        print(f"❌ Error converting to WAV: {e}")
        return None

def identify_language(wav_path, language_id, temp_dir):
    """Identifies the language of an audio file."""
    try:
        audio = AudioSegment.from_wav(wav_path)
        segment = audio[:50000] if len(audio) > 50000 else audio
        temp_wav = os.path.join(temp_dir, f"temp_{os.path.basename(wav_path)}")
        segment.export(temp_wav, format="wav", codec="pcm_s16le")

        data, sample_rate = sf.read(temp_wav)
        waveform = torch.tensor(data, dtype=torch.float32).unsqueeze(0)
        if sample_rate != 16000:
            print("⚠️ Resampling to 16000 Hz...")
            waveform = torch.tensor(torchaudio.transforms.Resample(sample_rate, 16000)(waveform.numpy()))
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        if waveform.shape[1] > 960000:
            waveform = waveform[:, :960000]

        prediction = language_id.classify_batch(wav_path)
        language = prediction[3][0].split(':')[0].strip()
        os.remove(temp_wav)
        print(f"🌐 Identified language: {language}")
        return language
    except Exception as e:
        print(f"❌ Error identifying language: {e}")
        return "en"

def transcribe_vosk(wav_path, model_dir):
    """Transcribes WAV audio using Vosk."""
    try:
        if not os.path.exists(model_dir):
            raise FileNotFoundError(f"Vosk model not found: {model_dir}")
        model = Model(model_dir)
        wf = wave.open(wav_path, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000, 32000, 44100, 48000]:
            raise ValueError("Audio must be WAV mono PCM with supported sample rate.")
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        full_text = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                full_text += result.get("text", "") + " "
        final_result = json.loads(rec.FinalResult())
        full_text += final_result.get("text", "")
        print(f"✅ Transcription completed for {wav_path}")
        return full_text.strip()
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return ""

def download_model_files(repo_id, savedir):
    """Downloads SpeechBrain model files from Hugging Face."""
    files = ["hyperparams.yaml", "embedding_model.ckpt", "label_encoder.txt"]
    os.makedirs(savedir, exist_ok=True)
    for file in files:
        hf_hub_download(repo_id=repo_id, filename=file, local_dir=savedir)
        print(f"✅ Downloaded {file} to {savedir}")

def main():
    """Scrapes and transcribes YouTube videos for real estate analysis."""
    update_yt_dlp()

    csv_path = "city_locality_list.csv"
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return
    df = pd.read_csv(csv_path)
    if "city" not in df.columns or "days" not in df.columns:
        print("❌ CSV must contain 'city' and 'days' columns.")
        return

    output_dir = "test"
    os.makedirs(output_dir, exist_ok=True)
    model_dir = os.path.join(output_dir, "speechbrain_model")
    temp_dir = os.path.join(output_dir, "temp")
    transcripts_dir = "transcripts"
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(transcripts_dir, exist_ok=True)

    repo_id = "speechbrain/lang-id-voxlingua107-ecapa"
    print(f"🔄 Downloading SpeechBrain model files...")
    download_model_files(repo_id, model_dir)
    language_id = EncoderClassifier.from_hparams(source=model_dir)
    print("✅ Language identification model loaded.")

    accepted_languages = {"en", "hi", "te", "gu"}
    language_to_model = {
        "en": VOSK_MODEL_EN,
        "hi": VOSK_MODEL_HI,
        "te": VOSK_MODEL_TE,
        "gu": VOSK_MODEL_GU,
    }
    for lang, path in language_to_model.items():
        if not os.path.exists(path):
            print(f"⚠️ Warning: Vosk model path for '{lang}' not set or does not exist: {path}. Update in script.")

    transcription_paths = []
    for index, row in df.iterrows():
        city = row["city"] + " real estate market"
        days = int(row["days"])
        max_results = 200

        print(f"\n▶ Processing City: {city} with days: {days}")
        results = search_youtube(city, max_results)
        filtered_videos = filter_videos(results, days, min_duration=50)

        if not filtered_videos:
            print(f"❌ No suitable videos found for {city}.")
            transcription_paths.append("")
            continue

        final_transcripts = []
        languages = []
        for idx, vid in enumerate(filtered_videos, start=1):
            print(f"\n▶ Processing Video #{idx}: {vid.get('title')}")
            downloaded_audio = download_audio(vid, output_dir)
            if not downloaded_audio:
                continue

            wav_path = os.path.join(output_dir, f"audio_{index}_{idx}.wav")
            converted_wav = convert_to_wav(downloaded_audio, wav_path)
            if not converted_wav:
                continue

            language = identify_language(wav_path, language_id, temp_dir)
            if language not in accepted_languages:
                print(f"❌ Language '{language}' not in accepted list (en, hi, te, gu). Skipping.")
                if os.path.exists(wav_path):
                    os.remove(wav_path)
                continue

            languages.append(language)
            model_dir_vosk = language_to_model.get(language)
            transcript_text = transcribe_vosk(wav_path, model_dir_vosk)
            if transcript_text:
                final_transcripts.append(f"==== Video {idx} ({language}) ====\n{transcript_text}\n")

            if os.path.exists(wav_path):
                os.remove(wav_path)
            if os.path.exists(downloaded_audio):
                os.remove(downloaded_audio)

        if final_transcripts:
            transcript_filename = f"{sanitize_filename(city)}_transcript.txt"
            transcript_path = os.path.join(transcripts_dir, transcript_filename)
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write("\n".join(final_transcripts))
            print(f"✅ Transcript saved to: {transcript_path}")
            transcription_paths.append(transcript_path)
        else:
            print(f"❌ No transcripts generated for {city}.")
            transcription_paths.append("")

        for temp_file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, temp_file))

    df["transcription_path"] = transcription_paths
    df.to_csv(csv_path, index=False)
    print(f"✅ Updated CSV with transcription paths: {csv_path}")

    if not os.listdir(temp_dir):
        os.rmdir(temp_dir)

if __name__ == "__main__":
    main()
