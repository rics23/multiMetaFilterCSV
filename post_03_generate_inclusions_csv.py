from auxiliary_01 import *

project = "phd_litreview1"

inclusions_file = get_project_path(project, 'inclusions.csv')
new_inclusions_file = get_project_path(project, 'filtered_inclusions.csv')

inclusions_df = read_csv(inclusions_file) if os.path.exists(inclusions_file) else pd.DataFrame()

subset_fields = ['Authors', 'Title', 'Document Title', 'DOI', 'Inclusion_Importance']

filtered_df = inclusions_df[subset_fields]

if 'Inclusion_Importance' in filtered_df.columns:
    filtered_df = filtered_df.sort_values(by='Inclusion_Importance', ascending=False)

save_csv(filtered_df, new_inclusions_file)
