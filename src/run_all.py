from generate_dataset import generate_dataset
from get_embeddings_with_coverhunter import get_embeddings_with_coverhunter
from convert_embeddings_to_csv import convert_embeddings_to_csv
from get_neighbors_to_estimate_precision import get_neighbors_to_estimate_precision
from convert_csv_to_json import convert_csv_to_json
import time
import pandas as pd
from utils.parse_config import config
import os


if __name__ == "__main__":
    # print estimated time to run all the steps
    start_time = time.time()

    generate_dataset()
    get_embeddings_with_coverhunter()
    convert_embeddings_to_csv()
    get_neighbors_to_estimate_precision()
    convert_csv_to_json()

    end_time = time.time()
    print(f"Total time taken: {end_time - start_time} seconds")

    # get number of lines of metadata_${VERSION}.csv and metadata_OLD_VERSION.csv and get the difference to estimate how many new songs were added
    metadata_version = pd.read_csv(os.path.join(os.path.expanduser(config['METADATA_OUTPUT_FILE'])), sep='\t')
    metadata_old_version = pd.read_csv(os.path.join(os.path.expanduser(config['METADATA_OLD_VERSION_FILE'])), sep='\t')
    last_message = (
        "Number of new songs added in last iteration " 
        f"comparing {config['METADATA_OUTPUT_FILE']} and {config['METADATA_OLD_VERSION_FILE']}: "
        f"{len(metadata_version) - len(metadata_old_version)}"
    )
    print(last_message)
