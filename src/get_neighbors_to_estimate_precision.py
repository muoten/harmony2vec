# open vectors.csv
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import re
import random
from utils.parse_config import config
from statsmodels.stats.proportion import proportions_ztest


IS_DEBUG = True
N_NEIGHBORS = 1

# set the seed for the random number generator
random.seed(42)

# if IS_DEBUG is False, disable the print statements except for the final one
if not IS_DEBUG:
    print_force = print
    print = lambda *args, **kwargs: None
else:
    print_force = print

# Function to clean and convert chords_set to a frozenset
def clean_chords_set(chords_set_str):
    # Remove unwanted characters and split by comma
    cleaned_str = re.sub(r"[{}'\"]", "", chords_set_str)  # Remove curly braces and quotes
    chords_list = cleaned_str.split(',')
    # Strip whitespace and filter out empty strings
    chords_list = [chord.strip() for chord in chords_list if chord.strip()]
    # Convert to frozenset for consistent comparison
    return frozenset(chords_list)

# Define a function to find the nearest neighbors
def find_neighbors(vector, nbrs):
    distances, indices = nbrs.kneighbors([vector])
    print(distances)
    print(indices)
    return indices[0]


def cosine_distance(vec1, vec2):
    from numpy import dot
    from numpy.linalg import norm
    return 1 - dot(vec1, vec2) / (norm(vec1) * norm(vec2))


def estimate_statistical_significance(hits, random_hits, total, total_random):
    # Data for binomial 1
    hits1 = hits
    total1 = total

    # Data for binomial 2
    hits2 = random_hits
    total2 = total_random

    # Perform the two-proportion z-test
    count = [hits1, hits2]
    nobs = [total1, total2]
    stat, p_value = proportions_ztest(count, nobs, alternative='larger')

    print("Z-statistic:", stat)
    print("P-value:", p_value)

    # Interpretation
    alpha = 0.05  # Significance level
    if p_value < alpha:
        print("Reject the null hypothesis: Binomial 1 proportion is greater than Binomial 2 proportion.")
    else:
        print("Fail to reject the null hypothesis: No evidence that Binomial 1 proportion is greater.")


def get_neighbors_to_estimate_precision():
    metadata = pd.read_csv(config['METADATA_OUTPUT_FILE'], sep='\t')

    vectors = pd.read_csv(config['VECTOR_OUTPUT_FILE'], sep='\t', header=None)

    # Check for empty strings, whitespace-only strings, NaN, or None in 'chords_set'
    mask_null = metadata['chords_set'].apply(lambda x: (isinstance(x, str) and x.strip() == '""') or pd.isna(x) or x is None)
    # remove from metadata the rows where mask_null is True
    metadata = metadata[~mask_null]
    # remove from vectors the rows where mask_null is True
    vectors = vectors[~mask_null]



    # Apply the cleaning function to the chords_set column
    metadata['chords_set'] = metadata['chords_set'].apply(clean_chords_set)


    # Convert the vectors DataFrame to a numpy array
    vectors_array = vectors.to_numpy()

    # Create a NearestNeighbors model
    nbrs = NearestNeighbors(n_neighbors=N_NEIGHBORS+1, algorithm='brute', metric='cosine').fit(vectors_array)


    hits = 0
    random_hits = 0

    for target_vector_index, vector in enumerate(vectors_array):    
        # print the row of metadata file corresponding to the target vector {target_vector_index}

        print(f"Target vector {target_vector_index}:")
        print(metadata.iloc[target_vector_index:target_vector_index+1])
        print(vectors_array[target_vector_index])


        # find the neighbors of the first vector
        neighbors = find_neighbors(vectors_array[target_vector_index], nbrs)
        # exclude the first neighbor, which is the vector itself
        neighbors = neighbors[1:]

        # also get cosine distance between the target vector and each of the neighbors
        source_vector = vectors_array[target_vector_index]
        print(source_vector)
        destination_vector1 = vectors_array[neighbors[0]]
        
        print(destination_vector1)
        distance1 = cosine_distance(source_vector, destination_vector1)
        print(f"Distance between target vector and first neighbor: {distance1}")

        # print the rows from the metadata file that have the same number of row as the neighbors
        print("Neighbors:")
        print(metadata.iloc[neighbors])

        # get the chords_set from the target vector
        target_chords_set = metadata.iloc[target_vector_index]['chords_set']

        # how many neighbors have the same chords_set as the target vector
        sum = (metadata.iloc[neighbors]['chords_set']==target_chords_set).sum()
        print(f"Number of neighbors with the same chords_set as the target vector: {sum}")
        hits += sum

        # get a list of N_NEIGHBORS elements random to act as baselines
        baselines = random.sample(range(len(metadata)), N_NEIGHBORS*10)
        baselines = [baseline for baseline in baselines if baseline != target_vector_index]
        if len(baselines) < N_NEIGHBORS*10:
            baselines.extend(random.sample(range(len(metadata)), N_NEIGHBORS*10 - len(baselines)))
        print_force(f"Baselines: {baselines}")

        # how many random baselines have the same chords_set as the target vector
        sum = (metadata.iloc[baselines]['chords_set']==target_chords_set).sum()
        print(f"Number of random baselines with the same chords_set as the target vector: {sum}")
        random_hits += sum
        
    total = len(vectors_array) * N_NEIGHBORS
    total_random = len(vectors_array) * N_NEIGHBORS*10

    # force print the final result even if IS_DEBUG is False
    print_force(f"{hits} hits out of {total}. So {hits/total*100:.1f}%")    
    print_force(f"{random_hits} random hits out of {total_random}. So {random_hits/total_random*100:.1f}%")
    estimate_statistical_significance(hits, random_hits, total, total_random)


if __name__ == "__main__":
    get_neighbors_to_estimate_precision()


