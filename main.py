from fastapi import FastAPI, Request, Form, Body, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import pandas as pd
import numpy as np
import os

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key='RL23IPH')

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Get a list of available projects
PROJECTS_DIR = 'data'
projects = [name for name in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, name))]


# Helper functions
def get_project_path(project_name, filename):
    return os.path.join(PROJECTS_DIR, project_name, filename)


def read_csv(file_path):
    return pd.read_csv(file_path) if os.path.exists(file_path) else pd.DataFrame()


def save_csv(df, file_path):
    print(f"Saving {file_path}")
    df.to_csv(file_path, index=False)


def read_static_info(file_path):
    return [line.strip() for line in open(file_path, 'r')] if os.path.exists(file_path) else []


def read_all_csvs(project):
    sources_dir = get_project_path(project, 'sources')
    all_files = [os.path.join(sources_dir, f) for f in os.listdir(sources_dir) if f.endswith('.csv')]
    all_dataframes = [read_csv(f) for f in all_files]
    return pd.concat(all_dataframes, ignore_index=True) if all_dataframes else pd.DataFrame()


def concatenate_fields(df):
    df['combined'] = df.apply(lambda row: '_'.join(row.astype(str)), axis=1)
    return df


def concatenate_record_fields(record):
    return '_'.join(map(str, record.values()))


def filter_out_processed_records(all_data_df, inclusions_df, exclusions_df):
    # Concatenate all fields to form a unique combined field temporarily
    all_data_df_temp = concatenate_fields(all_data_df.copy())
    inclusions_df_temp = concatenate_fields(inclusions_df.copy())
    exclusions_df_temp = concatenate_fields(exclusions_df.copy())

    # Create a set of combined fields from inclusions and exclusions
    processed_combined = set(inclusions_df_temp['combined']).union(exclusions_df_temp['combined'])

    # Filter out records whose combined field is in the processed_combined set
    return all_data_df[~all_data_df_temp['combined'].isin(processed_combined)]


def find_and_move_duplicates(project):
    sources_dir = get_project_path(project, 'sources')
    duplicates_file = get_project_path(project, 'duplicates.csv')
    combined_file = get_project_path(project, 'all_data.csv')

    all_files = [os.path.join(sources_dir, f) for f in os.listdir(sources_dir) if f.endswith('.csv')]
    all_dataframes = [read_csv(f) for f in all_files]
    combined_df = pd.concat(all_dataframes, ignore_index=True) if all_dataframes else pd.DataFrame()

    duplicates_df = combined_df[combined_df.duplicated(keep=False)]
    unique_df = combined_df.drop_duplicates()

    save_csv(unique_df, combined_file)
    save_csv(duplicates_df, duplicates_file)

    inclusions_file = get_project_path(project, 'inclusions.csv')
    exclusions_file = get_project_path(project, 'exclusions.csv')

    # Read existing inclusions and exclusions
    inclusions_df = read_csv(inclusions_file) if os.path.exists(inclusions_file) else pd.DataFrame()
    exclusions_df = read_csv(exclusions_file) if os.path.exists(exclusions_file) else pd.DataFrame()

    # Convert inclusions and exclusions to sets of DOIs and rows for quick lookup
    inclusion_dois = set(inclusions_df['DOI'].dropna()) if not inclusions_df.empty else set()
    exclusion_dois = set(exclusions_df['DOI'].dropna()) if not exclusions_df.empty else set()

    inclusion_rows = set([tuple(row) for row in inclusions_df.to_numpy()]) if not inclusions_df.empty else set()
    exclusion_rows = set([tuple(row) for row in exclusions_df.to_numpy()]) if not exclusions_df.empty else set()

    def is_duplicate(record):
        doi = record.get('DOI')
        if pd.notna(doi) and (doi in inclusion_dois or doi in exclusion_dois):
            return True
        record_tuple = tuple(record)
        if record_tuple in inclusion_rows or record_tuple in exclusion_rows:
            return True
        return False

    # Initialize lists to store new duplicate records
    new_duplicates = []

    # Iterate over combined_df and check for duplicates
    for idx, record in unique_df.iterrows():
        if is_duplicate(record):
            new_duplicates.append(record)

    # Create a DataFrame for new duplicates and remove them from combined_df
    new_duplicates_df = pd.DataFrame(new_duplicates)
    unique_df = unique_df[~unique_df.index.isin(new_duplicates_df.index)]

    # Combine new duplicates with existing duplicates
    if os.path.exists(duplicates_file):
        existing_duplicates_df = read_csv(duplicates_file)
        all_duplicates_df = pd.concat([existing_duplicates_df, new_duplicates_df], ignore_index=True)
    else:
        all_duplicates_df = new_duplicates_df

    save_csv(unique_df, combined_file)
    save_csv(all_duplicates_df, duplicates_file)


@app.on_event("startup")
async def startup_event():
    for project in projects:
        find_and_move_duplicates(project)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    project = request.session.get('project')
    if not project:
        project = projects[0]

    INCLUSIONS_FILE = get_project_path(project, 'inclusions.csv')
    EXCLUSIONS_FILE = get_project_path(project, 'exclusions.csv')
    INC_EXC_CRITERIA_FILE = get_project_path(project, 'inc_exc_criteria.txt')
    SELECTED_FIELDS_FILE = get_project_path(project, 'selected_fields.txt')

    all_data_df = read_csv(get_project_path(project, 'all_data.csv'))
    inclusions_df = read_csv(INCLUSIONS_FILE)
    exclusions_df = read_csv(EXCLUSIONS_FILE)
    static_info = read_static_info(INC_EXC_CRITERIA_FILE)

    all_data_df = filter_out_processed_records(all_data_df, inclusions_df, exclusions_df)

    if all_data_df.empty:
        return "No more records."

    record = all_data_df.iloc[0].to_dict()
    combined_record = concatenate_record_fields(record)

    # Ensure inclusions_df and exclusions_df have the combined field
    inclusions_df_temp = concatenate_fields(inclusions_df.copy())
    exclusions_df_temp = concatenate_fields(exclusions_df.copy())

    included = (not inclusions_df_temp.empty) and (combined_record in inclusions_df_temp['combined'].values)
    excluded = (not exclusions_df_temp.empty) and (combined_record in exclusions_df_temp['combined'].values)

    selected_fields = read_static_info(SELECTED_FIELDS_FILE) if os.path.exists(SELECTED_FIELDS_FILE) else list(record.keys())

    return templates.TemplateResponse("index.html", {
        "request": request,
        "project": project,
        "projects": projects,
        "record": record,
        "static_info": static_info,
        "record_id": 0,
        "included": included,
        "excluded": excluded,
        "selected_fields": selected_fields,
        "total_records": len(all_data_df),
        "included_count": len(inclusions_df),
        "excluded_count": len(exclusions_df),
        "duplicates_count": len(read_csv(get_project_path(project, 'duplicates.csv'))),
        "message": ""
    })


@app.post("/set_project", response_class=RedirectResponse)
async def set_project(request: Request, project: str = Form(...)):
    if project not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    request.session['project'] = project
    return RedirectResponse(url="/", status_code=303)


@app.get("/set_project_manually/{project_name}", response_class=RedirectResponse)
@app.post("/set_project_manually/{project_name}", response_class=RedirectResponse)
async def set_project_manually(request: Request, project_name: str):
    project_name = project_name.strip()
    if project_name not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    request.session['project'] = project_name
    return RedirectResponse(url="/", status_code=303)


def check_duplicates(record, inclusions_df, exclusions_df):
    inclusions_df_temp = concatenate_fields(inclusions_df.copy())
    exclusions_df_temp = concatenate_fields(exclusions_df.copy())
    combined_record = concatenate_record_fields(record)
    if not inclusions_df_temp.empty and combined_record in inclusions_df_temp['combined'].values:
        return True
    if not exclusions_df_temp.empty and combined_record in exclusions_df_temp['combined'].values:
        return True
    return False


@app.post("/action/{action}/{record_id}")
async def action(action: str, record_id: int, request: Request, exclusion_reason: str = Form(None)):
    project = request.session.get('project')
    if not project:
        project = projects[0]

    INCLUSIONS_FILE = get_project_path(project, 'inclusions.csv')
    EXCLUSIONS_FILE = get_project_path(project, 'exclusions.csv')
    DUPLICATES_FILE = get_project_path(project, 'duplicates.csv')
    ALL_DATA_FILE = get_project_path(project, 'all_data.csv')
    SELECTED_FIELDS_FILE = get_project_path(project, 'selected_fields.txt')

    all_data_df = read_csv(ALL_DATA_FILE)
    inclusions_df = read_csv(INCLUSIONS_FILE)
    exclusions_df = read_csv(EXCLUSIONS_FILE)
    duplicates_df = read_csv(DUPLICATES_FILE)

    if record_id >= len(all_data_df):
        return {"status": "error", "message": "Invalid record ID"}

    record = all_data_df.iloc[record_id].to_dict()

    if check_duplicates(record, inclusions_df, exclusions_df):
        duplicates_df = pd.concat([duplicates_df, pd.DataFrame([record])], ignore_index=True)
        save_csv(duplicates_df, DUPLICATES_FILE)
    else:
        if action == "include":
            inclusions_df = pd.concat([inclusions_df, pd.DataFrame([record])], ignore_index=True)
            save_csv(inclusions_df, INCLUSIONS_FILE)
        elif action == "exclude":
            record['Exclusion_Reason'] = exclusion_reason
            exclusions_df = pd.concat([exclusions_df, pd.DataFrame([record])], ignore_index=True)
            save_csv(exclusions_df, EXCLUSIONS_FILE)

    # Remove the record from all_data_df by index
    all_data_df = all_data_df.drop(all_data_df.index[record_id])
    save_csv(all_data_df, ALL_DATA_FILE)

    # Re-read the CSV to ensure the state is updated
    all_data_df = read_csv(ALL_DATA_FILE)
    all_data_df = filter_out_processed_records(all_data_df, inclusions_df, exclusions_df)

    if not all_data_df.empty:
        next_record_id = 0
        next_record = all_data_df.iloc[next_record_id].to_dict()
    else:
        next_record_id = -1
        next_record = {}

    # Filter selected fields
    selected_fields = read_static_info(SELECTED_FIELDS_FILE)
    if selected_fields:
        next_record = {key: next_record[key] for key in selected_fields if key in next_record}

    def sanitize_for_json(data):
        if isinstance(data, dict):
            return {k: (None if (isinstance(v, float) and (np.isnan(v) or np.isinf(v))) else v) for k, v in data.items()}
        return data

    next_record = sanitize_for_json(next_record)

    print(f"Total: {len(all_data_df)} | Included: {len(inclusions_df)} | Excluded: {len(exclusions_df)} | Duplicates: {len(duplicates_df)}")

    return {
        "status": "success",
        "record_id": next_record_id,
        "record": next_record,
        "total_records": len(all_data_df),
        "included_count": len(inclusions_df),
        "excluded_count": len(exclusions_df),
        "duplicates_count": len(duplicates_df)
    }


@app.post("/save_selected_fields")
async def save_selected_fields_route(request: Request, selected_fields: list = Body(...)):
    project = request.session.get('project')
    if not project:
        raise HTTPException(status_code=400, detail="Project not selected")

    SELECTED_FIELDS_FILE = get_project_path(project, 'selected_fields.txt')
    with open(SELECTED_FIELDS_FILE, 'w') as file:
        file.write('\n'.join(selected_fields))
    return {"status": "success", "message": "Selected fields saved successfully."}
