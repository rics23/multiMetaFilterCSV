import requests
import os
import json
import webbrowser
from urllib.parse import quote, unquote
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DOI_URL_PREFIX = 'https://doi.org/'


def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


# Download PDF from URL
def download_pdf(url, dest_folder):
    headers = {
        'Accept': 'application/pdf',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    session = requests_retry_session()

    try:
        response = session.get(url, headers=headers, stream=True, timeout=20)
        content_type = response.headers.get('Content-Type', '')

        if 'application/pdf' in content_type:
            filename = unquote(url.split('/')[-1])
            if not filename.endswith('.pdf'):
                filename += '.pdf'

            pdf_path = os.path.join(dest_folder, filename)
            with open(pdf_path, 'wb') as pdf_file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        pdf_file.write(chunk)
            logging.info(f'     Downloaded: {pdf_path}')
            return True
        else:
            logging.warning(f'     Content at URL is not a PDF: {url}')
            return False
    except Exception as e:
        logging.error(f'     Error downloading PDF from {url}: {e}')
        return False


def resolve_doi(doi):
    headers = {
        'Accept': 'application/pdf, application/json;q=0.9, */*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    doi_url = f'https://doi.org/{quote(doi)}'
    session = requests_retry_session()

    try:
        response = session.head(doi_url, headers=headers, allow_redirects=True, timeout=10)
        if response.status_code == 200:
            final_url = response.url
            logging.info(f'     DOI resolved to URL: {final_url}')
            return final_url
        else:
            logging.warning(f'     Failed to resolve DOI {doi}: HTTP {response.status_code}')
            return None
    except Exception as e:
        logging.error(f'     Error resolving DOI {doi}: {e}')
    return None


def fetch_unpaywall_data(doi, email):
    url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            logging.warning(f"     Error fetching data for DOI {doi}: HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"     Request exception for DOI {doi}: {e}")
        return None


def save_unpaywall_data(doi, data, save_folder):
    filename = f"{doi.replace('/', '_')}.json"
    filepath = os.path.join(save_folder, filename)
    with open(filepath, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    logging.info(f"     Saved data for DOI {doi} to {filepath}")


def find_pdf_links(data):
    if 'best_oa_location' in data and data['best_oa_location']:
        return data['best_oa_location']['url_for_pdf']

    if 'oa_locations' in data:
        for location in data['oa_locations']:
            if location.get('url_for_pdf'):
                return location['url_for_pdf']

    logging.warning("     No PDF link found in Unpaywall data")
    return None

