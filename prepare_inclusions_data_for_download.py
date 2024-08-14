import os
import pandas as pd

project = "msc_project"

input_file = os.path.join('data', project, 'inclusions.csv')
output_file = os.path.join('data', project, 'inclusions_filtered.csv')

columns_to_keep = [
    'Authors', 'Title', 'DOI', 'Link', 'EID',
    'Document Title', 'PDF Link', 'Document Identifier'
]

df = pd.read_csv(input_file)

existing_columns = [col for col in columns_to_keep if col in df.columns]
df_filtered = df[existing_columns]

df_filtered.to_csv(output_file, index=False)

print(f"Filtered CSV file saved as '{output_file}' with columns: {existing_columns}")
