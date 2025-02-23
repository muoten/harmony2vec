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
    # Get embeddings from the features
    print(f"Getting embeddings from the features in {WAV_FOLDER}")
    command = f"PYTHONPATH={COVERHUNTER_FOLDER} python {COVERHUNTER_FOLDER}/tools/make_embeds.py {WAV_FOLDER} {MODEL_FOLDER}"
    if IS_DEBUG:
        print(command)
    else:
        os.system(command)


if __name__ == "__main__":
    get_embeddings_with_coverhunter()