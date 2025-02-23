from generate_dataset import generate_dataset
from get_embeddings_with_coverhunter import get_embeddings_with_coverhunter
from convert_embeddings_to_csv import convert_embeddings_to_csv
from get_neighbors_to_estimate_precision import get_neighbors_to_estimate_precision
from convert_csv_to_json import convert_csv_to_json


if __name__ == "__main__":
    generate_dataset()
    get_embeddings_with_coverhunter()
    convert_embeddings_to_csv()
    get_neighbors_to_estimate_precision()
    convert_csv_to_json()

