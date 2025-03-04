import time
import os
import html
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def setup_driver():
    """Sets up Selenium WebDriver with Chrome."""
    options = Options()
    options.add_argument("--lang=en")
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def create_html_page(text, html_path):
    """Converts a text file into an HTML file for Chrome translation."""
    html_content = f"""
    <html lang="hi">
    <head><meta charset="UTF-8"></head>
    <body><div id="text-to-translate">{html.escape(text)}</div></body>
    </html>
    """
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

def translate_text(driver, html_path):
    """Opens the HTML file in Chrome and translates to English."""
    driver.get("file://" + os.path.abspath(html_path))
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "text-to-translate"))
        )
        ActionChains(driver).context_click(element).perform()
        time.sleep(2)
        for _ in range(8):
            pyautogui.press('down')
            time.sleep(0.1)
        pyautogui.press('enter')
        time.sleep(10)
        translated_element = driver.find_element(By.ID, "text-to-translate")
        return translated_element.text
    except Exception as e:
        print(f"❌ Translation failed: {e}")
        return None

def translate_text_file(input_txt, output_txt):
    """Translates a text file to English using Chrome."""
    driver = setup_driver()
    html_path = "temp.html"
    try:
        with open(input_txt, "r", encoding="utf-8") as f:
            original_text = f.read()
        print(f"🔄 Creating HTML file for translation: {input_txt}")
        create_html_page(original_text, html_path)
        print(f"🔄 Translating: {input_txt}")
        english_text = translate_text(driver, html_path)
        if english_text:
            with open(output_txt, "w", encoding="utf-8") as f:
                f.write(english_text)
            print(f"✅ Translation saved to: {output_txt}")
            return output_txt
        else:
            print(f"❌ Translation failed for {input_txt}.")
            return None
    finally:
        driver.quit()
        if os.path.exists(html_path):
            os.remove(html_path)

def main():
    """Processes transcripts for translation."""
    transcripts_dir = "transcripts"
    translated_dir = "translated"
    csv_path = "city_locality_list.csv"
    os.makedirs(translated_dir, exist_ok=True)

    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return
    df = pd.read_csv(csv_path)
    if "transcription_path" not in df.columns:
        print("❌ CSV must contain 'transcription_path' column.")
        return

    translated_paths = []
    for index, row in df.iterrows():
        input_txt = row["transcription_path"]
        if not input_txt or not os.path.exists(input_txt):
            print(f"⚠️ Skipping row {index}: '{input_txt}' invalid.")
            translated_paths.append("")
            continue
        filename = os.path.basename(input_txt)
        output_txt = os.path.join(translated_dir, filename)
        print(f"\n▶ Translating: {input_txt}")
        translated_path = translate_text_file(input_txt, output_txt)
        translated_paths.append(translated_path if translated_path else "")

    df["translated_path"] = translated_paths
    df.to_csv(csv_path, index=False)
    print(f"✅ Updated CSV with translated paths: {csv_path}")

if __name__ == "__main__":
    main()
