from fastapi import FastAPI, Request, Form, Body, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import pandas as pd
import os
import requests

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key='your_secret_key')

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Get a list of available projects
PROJECTS_DIR = 'data'
projects = [name for name in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, name))]


# Helper functions to get paths based on the project
def get_project_path(project_name, filename):
    return os.path.join(PROJECTS_DIR, project_name, filename)


def read_csv(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame()


def save_csv(df, file_path):
    df.to_csv(file_path, index=False)


def read_selected_fields(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.read().splitlines()
    else:
        return []


def save_selected_fields(file_path, fields):
    with open(file_path, 'w') as file:
        file.write('\n'.join(fields))


def read_static_info(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]


# Route to select project
@app.get("/select_project", response_class=HTMLResponse)
async def select_project(request: Request):
    return templates.TemplateResponse("select_project.html", {
        "request": request,
        "projects": projects
    })


# Route to set project in session and redirect to index
@app.post("/set_project", response_class=RedirectResponse)
async def set_project(request: Request, project: str = Form(...)):
    if project not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    request.session['project'] = project
    return RedirectResponse(url="/", status_code=303)


# Route to display a record
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, record_id: int = 0):
    project = request.session.get('project')
    if not project:
        return RedirectResponse(url="/select_project", status_code=303)

    CSV_FILE = get_project_path(project, 'scopus.csv')
    INCLUSIONS_FILE = get_project_path(project, 'inclusions.csv')
    EXCLUSIONS_FILE = get_project_path(project, 'exclusions.csv')
    INC_EXC_CRITERIA_FILE = get_project_path(project, 'inc_exc_criteria.txt')
    SELECTED_FIELDS_FILE = get_project_path(project, 'selected_fields.txt')

    scopus_df = read_csv(CSV_FILE)
    inclusions_df = read_csv(INCLUSIONS_FILE)
    exclusions_df = read_csv(EXCLUSIONS_FILE)
    static_info = read_static_info(INC_EXC_CRITERIA_FILE)

    if record_id >= len(scopus_df):
        return "No more records."

    record = scopus_df.iloc[record_id].to_dict()

    included = (not inclusions_df.empty) and (record['EID'] in inclusions_df['EID'].values)
    excluded = (not exclusions_df.empty) and (record['EID'] in exclusions_df['EID'].values)

    selected_fields = read_selected_fields(SELECTED_FIELDS_FILE)
    if not selected_fields:
        selected_fields = list(record.keys())
        save_selected_fields(SELECTED_FIELDS_FILE, selected_fields)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "record": record,
        "static_info": static_info,
        "record_id": record_id,
        "included": included,
        "excluded": excluded,
        "selected_fields": selected_fields
    })


# Route to handle include/exclude actions
@app.post("/action/{action}/{record_id}")
async def action(request: Request, action: str, record_id: int):
    project = request.session.get('project')
    if not project:
        raise HTTPException(status_code=400, detail="No project selected")

    CSV_FILE = get_project_path(project, 'scopus.csv')
    INCLUSIONS_FILE = get_project_path(project, 'inclusions.csv')
    EXCLUSIONS_FILE = get_project_path(project, 'exclusions.csv')

    scopus_df = read_csv(CSV_FILE)
    inclusions_df = read_csv(INCLUSIONS_FILE)
    exclusions_df = read_csv(EXCLUSIONS_FILE)

    record = scopus_df.iloc[record_id].to_dict()

    if action == 'include':
        inclusions_df = pd.concat([inclusions_df, pd.DataFrame([record])], ignore_index=True)
        save_csv(inclusions_df, INCLUSIONS_FILE)
        download_document(record['Link'], record['Title'], project)
    elif action == 'exclude':
        exclusions_df = pd.concat([exclusions_df, pd.DataFrame([record])], ignore_index=True)
        save_csv(exclusions_df, EXCLUSIONS_FILE)

    scopus_df.drop(record_id, inplace=True)
    scopus_df.reset_index(drop=True, inplace=True)
    save_csv(scopus_df, CSV_FILE)

    return RedirectResponse(url=f"/?record_id={record_id}", status_code=303)


# Function to download document
def download_document(url, title, project):
    response = requests.get(url)
    if response.status_code == 200:
        project_folder = get_project_path(project, 'inclusions')
        os.makedirs(project_folder, exist_ok=True)
        file_path = os.path.join(project_folder, f"{title}.pdf")
        with open(file_path, 'wb') as file:
            file.write(response.content)


# Route to save selected fields
@app.post("/save_selected_fields")
async def save_selected_fields_route(request: Request, selected_fields: list = Body(...)):
    project = request.session.get('project')
    if not project:
        raise HTTPException(status_code=400, detail="No project selected")

    SELECTED_FIELDS_FILE = get_project_path(project, 'selected_fields.txt')
    save_selected_fields(SELECTED_FIELDS_FILE, selected_fields)
    return {"message": "Selected fields saved successfully"}
