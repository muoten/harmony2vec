import os
import json
import wave
from pydub import AudioSegment
from utils.parse_config import config
from utils.yt_utils import video_exists_in_folder


def get_duration(file_path):
    """Returns duration of audio file in seconds"""
    if file_path.endswith('.wav'):
        with wave.open(file_path, 'r') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            return frames / float(rate)
    elif file_path.endswith('.mp3'):
        audio = AudioSegment.from_mp3(file_path)
        return len(audio) / 1000.0  # Convert milliseconds to seconds
    return 0


def get_dataset_from_audio_folder():
    dataset = []
    audio_dir = os.path.expanduser(config['WAV_FOLDER'])

    for root, _, files in os.walk(audio_dir):
        for file in files:
            if file.endswith(('.wav', '.mp3')):  # Support both WAV and MP3
                #if video_exists_in_folder(file, config['WAV_FOLDER']):
                #    continue
                file_path = os.path.join(root, file)
                duration = get_duration(file_path)
                relative_path = os.path.relpath(file_path, audio_dir)
                song_title = os.path.splitext(file)[0]
                version_info = os.path.basename(root)
                utt_id = f"{version_info}_{song_title}"
                entry = {
                    "perf": utt_id,
                    "wav": file_path,  # Path can be MP3 or WAV
                    "dur_s": duration,
                    "work": song_title,
                    "version": version_info,
                    "work_id": 0,
                }
                dataset.append(entry)

    with open(f'{audio_dir}/dataset.txt', 'w') as f:
        for entry in dataset:
            f.write(json.dumps(entry) + '\n')

    print("dataset.txt has been successfully created!")


if __name__ == "__main__":
    get_dataset_from_audio_folder()
