# A tool for streamlining systematic literature reviews, combining CSV
# projects from diverse databases, standardising results on a local web page
# for efficient duplicate detection, inclusion/exclusion tracking, and
# PRISMA-aligned visualisations and supporting files.
# Copyright (C) 2024  Ricardo Lopes  rics.23@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import pandas as pd
import matplotlib.pyplot as plt
from upsetplot import UpSet, from_memberships
from venn import venn

PROJECTS_DIR = 'projects'
projects = [name for name in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, name))]


def get_project_path(project_name, filename):
    return os.path.join(PROJECTS_DIR, project_name, filename)


def read_csv(file_path):
    return pd.read_csv(file_path) if os.path.exists(file_path) else pd.DataFrame()


def save_csv(df, file_path):
    print(f"Saving {file_path}")
    df.to_csv(file_path, index=False)


# Create UpSet Plot
def plot_upset_plot(venn_diagram_data, filenames, project):
    idx = []
    for f in filenames:
        x = venn_diagram_data.columns.get_loc(f)
        idx.append(x)

    source_columns = venn_diagram_data.columns[idx]

    # Create membership sets for each combination of sources
    memberships = []
    for idx, row in venn_diagram_data.iterrows():
        membership = tuple(col for col in source_columns if row[col] == 1)
        if membership:
            memberships.append(membership)

    # Generate the projects for the UpSet plot
    upset_data = from_memberships(memberships)

    # Plot the UpSet diagram
    upset = UpSet(upset_data, subset_size='count', show_counts='%d', sort_by='cardinality')
    upset.plot()
    plt.title("UpSet Plot for Overlapping Records")
    plt.savefig(get_project_path(project, "upset_plot.png"))


def plot_venn_diagram(venn_diagram_data, filenames, project):
    # Create a dictionary to hold sets of venn_ids for each file
    sets_dict = {}

    for filename in filenames:
        # Get the set of venn_ids where the file column has value 1
        file_set = set(venn_diagram_data.loc[venn_diagram_data[filename] == 1, 'venn_id'])
        sets_dict[filename] = file_set

    # Check if there are more than 6 sets and slice the first 6
    if len(sets_dict) > 6:
        print(f"Warning: More than 6 sets found. Only the first 6 will be plotted.")
        sets_dict = {k: sets_dict[k] for k in list(sets_dict.keys())[:6]}

    # Plot the Venn diagram using the 'venn' package
    venn(sets_dict)

    # Save the Venn diagram plot
    plt.title("Venn Diagram for Overlapping Records")
    plt.savefig(get_project_path(project, "venn_diagram.png"))
    plt.show()
    print(f"Venn Diagram saved as PNG: {get_project_path(project, 'venn_diagram.png')}")


def find_and_move_duplicates(project):
    processed_sources_dir = get_project_path(project, 'processed_sources')
    all_files = [os.path.join(processed_sources_dir, f) for f in os.listdir(processed_sources_dir) if
                 f.endswith('.csv')]

    inclusions_file = get_project_path(project, 'inclusions.csv')
    if os.path.exists(inclusions_file):
        all_files.append(inclusions_file)

    venn_diagram_data = pd.DataFrame(columns=['EID', 'DOI', 'Abstract'])

    filenames = []

    venn_counter = 1

    for file in all_files:
        filename = os.path.splitext(os.path.basename(file))[0]
        filenames.append(filename)
        f = read_csv(file)

        print(f"Processing file: {filename}")

        for idx, record in f.iterrows():
            eid = record.get('EID')
            doi = record.get('DOI')
            abstract = record.get("Abstract")
            record_df = pd.DataFrame([record])

            eid_exists = pd.notna(eid) and venn_diagram_data['EID'].isin([eid]).any()
            doi_exists = pd.notna(doi) and venn_diagram_data['DOI'].isin([doi]).any()
            abstract_exists = pd.notna(abstract) and venn_diagram_data['Abstract'].isin([abstract]).any()

            if eid_exists or doi_exists or abstract_exists:
                if filename not in venn_diagram_data.columns:
                    venn_diagram_data[filename] = 0
                venn_diagram_data.loc[(venn_diagram_data['EID'] == eid) |
                                      (venn_diagram_data['DOI'] == doi) |
                                      (venn_diagram_data['Abstract'] == abstract), filename] += 1
            else:
                record_df['venn_id'] = venn_counter
                venn_counter += 1
                record_df[filename] = 1
                venn_diagram_data = pd.concat([venn_diagram_data, record_df], ignore_index=True)

    save_csv(venn_diagram_data, 'dev_local/venn_diagram_data.csv')

    # Generate the UpSet plot after processing
    plot_upset_plot(venn_diagram_data, filenames, project)

    plot_venn_diagram(venn_diagram_data, filenames, project)


# Run for the specified project
find_and_move_duplicates('phd_litreview1')
