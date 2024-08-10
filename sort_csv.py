import pandas as pd


def remove_duplicates_and_sort_csv(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Sort the DataFrame by all columns
    df = df.sort_values(by=list(df.columns))

    df = df.sort_values(by=['DOI'])

    # Save the cleaned DataFrame back to a CSV file
    df.to_csv(output_file, index=False)


# Example usage
input_file = 'data/msc_project/combined_output.csv'
output_file = 'data/msc_project/combined_output_sorted.csv'
remove_duplicates_and_sort_csv(input_file, output_file)

df = pd.read_csv(output_file)

doi = "ricardo"
tab = ""
counter = 0

for index, record in df.iterrows():
    if record['DOI'] == doi:
        tab = "     "
        counter += 1
    else:
        tab = ""
    print(tab, record['DOI'], record['Authors'])
    doi = record['DOI']

print(f"Total number of duplicates: {counter}")