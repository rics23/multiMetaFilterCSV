from fastapi import FastAPI, Request, Form, Body, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import pandas as pd
import numpy as np
import os
import shutil

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key='RL23IPH')

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

PROJECTS_DIR = 'data'
projects = [name for name in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, name))]


def get_project_path(project_name, filename):
    return os.path.join(PROJECTS_DIR, project_name, filename)


def read_csv(file_path):
    return pd.read_csv(file_path) if os.path.exists(file_path) else pd.DataFrame()


def save_csv(df, file_path):
    print(f"1 - Saving {file_path}")
    df.to_csv(file_path, index=False)


def read_static_info(file_path):
    return [line.strip() for line in open(file_path, 'r')] if os.path.exists(file_path) else []


# def read_all_csvs(project):
#     sources_dir = get_project_path(project, 'sources')
#     all_files = [os.path.join(sources_dir, f) for f in os.listdir(sources_dir) if f.endswith('.csv')]
#     all_dataframes = [read_csv(f) for f in all_files]
#     return pd.concat(all_dataframes, ignore_index=True) if all_dataframes else pd.DataFrame()

def find_and_move_duplicates(project):

    avoid_fields = ['ISSN']

    sources_dir = get_project_path(project, 'sources')
    duplicates_file = get_project_path(project, 'duplicates.csv')
    combined_file = get_project_path(project, 'all_data.csv')

    all_files = [os.path.join(sources_dir, f) for f in os.listdir(sources_dir) if f.endswith('.csv')]
    all_dataframes = [read_csv(f) for f in all_files]
    combined_df = pd.concat(all_dataframes, ignore_index=True) if all_dataframes else pd.DataFrame()

    duplicates_df = read_csv(duplicates_file) if os.path.exists(duplicates_file) else pd.DataFrame(columns=combined_df.columns)
    unique_df = read_csv(combined_file) if os.path.exists(combined_file) else pd.DataFrame(columns=combined_df.columns)

    for idx, record in combined_df.iterrows():
        unique_dois = set(unique_df['DOI'].dropna()) if (not unique_df.empty and 'DOI' in unique_df.columns) else set()
        unique_abstracts = set(unique_df['Abstract'].dropna()) if (not unique_df.empty and 'Abstract' in unique_df.columns) else set()

        doi = record.get('DOI')
        abstract = record.get('Abstract')

        record_df = pd.DataFrame([record])

        def is_in_unique():
            result = False
            for _, unique_record in unique_df.iterrows():
                rec_check = True
                for field in unique_df.columns:
                    if field in avoid_fields:
                        continue

                    if pd.isna(record[field]) and pd.isna(unique_record[field]):
                        continue

                    try:
                        if isinstance(record[field], (int, float)) and isinstance(unique_record[field], (int, float)):
                            if round(float(record[field])) != round(float(unique_record[field])):
                                rec_check = False
                                break
                        else:
                            if str(record[field]).strip() != str(unique_record[field]).strip():
                                rec_check = False
                                break
                    except ValueError:
                        rec_check = False
                        break

                if rec_check:
                    result = True
                    break

            return result

        if (
                (pd.notna(doi) and doi in unique_dois) or
                (abstract != "[No abstract available]" and abstract in unique_abstracts) or
                is_in_unique()
        ):
            duplicates_df = pd.concat([duplicates_df, record_df], ignore_index=True)
        else:
            unique_df = pd.concat([unique_df, record_df], ignore_index=True)

    save_csv(unique_df, combined_file)
    save_csv(duplicates_df, duplicates_file)

    unique_df = read_csv(combined_file) if os.path.exists(combined_file) else pd.DataFrame(columns=combined_df.columns)

    print(f"3 - Saving Duplicates containing {len(duplicates_df)} records")

    inclusions_file = get_project_path(project, 'inclusions.csv')
    exclusions_file = get_project_path(project, 'exclusions.csv')

    inclusions_df = read_csv(inclusions_file) if os.path.exists(inclusions_file) else pd.DataFrame()
    exclusions_df = read_csv(exclusions_file) if os.path.exists(exclusions_file) else pd.DataFrame()

    inclusion_dois = set(inclusions_df['DOI'].dropna()) if (not inclusions_df.empty and 'DOI' in inclusions_df.columns) else set()
    exclusion_dois = set(exclusions_df['DOI'].dropna()) if (not exclusions_df.empty and 'DOI' in exclusions_df.columns) else set()

    inclusion_abstracts = set(inclusions_df['Abstract'].dropna()) if (not inclusions_df.empty and 'Abstract' in inclusions_df.columns) else set()
    exclusion_abstracts = set(exclusions_df['Abstract'].dropna()) if (not exclusions_df.empty and 'Abstract' in exclusions_df.columns) else set()

    found_inc_exc = pd.DataFrame(columns=combined_df.columns)
    new_unique_df = pd.DataFrame(columns=combined_df.columns)

    for idx, record in unique_df.iterrows():
        doi = record.get('DOI')
        abstract = record.get('Abstract')

        record_df = pd.DataFrame([record])

        def is_in_inclusions():
            result = False
            for _, inclusion_record in inclusions_df.iterrows():
                rec_check = True
                for field in unique_df.columns:
                    if field in avoid_fields:
                        continue

                    if pd.isna(record[field]) and pd.isna(inclusion_record[field]):
                        continue

                    try:
                        if isinstance(record[field], (int, float)) and isinstance(inclusion_record[field], (int, float)):
                            if round(float(record[field])) != round(float(inclusion_record[field])):
                                rec_check = False
                                break
                        else:
                            if str(record[field]).strip() != str(inclusion_record[field]).strip():
                                rec_check = False
                                break
                    except ValueError:
                        rec_check = False
                        break

                if rec_check:
                    result = True
                    break

            return result

        def is_in_exclusions():
            result = False
            for _, exclusion_record in exclusions_df.iterrows():
                rec_check = True
                for field in unique_df.columns:
                    if field in avoid_fields:
                        continue

                    if pd.isna(record[field]) and pd.isna(exclusion_record[field]):
                        continue

                    try:
                        if isinstance(record[field], (int, float)) or isinstance(exclusion_record[field], (int, float)):
                            if round(float(record[field])) != round(float(exclusion_record[field])):
                                rec_check = False
                                break
                        else:
                            if str(record[field]).strip() != str(exclusion_record[field]).strip():
                                rec_check = False
                                break
                    except ValueError:
                        rec_check = False
                        break

                if rec_check:
                    result = True
                    break

            return result

        if (
                (pd.notna(doi) and (doi in inclusion_dois or doi in exclusion_dois)) or
                (abstract != "[No abstract available]" and (abstract in inclusion_abstracts or abstract in exclusion_abstracts))
        ):
            found_inc_exc = pd.concat([found_inc_exc, record_df], ignore_index=True)
        elif is_in_inclusions() or is_in_exclusions():
            print("Found in inclusions or exclusions")
            found_inc_exc = pd.concat([found_inc_exc, record_df], ignore_index=True)
        else:
            new_unique_df = pd.concat([new_unique_df, record_df], ignore_index=True)

    save_csv(new_unique_df, combined_file)

    print(f"4 - Found {len(found_inc_exc)} records in either inclusions or exclusions")
    print(f"5 - New unique df contains {len(new_unique_df)} records")

    processed_folder = os.path.join(os.path.dirname(sources_dir), "processed_sources")

    if not os.path.exists(processed_folder):
        os.makedirs(processed_folder)

    for file in all_files:
        shutil.move(file, processed_folder)
        print(f"Moved {file} to {processed_folder}")

@app.on_event("startup")
async def startup_event():
    for project in projects:
        find_and_move_duplicates(project)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    project = request.session.get('project')
    if not project:
        project = projects[0]

    ALL_DATA_FILE = get_project_path(project, 'all_data.csv')
    INCLUSIONS_FILE = get_project_path(project, 'inclusions.csv')
    EXCLUSIONS_FILE = get_project_path(project, 'exclusions.csv')
    INC_EXC_CRITERIA_FILE = get_project_path(project, 'inc_exc_criteria.txt')
    SELECTED_FIELDS_FILE = get_project_path(project, 'selected_fields.txt')

    all_data_df = read_csv(ALL_DATA_FILE)
    inclusions_df = read_csv(INCLUSIONS_FILE)
    exclusions_df = read_csv(EXCLUSIONS_FILE)
    static_info = read_static_info(INC_EXC_CRITERIA_FILE)

    if all_data_df.empty:
        message = "No more records."
        return templates.TemplateResponse("index.html", {
            "request": request,
            "project": project,
            "projects": projects,
            "record": {},
            "static_info": static_info,
            "record_id": -1,
            "selected_fields": [],
            "total_records": len(all_data_df),
            "included_count": len(inclusions_df),
            "excluded_count": len(exclusions_df),
            "duplicates_count": len(read_csv(get_project_path(project, 'duplicates.csv'))),
            "message": message
        })

    record = all_data_df.iloc[0].to_dict()

    selected_fields = read_static_info(SELECTED_FIELDS_FILE) if os.path.exists(SELECTED_FIELDS_FILE) else list(record.keys())

    return templates.TemplateResponse("index.html", {
        "request": request,
        "project": project,
        "projects": projects,
        "record": record,
        "static_info": static_info,
        "record_id": 0,
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

    record = all_data_df.iloc[record_id]

    if action == "include":
        inclusions_df = pd.concat([inclusions_df, pd.DataFrame([record])], ignore_index=True)
        save_csv(inclusions_df, INCLUSIONS_FILE)
    elif action == "exclude":
        record['Exclusion_Reason'] = exclusion_reason
        exclusions_df = pd.concat([exclusions_df, pd.DataFrame([record])], ignore_index=True)
        save_csv(exclusions_df, EXCLUSIONS_FILE)

    all_data_df = all_data_df.drop(all_data_df.index[record_id])
    save_csv(all_data_df, ALL_DATA_FILE)

    all_data_df = read_csv(ALL_DATA_FILE)

    if not all_data_df.empty:
        next_record_id = 0
        next_record = all_data_df.iloc[next_record_id].to_dict()
    else:
        next_record_id = -1
        next_record = {}

    selected_fields = read_static_info(SELECTED_FIELDS_FILE)
    if selected_fields:
        next_record = {key: next_record[key] for key in selected_fields if key in next_record}

    # def sanitize_for_json(data):
    #     if isinstance(data, dict):
    #         return {k: (None if (isinstance(v, float) and (np.isnan(v) or np.isinf(v))) else v) for k, v in data.items()}
    #     return data
    #
    # next_record = sanitize_for_json(next_record)

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
