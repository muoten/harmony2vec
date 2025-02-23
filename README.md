# harmony2vec
Audio embeddings for music similarity search

## Requirements

- It uses [CoverHunterMPS](https://github.com/alanngnet/CoverHunterMPS) to extract embeddings from audio files, downloaded on folder `$COVERHUNTER_FOLDER`.

    `git clone https://github.com/alanngnet/CoverHunterMPS`
     A pretrained model is required in `$MODEL_FOLDER`
- `ffmpeg` is used to covert the audio files
- Install dependencies with `pip install -r requirements.txt`

## Usage

### Step by step
- 1. Run `python src/generate_dataset.py` to download the audio files from youtube to `$MP3_FOLDER`, convert them to mono wav files at 16kHz into `$WAV_FOLDER`, prepare the wav folder to be used by CoverHunterMPS to extract features and copy the hparams.yaml file to the wav folder
- 2. Run `python src/get_embeddings_with_coverhunter.py` to get embeddings from the wav files after generating the features with CoverHunterMPS
- 3. Run `python src/convert_embeddings_to_csv.py` to convert the embeddings to a csv file
- 4. Run `python src/get_neighbors_to_estimate_precision.py` to estimate the precision of the model to get closest neighbors with same chords
- 5. Run `python src/convert_csv_to_json.py` to convert the csv files to a json file compliant with Milvus vector database

### All in one

- Run `python src/run_all.py` to run all the steps above