# data from 'https://raw.githubusercontent.com/jesse-a-l-hamer/chord_progression_assistant/refs/heads/master/three_chord_songs.csv'
import numpy as np
import pandas as pd

from utils.parse_config import config

EXCLUDE_ALL_MINOR = False   
EXCLUDE_MORE_THAN_4CHORDS_PER_SONG = True
USE_SET_NOT_SEQUENCE = False
USE_TEMPO = True
LIST_OF_PROBLEMATIC_SONGS_TO_EXCLUDE = [
    'new romantics', 'shake it off', 'ho hey', 
    'always online', 'take me home country roads', 'dear darlin', 
    'unsteady', 'seven nation army',
]
MAX_COLS = 6

metadata_output_file = config['METADATA_YT_OUTPUT_FILE']

# Function to generate chord progression based on pitch class and mode
def get_chord_progression(sequence, key, mode):

    pitch_class_to_note = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    roman_numerals = sequence.split(',')
    key = int(key)  # Convert key to integer for pitch-class indexing

    chords = []
    for numeral in roman_numerals:
        degree = int(numeral) - 1  # Convert Roman numeral to index (1-based to 0-based)
        assert degree <= 6
        assert degree <= len ([0, 2, 4, 5, 7, 9, 11])
        root_pitch = (key + [0, 2, 4, 5, 7, 9, 11][degree]) % 12  # Calculate pitch class

        # Determine chord type (major/minor/diminished)
        chord_root = pitch_class_to_note[root_pitch]
        chord_type = "m"
        if mode == 1 and degree+1 in [1,4,5] or mode == 0 and degree+1 in [3,6,7]:
            chord_type = ""
        elif mode == 1 and degree+1 in [7] or mode == 0 and degree+1 in [2]:
            chord_type = "d"

        chords.append(f"{chord_root}{chord_type}")

    return chords


def get_chord_progression_per_row(row):
    qualified_chords = get_chord_progression(row['cp'], row['key'], row['mode'])
    return qualified_chords


def is_valid_list(value):
    try:
        # Split the string into parts, convert to integers, and check conditions
        integers = [int(x) for x in value.split(',')]
        if all(i < 8 for i in integers):
            return True
    except (ValueError, AttributeError):
        # ValueError: Non-integer value in the string
        # AttributeError: Input is not a string
        return False
    return False


def key_in_text(key):
    pitch_class_to_note = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return pitch_class_to_note[int(key)]


if __name__ == "__main__":
    # A 4 chord pattern does not mean the song only has these 4 chords. Further filter is required
    df = pd.read_csv('data/four_chord_songs.csv', sep=',')

    # Concatenate the `cp` column for combinations of `artist`, `song`, and `section`
    df_combined_per_section = (
        df.groupby(['artist', 'song', 'section'])['cp']
        .apply(lambda x: set(','.join(x)))
        .reset_index()
    )

    df_merge = pd.merge(df, df_combined_per_section, on=['artist', 'song', 'section'], how='left')
    less_than_5_chords_per_section = df_merge.cp_y.apply(lambda x: len(x) <=5)
    df = df[less_than_5_chords_per_section].reset_index(drop=True)

    if EXCLUDE_MORE_THAN_4CHORDS_PER_SONG:
        df_combined_per_song = (
            df.groupby(['artist', 'song'])['cp']
            .apply(lambda x: set(','.join(x)))
            .reset_index()
        )

        df_merge = pd.merge(df, df_combined_per_song, on=['artist', 'song'], how='left')
        less_than_5_chords_per_song = df_merge.cp_y.apply(lambda x: len(x) <=5)
        df = df[less_than_5_chords_per_song]

    # Filter NaN
    df = df[~df['key'].isna() & ~df['mode'].isna()]

    df = df[df['cp'].apply(is_valid_list)]


    df = df[~df.song.isin(LIST_OF_PROBLEMATIC_SONGS_TO_EXCLUDE)]

    df['chords'] = df.apply(
        lambda row: get_chord_progression(row['cp'], row['key'], row['mode']),
        axis=1
    )
    if EXCLUDE_ALL_MINOR:
        mask_outliers = df['chords'].apply(lambda x: sum(1 for chord in x if 'm' in chord)==4)
        df = df[~mask_outliers]

    df['chord_set'] = df['chords'].apply(lambda x: set(x))
    column_with_chords = 'chords'
    if USE_SET_NOT_SEQUENCE:
        column_with_chords = 'chord_set'

    if EXCLUDE_MORE_THAN_4CHORDS_PER_SONG:
        df = df.drop_duplicates(subset=['mode', 'key', 'song', 'artist'], keep='first')
        df['section'] = ''
        df = df.reset_index(drop=True)

    df['key'] = df['key'].apply(key_in_text)
    df['mode'] = df['mode'].apply(lambda x: 'm' if x == 0 else '')
    df['key'] = df['key'] + df['mode']
    df_metadata = df.loc[:,['chords','cp','key', 'section', 'song', 'artist', 'tempo']]
    if EXCLUDE_MORE_THAN_4CHORDS_PER_SONG:
        df_metadata = df_metadata.drop(columns='section')
    print(df_metadata)

    extra_columns = ['chords_list', 'youtube_id', 'chords_set', 'work_id']
    for column_name in extra_columns:
        df_metadata[column_name] = ''

    #df_metadata.to_csv('data/metadata_yt_out_input.csv', sep='\t', index=False)
df_metadata_input = df_metadata
df_metadata_input.chords = df_metadata_input.chords.astype(str)
print(df_metadata_input.chords.dtype)

df_metadata_out = pd.read_csv(metadata_output_file, sep='\t')

# Calculate and print the number of rows that are different when comparing the two dataframes

N = min(df_metadata_input.shape[0], df_metadata_out.shape[0])

num_different_rows = (df_metadata_input.iloc[:N, :MAX_COLS] != df_metadata_out.iloc[:N, :MAX_COLS]).any(axis=1).sum()
print(f"Number of different rows: {num_different_rows}")

# if num_different_rows > 0, print the rows that are different
if num_different_rows > 0:  
    mask_different_rows = (df_metadata_input.iloc[:N, :MAX_COLS] != df_metadata_out.iloc[:N, :MAX_COLS]).any(axis=1)
    print(df_metadata_input.iloc[:N, :MAX_COLS][mask_different_rows])
    print(df_metadata_out.iloc[:N, :MAX_COLS][mask_different_rows])


# assert that the two dataframes are identical for the first 6 columns
assert df_metadata_input.iloc[:, :MAX_COLS].equals(df_metadata_out.iloc[:, :MAX_COLS])