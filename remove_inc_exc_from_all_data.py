import pandas as pd

# Read the CSV files
all_data = pd.read_csv('data/msc_project/all_data.csv')
inclusions = pd.read_csv('data/msc_project/inclusions.csv')
exclusions = pd.read_csv('data/msc_project/exclusions.csv')
duplicates = pd.read_csv('data/msc_project/duplicates.csv')

# Convert inclusions and exclusions to sets of DOIs for quick lookup
inclusion_dois = set(inclusions['DOI'].dropna())
exclusion_dois = set(exclusions['DOI'].dropna())

# Convert inclusions and exclusions to sets of tuples for row comparison
inclusion_rows = set([tuple(row) for row in inclusions.to_numpy()])
exclusion_rows = set([tuple(row) for row in exclusions.to_numpy()])


# Function to check if a record is in inclusion or exclusion
def is_duplicate(record):
    doi = record.get('DOI')
    if pd.notna(doi) and (doi in inclusion_dois or doi in exclusion_dois):
        return True
    record_tuple = tuple(record)
    if record_tuple in inclusion_rows or record_tuple in exclusion_rows:
        return True
    return False


# Initialize a list to store new duplicate records
new_duplicates = []

# Iterate over all_data and check for duplicates
for idx, record in all_data.iterrows():
    if is_duplicate(record):
        new_duplicates.append(record)

# Create a DataFrame for new duplicates and remove them from all_data
new_duplicates_df = pd.DataFrame(new_duplicates)
all_data = all_data[~all_data.index.isin(new_duplicates_df.index)]

# Combine new duplicates with existing duplicates
duplicates = pd.concat([duplicates, new_duplicates_df])

# Write the updated all_data and duplicates to their respective CSV files
all_data.to_csv('data/msc_project/all_data.csv', index=False)
duplicates.to_csv('data/msc_project/duplicates.csv', index=False)
