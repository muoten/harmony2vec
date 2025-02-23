from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import re
import time
import pandas as pd
import ast
import os
import glob
import shutil

from utils.parse_config import config

METADATA_YT_INPUT_FILE = config['METADATA_YT_INPUT_FILE']
METADATA_YT_OUTPUT_FILE = config['METADATA_YT_OUTPUT_FILE']


def video_exists_in_folder(video_id, mp3_folder):
    """
    Check if any file in mp3_folder starts with video_id
    
    Args:
        video_id (str): YouTube video ID to check
        mp3_folder (str): Path to the MP3 folder
    
    Returns:
        bool: True if a matching file exists, False otherwise
    """
    # Search pattern for any file starting with video_id
    search_pattern = os.path.join(os.path.expanduser(mp3_folder), f"{video_id}*")
    
    # Use glob to find any matching files
    matching_files = glob.glob(search_pattern)
    
    return len(matching_files) > 0


def crawl_video_for_song(driver, artist, title):
    artist = artist.replace(' ', '-').replace('\'', '')
    title = title.replace(' ', '-').replace('\'', '')
    youtube_id = None
    try:
        # Step 1: Go to the Hooktheory chord progression search page
        url = f"https://www.hooktheory.com/theorytab/view/{artist}/{title}"
        driver.get(url)
        time.sleep(3)
        # Step 2: Locate the iframe

        # Find the iframe by its ID
        iframe = driver.find_element(By.ID, "hookpad-youtube-player")

        # Step 3: Switch to the iframe context
        driver.switch_to.frame(iframe)

        # Step 4: Extract all <a> elements inside the iframe, then filter by class
        links = driver.find_elements(By.CSS_SELECTOR, "a")
        target_class = "ytp-watermark yt-uix-sessionlink"
        links = [link for link in links if target_class in link.get_attribute("class")]

        # Step 5: Filter and extract YouTube identifiers
        youtube_ids = []
        for link in links:
            href = link.get_attribute("href")
            if href and "youtube.com/watch" in href:  # Ensure it's a YouTube link
                match = re.search(r"v=([a-zA-Z0-9_-]+)", href)
                if match:
                    youtube_ids.append(match.group(1))  # Extract YouTube video ID

        # Print the extracted YouTube IDs
        print("YouTube Identifiers:")
        print(youtube_ids)
        youtube_id = youtube_ids[0]
    except:
        pass

    return youtube_id


def yt_crawler():
    youtube_ids = []
    df = pd.read_csv(METADATA_YT_INPUT_FILE, sep='\t')

    target_chords = {'C', 'G', 'Am', 'F'}
    target_chords = {'C', 'G', 'Em', 'D'}
    target_chords = {'G#', 'C#', 'D#', 'Fm'}
    target_chords = {'E', 'D', 'F#m', 'A'}
    target_chords = {'A#m', 'D#m', 'C', 'G#m'}
    target_chords = {'C#', 'D#', 'Fm', 'G#'}
    target_chords = {'F#m', 'G#', 'Em', 'Bm'}


    # Convert the 'chords' column to actual lists and filter rows
    df['chords_list'] = df['chords'].apply(lambda x: ast.literal_eval(x))  # Safely evaluate the string as a list
    
    df['chords_set'] = df['chords'].apply(lambda x: set(ast.literal_eval(x)))
    filtered_df = df[df.chords_set == target_chords]
    filtered_df = filtered_df[filtered_df.youtube_id.isna()]

    n_targets = len(filtered_df)
    print(f"Identified {n_targets} new targets to be crawled")
    if n_targets > 0:
        # Set up the Chrome WebDriver using ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        for song, artist in zip(filtered_df["song"], filtered_df["artist"]):
            youtube_id = crawl_video_for_song(driver, artist, song)
            youtube_ids.append(youtube_id)
        df.loc[filtered_df.index,'youtube_id'] = youtube_ids
        df.to_csv(METADATA_YT_OUTPUT_FILE, index=False, sep='\t')

        # Finally close the browser
        driver.quit()
    else:
        print("No new targets to be crawled")
        # So we copy the existing metadata to the output file
        shutil.copy(METADATA_YT_INPUT_FILE, METADATA_YT_OUTPUT_FILE)

    videos_to_download = list(df[~df.youtube_id.isna()].youtube_id)

    os.system(f'mkdir -p {config["MP3_FOLDER"]}')
    command_base = f"yt-dlp -x --audio-format mp3 --add-metadata -o '{config['MP3_FOLDER']}/%(title)s.%(ext)s' -- "
    for video_id in videos_to_download:
        if not video_exists_in_folder(video_id, config["MP3_FOLDER"]):
            to_be_replaced = f"{config['MP3_FOLDER']}/"
            replacement = f"{to_be_replaced}{video_id}__"
            command = command_base.replace(to_be_replaced, replacement)
            full_command = f"{command}{video_id}"
            print(full_command)
            os.system(full_command)
        else:
            print(f"Video {video_id} already exists in MP3 folder, skipping...")
