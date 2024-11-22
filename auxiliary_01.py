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

PROJECTS_DIR = 'projects'
projects = [name for name in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, name))]


def read_csv(file_path):
    return pd.read_csv(file_path) if os.path.exists(file_path) else pd.DataFrame()


def get_project_path(project_name, filename):
    return os.path.join(PROJECTS_DIR, project_name, filename)


def save_csv(df, file_path):
    print(f"1 - Saving {file_path}")
    df.to_csv(file_path, index=False)


def read_static_info(file_path):
    return [line.strip() for line in open(file_path, 'r')] if os.path.exists(file_path) else []


