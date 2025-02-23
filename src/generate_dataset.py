from utils.yt_utils import yt_crawler
from utils.convert_mp3_to_mono_wav_16k import convert_mp3_to_mono_wav_16k
from utils.get_dataset_from_audio_folder import get_dataset_from_audio_folder
import os
from utils.parse_config import config


if __name__ == "__main__":
     # Download the audio files from youtube to $MP3_FOLDER
    yt_crawler()

    # Convert the mp3 files from $MP3_FOLDER to mono wav files at 16kHz into $WAV_FOLDER. It uses ffmpeg.
    convert_mp3_to_mono_wav_16k()

    # Prepare the wav folder to be used by CoverHunterMPS to extract features
    get_dataset_from_audio_folder() 

    # Copy the hparams.yaml file to the wav folder
    os.system(f"cp {config['COVERHUNTER_FOLDER']}/data/covers80_testset/hparams.yaml {config['WAV_FOLDER']}")
