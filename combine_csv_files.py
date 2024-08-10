import os
import pandas as pd


def combine_csv_files(folder_path):
    # Get a list of all CSV files in the folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    # Initialize an empty list to store dataframes
    dataframes = []

    # Read each CSV file and append it to the list
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        dataframes.append(df)

    # Concatenate all dataframes in the list
    combined_df = pd.concat(dataframes, ignore_index=True)

    return combined_df


# Example usage:
folder_path = 'data/msc_project/sources'
combined_df = combine_csv_files(folder_path)

# Optionally, save the combined dataframe to a new CSV file
combined_df.to_csv('data/msc_project/combined_output.csv', index=False)
