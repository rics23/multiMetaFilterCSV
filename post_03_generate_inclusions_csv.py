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

project = "phd_litreview1"

inclusions_file = get_project_path(project, 'inclusions.csv')
new_inclusions_file = get_project_path(project, 'filtered_inclusions.csv')

inclusions_df = read_csv(inclusions_file) if os.path.exists(inclusions_file) else pd.DataFrame()

subset_fields = ['Authors', 'Title', 'Document Title', 'DOI', 'Inclusion_Importance']

filtered_df = inclusions_df[subset_fields]

if 'Inclusion_Importance' in filtered_df.columns:
    filtered_df = filtered_df.sort_values(by='Inclusion_Importance', ascending=False)

save_csv(filtered_df, new_inclusions_file)
