import pandas as pd
import os

# Define the project name and paths to the files
project = "msc_project"
PROJECTS_DIR = 'data'


def get_project_path(project_name, filename):
    return os.path.join(PROJECTS_DIR, project_name, filename)


INCLUSIONS_FILE = get_project_path(project, 'inclusions.csv')
EXCLUSIONS_FILE = get_project_path(project, 'exclusions.csv')


def read_csv(file_path):
    return pd.read_csv(file_path) if os.path.exists(file_path) else pd.DataFrame()


def save_csv(df, file_path):
    df.to_csv(file_path, index=False)


def concatenate_fields(df):
    df['combined'] = df.apply(lambda row: '_'.join(row.astype(str)), axis=1)
    return df


def move_eid_column(df):
    if 'EID' in df.columns and 'Source' in df.columns:
        # Remove EID from its current location
        eid_column = df.pop('EID')
        # Find the index of the Source column
        source_index = df.columns.get_loc('Source')
        # Insert EID after Source
        df.insert(source_index + 1, 'EID', eid_column)
    return df


# Read the existing inclusions and exclusions files
inclusions_df = read_csv(INCLUSIONS_FILE)
exclusions_df = read_csv(EXCLUSIONS_FILE)

# Move the 'EID' column to right after the 'Source' column
inclusions_df = move_eid_column(inclusions_df)
exclusions_df = move_eid_column(exclusions_df)

# # Add the 'combined' column
# inclusions_df = concatenate_fields(inclusions_df)
# exclusions_df = concatenate_fields(exclusions_df)

# Save the updated DataFrames back to the files
save_csv(inclusions_df, INCLUSIONS_FILE)
save_csv(exclusions_df, EXCLUSIONS_FILE)

print(f"Updated {INCLUSIONS_FILE} moved 'EID' column.")
print(f"Updated {EXCLUSIONS_FILE} moved 'EID' column.")
