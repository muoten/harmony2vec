from utils.parse_config import config
import os

IS_DEBUG = False
COVERHUNTER_FOLDER = config['COVERHUNTER_FOLDER']
WAV_FOLDER = config['WAV_FOLDER']
MODEL_FOLDER = config['MODEL_FOLDER']


def get_embeddings_with_coverhunter():
    # Extract features from the wav files
    print(f"Extracting features from the wav files in {WAV_FOLDER}")
    command = f"PYTHONPATH={COVERHUNTER_FOLDER} python {COVERHUNTER_FOLDER}/tools/extract_csi_features.py {WAV_FOLDER}"
    if IS_DEBUG:
        print(command)
    else:
        os.system(command)

    # get number of files with extension .wav in WAV_FOLDER
    num_wav_files = len([f for f in os.listdir(os.path.expanduser(WAV_FOLDER)) if f.endswith('.wav')])
    print(f"Number of .wav files in {WAV_FOLDER}: {num_wav_files}")

    # get number of files with extension .npy in WAV_FOLDER/cqt_feat
    num_npy_files = len([f for f in os.listdir(os.path.join(os.path.expanduser(WAV_FOLDER), 'cqt_feat')) if f.endswith('.npy')])
    print(f"Number of .npy files in {WAV_FOLDER}/cqt_feat: {num_npy_files}")

    # raise error if num_wav_files is not equal to num_npy_files
    if num_wav_files != num_npy_files:
        raise ValueError(f"Number of wav files in {WAV_FOLDER} is not equal to the number of .npy files in {WAV_FOLDER}/cqt_feat")

    # Get embeddings from the features
    print(f"Getting embeddings from the features in {WAV_FOLDER}")
    command = f"PYTHONPATH={COVERHUNTER_FOLDER} python {COVERHUNTER_FOLDER}/tools/make_embeds.py {WAV_FOLDER} {MODEL_FOLDER}"
    if IS_DEBUG:
        print(command)
    else:
        os.system(command)


if __name__ == "__main__":
    get_embeddings_with_coverhunter()