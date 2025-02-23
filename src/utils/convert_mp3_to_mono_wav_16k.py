import os
import subprocess
from utils.parse_config import config


def convert_mp3_to_mono_wav_16k():
    # Directory containing MP3 files
    input_dir = os.path.expanduser(config['MP3_FOLDER'])
    # Output directory for WAV files
    output_dir = os.path.expanduser(config['WAV_FOLDER'])

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Loop through all MP3 files in the input directory
    for mp3_file in os.listdir(input_dir):
        if mp3_file.endswith('.mp3'):
            # Extract the base name of the file (without extension)
            base_name = os.path.splitext(mp3_file)[0]
            print(f"Converting {base_name}")
            # Define the output WAV file path
            wav_file = os.path.join(output_dir, f"{base_name}.wav")
            
            # Convert MP3 to WAV with mono audio and 16 kHz sample rate
            subprocess.run(['ffmpeg', '-n','-i', os.path.join(input_dir, mp3_file), '-ac', '1', '-ar', '16000', wav_file])

    print("Conversion complete!")


if __name__ == "__main__":
    convert_mp3_to_mono_wav_16k()