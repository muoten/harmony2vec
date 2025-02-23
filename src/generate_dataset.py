from utils.yt_utils import yt_crawler
from utils.convert_mp3_to_mono_wav_16k import convert_mp3_to_mono_wav_16k
from utils.get_dataset_from_audio_folder import get_dataset_from_audio_folder
import os
from utils.parse_config import config


def generate_dataset():
    # Download the audio files from youtube to $MP3_FOLDER
    if not os.path.exists(config['METADATA_YT_OUTPUT_FILE']):
        yt_crawler()

    # Convert the mp3 files from $MP3_FOLDER to mono wav files at 16kHz into $WAV_FOLDER. It uses ffmpeg.
    convert_mp3_to_mono_wav_16k()

    # Prepare the wav folder to be used by CoverHunterMPS to extract features
    get_dataset_from_audio_folder() 


    # if file $WAV_FOLDER/full.txt exists and its number of lines is not coincident with lines in $WAV_FOLDER/dataset.txt, remove
    for file in ['full.txt', 'sp_aug.txt']:
        if os.path.exists(os.path.join(config['WAV_FOLDER'], file)):
            if len(open(os.path.join(config['WAV_FOLDER'], file)).readlines()) != len(open(os.path.join(config['WAV_FOLDER'], 'dataset.txt')).readlines()):
                os.remove(os.path.join(config['WAV_FOLDER'], file))

    # Copy the hparams.yaml file to the wav folder
    os.system(f"cp {config['COVERHUNTER_FOLDER']}/data/covers80_testset/hparams.yaml {config['WAV_FOLDER']}")


if __name__ == "__main__":
    generate_dataset() 