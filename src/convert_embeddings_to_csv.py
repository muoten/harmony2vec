import pickle
import csv
from sklearn.decomposition import PCA
import pandas as pd
from utils.parse_config import config
import os
from utils.merge_metadata_from_dataset import merge_metadata_from_dataset


def convert_embeddings_to_csv():
    wav_folder = os.path.expanduser(config['WAV_FOLDER'])
    # Path to the pickle file
    pickle_file_path = os.path.join(wav_folder, 'reference_embeddings.pkl')

    # Path to the output CSV file
    csv_file_path =  config['VECTOR_OUTPUT_FILE']

    # read metadata.csv
    metadata_file_path = config['METADATA_OUTPUT_FILE']
    metadata = pd.read_csv(metadata_file_path, sep='\t')

    # Load the embeddings from the pickle file
    with open(pickle_file_path, 'rb') as f:
        reference_embeddings = pickle.load(f)

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

    embeddings_list = merged_data.iloc[:, 11:].values

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


if __name__ == "__main__":

    # First, merge the metadata from the dataset.txt file to be used to convert the embeddings to a csv file
    merge_metadata_from_dataset()
    # Then, convert the embeddings to a csv file
    convert_embeddings_to_csv()


