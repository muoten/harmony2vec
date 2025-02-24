import pickle
import csv
from sklearn.decomposition import PCA
import pandas as pd
from utils.parse_config import config
import os
from utils.merge_metadata_from_dataset import merge_metadata_from_dataset


def convert_embeddings_to_csv():

     # First, merge the metadata from the dataset.txt file to be used to convert the embeddings to a csv file
    merge_metadata_from_dataset()

    wav_folder = os.path.expanduser(config['WAV_FOLDER'])
    # Path to the pickle file
    pickle_file_path = os.path.join(wav_folder, 'reference_embeddings.pkl')

    # Path to the output CSV file
    csv_file_path =  config['VECTOR_OUTPUT_FILE']

    # read metadata.csv
    metadata_file_path = config['METADATA_OUTPUT_FILE']
    metadata = pd.read_csv(metadata_file_path, sep='\t')

    # if metadata contains any duplicate in colum title, raise an error
    if metadata['title'].duplicated().any():
        # in error message, print the duplicate titles
        raise ValueError(f"metadata contains duplicate titles: {metadata[metadata['title'].duplicated()]['title'].unique()}")

    # Load the embeddings from the pickle file
    with open(pickle_file_path, 'rb') as f:
        reference_embeddings = pickle.load(f)

    # get the number of keys in the reference_embeddings dictionary
    num_keys = len(reference_embeddings)
    print(f"Number of keys in the reference_embeddings dictionary: {num_keys}")

    # Convert the dictionary to a DataFrame
    reference_embeddings_df = pd.DataFrame.from_dict(reference_embeddings, orient='index')

    # Reset the index to have the keys as a column
    reference_embeddings_df = reference_embeddings_df.reset_index()

    # rename column index to title
    reference_embeddings_df = reference_embeddings_df.rename(columns={'index': 'title'})
    prefix_to_remove = config['WAV_FOLDER'].replace('~/', '')
    reference_embeddings_df['title'] = reference_embeddings_df['title'].str.replace(prefix_to_remove, '')

    # rename columns by converting them to strings first
    reference_embeddings_df = reference_embeddings_df.rename(
        columns=lambda x: f'embedding_dim_{x}' if str(x).isdigit() else x
    )

    # merge metadata with embeddings by title
    merged_data = pd.merge(metadata, reference_embeddings_df, on='title', how='left')

    # get embeddings from merged_data columns embedding_dim_0 to embedding_dim_127

    embeddings_list = merged_data.iloc[:, 13:].values

    # check embeddings_list has the same number of rows as num_keys
    if embeddings_list.shape[0] != num_keys:
        raise ValueError(f"embeddings_list has {embeddings_list.shape[0]} rows, but num_keys is {num_keys}")

    # Apply PCA to reduce dimensionality to 20
    pca = PCA(n_components=49)
    reduced_embeddings = pca.fit_transform(embeddings_list)
    #reduced_embeddings = embeddings_list

    # Write the reduced vectors to a CSV file using tab as the separator
    with open(csv_file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter='\t')
        
        # Write each reduced embedding as a row in the CSV
        for reduced_embedding in reduced_embeddings:
            writer.writerow(reduced_embedding)

    print(f"Reduced vectors CSV created at {csv_file_path}")

    # postprocess the csv files to remove empty chords
    postprocess_csvs_to_remove_empty_chords(os.path.expanduser(config['METADATA_OUTPUT_FILE']), os.path.expanduser(config['VECTOR_OUTPUT_FILE']))



def postprocess_csvs_to_remove_empty_chords(csv_metadata_file_path, csv_vectors_file_path):
    # read metadata.csv
    metadata = pd.read_csv(csv_metadata_file_path, sep='\t')
    # read vectors.csv
    vectors = pd.read_csv(csv_vectors_file_path, sep='\t', header=None)

    # Check for empty strings, whitespace-only strings, NaN, or None in 'chords_set'
    mask_null = metadata['chords_set'].apply(lambda x: (isinstance(x, str) and x.strip() == '""') or pd.isna(x) or x is None)
        
    # remove from metadata the rows where mask_null is True
    metadata = metadata[~mask_null]
    # remove from vectors the rows where mask_null is True
    vectors = vectors[~mask_null]

    # write metadata to csv
    metadata.to_csv(csv_metadata_file_path, sep='\t', index=False)
    # write vectors to csv
    vectors.to_csv(csv_vectors_file_path, sep='\t', index=False, header=False)
    # print the number of rows in the metadata and vectors after postprocessing
    print(f"Number of rows in the metadata after postprocessing to remove empty chords: {metadata.shape[0]}")
    print(f"Number of rows in the vectors after postprocessing to remove empty chords: {vectors.shape[0]}")
       
        

if __name__ == "__main__":
    # Then, convert the embeddings to a csv file
    convert_embeddings_to_csv() 



