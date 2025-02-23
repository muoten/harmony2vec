import csv
import json
import pandas as pd

import os
from utils.parse_config import config


def merge_metadata_from_dataset():
    WAV_FOLDER = os.path.expanduser(config['WAV_FOLDER'])

    # create metadata.csv using the titles from the dataset.csv file

    metadata_output_file = config['METADATA_OUTPUT_FILE']
    # Path to the dataset CSV file
    dataset_file_path = os.path.join(WAV_FOLDER, 'dataset.txt')

    metadata_yt_output_file = os.path.expanduser(config['METADATA_YT_OUTPUT_FILE'])

    # dataset.txt is a file with a list of dictionaries
    # read the dataset.txt file as a list of dictionaries, one per line

    with open(dataset_file_path, 'r') as f:
        data = [json.loads(line) for line in f]

    prefix_to_remove = config['WAV_FOLDER'].replace('~/', '')

    songs = [d['perf'].replace(prefix_to_remove, '') for d in data]
    duration = [d['dur_s'] for d in data]

    # create a dataframe from the list of dictionaries
    df = pd.DataFrame({'title': songs, 'duration': duration})

    # get youtube_id from the title, between the first '_' and the first '__'
    df['youtube_id'] = df['title'].str.extract(r'_(.*?)__')
    print(df['youtube_id'].head())

        # if df contains any duplicate in colum title, raise an error
    if df['title'].duplicated().any():
        # in error message, print the duplicate titles
        raise ValueError(f"metadata contains duplicate titles: {df[df['title'].duplicated()]['title'].unique()}")

    # read the old metadata file
    metadata_yt = pd.read_csv(metadata_yt_output_file, sep='\t')
    # merge df and old_metadata on youtube_id
    df = pd.merge(df, metadata_yt, on='youtube_id', how='left')


    print(df.head())
    df = df.fillna('')
    # convert chords_set to a string
    # Convert chords_set to a string, ensuring it's a comma-separated list
    df['chords_set'] = df['chords_set'].apply(lambda x: f'"{x}"')

    # write the dataframe to a csv file
    df.to_csv(metadata_output_file, index=False, sep='\t')


    print(f"Metadata CSV created at {metadata_output_file}")

    # print the value_counts() of chords_set
    print(df['chords_set'].value_counts())
    print(df['chords_list'].value_counts())




