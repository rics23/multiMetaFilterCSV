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

from auxiliary_01 import *
from auxiliary_02 import *

project = "phd_litreview1"

inclusions_file = get_project_path(project, 'inclusions.csv')
inclusions_df = read_csv(inclusions_file) if os.path.exists(inclusions_file) else pd.DataFrame()

dois_file = get_project_path(project, "dois.csv")
dois_df = read_csv(dois_file) if os.path.exists(dois_file) else pd.DataFrame()

if 'DOI' not in dois_df.columns:
    dois_df['DOI'] = []

if 'Inclusion_Importance' not in dois_df.columns:
    dois_df['Inclusion_Importance'] = []

inclusions_df = inclusions_df.dropna(subset=['DOI', 'Inclusion_Importance'])

new_dois = pd.DataFrame({
    'DOI': inclusions_df['DOI'].values,
    'Inclusion_Importance': inclusions_df['Inclusion_Importance'].values
})

dois_df = pd.concat([dois_df, new_dois], ignore_index=True)

dois_df = dois_df.drop_duplicates(subset=['DOI']).reset_index(drop=True)

dois_df = dois_df.sort_values(by='Inclusion_Importance', ascending=False)

for doi in dois_df['DOI']:
    print(doi)

save_csv(dois_df, dois_file)

save_folder = get_project_path(project, "unpaywall_data")
pdf_folder = get_project_path(project, "PDFs")

email = "rics.23@gmail.com"

os.makedirs(save_folder, exist_ok=True)
os.makedirs(pdf_folder, exist_ok=True)

# if not os.path.exists(dois_file):
#     logging.error(f'     The file {dois_file} does not exist.')
#
# dois_df = read_csv(dois_file) if os.path.exists(dois_file) else pd.DataFrame()
#
# if dois_df.empty:
#     logging.warning('     No DOIs found in the file.')

for index, row in dois_df.iterrows():
    doi = row['DOI']
    inclusion_importance = row['Inclusion_Importance']

    logging.info(f'     Processing DOI: {doi} with Inclusion Importance: {inclusion_importance}')

    importance_folder = os.path.join(save_folder, f"Importance_{inclusion_importance}")
    importance_pdf_folder = os.path.join(pdf_folder, f"Importance_{inclusion_importance}")

    os.makedirs(importance_folder, exist_ok=True)
    os.makedirs(importance_pdf_folder, exist_ok=True)

    data = fetch_unpaywall_data(doi, email)
    if data:
        save_unpaywall_data(doi, data, importance_folder)
        pdf_url = find_pdf_links(data)
        if pdf_url:
            if download_pdf(pdf_url, importance_pdf_folder):
                continue

    resolved_url = resolve_doi(doi)
    if resolved_url:
        if download_pdf(resolved_url, importance_pdf_folder):
            continue
        else:
            logging.info(f'Opening URL in browser: {resolved_url}')
            webbrowser.open_new_tab(resolved_url)
    else:
        logging.warning(f'Could not resolve DOI: {doi}')
        webbrowser.open_new_tab(f"{DOI_URL_PREFIX}{doi}")