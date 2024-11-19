import os
import pandas as pd

PROJECTS_DIR = 'data'
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


