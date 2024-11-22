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

import requests
import csv
import xml.etree.ElementTree as ET

search_queries = {
    "1-a": '"Artificial Intelligence" AND ("Criminal Justice" OR "Law Enforcement") AND ("UK" OR "United Kingdom" OR "Britain")',
    "1-b": '("AI" OR "Machine Learning" OR "Algorithmic") AND ("Criminal Justice System" OR "Law Enforcement" OR "Policing") AND ("UK" OR "Britain")',
    "1-c": '("Artificial Intelligence" OR "AI technology") AND ("Judicial System" OR "Criminal Law") AND ("UK" OR "England" OR "Wales")',
    "1-d": '("Artificial Intelligence" OR "AI") AND ("Criminal Justice" OR "Public Safety" OR "Justice Sector") AND ("UK" OR "United Kingdom")',

    "2-a": '("Predictive Analytics" OR "AI") AND ("Justice System" OR "Legal System") AND ("UK" OR "United Kingdom")',
    "2-b": '("AI" OR "Machine Learning" OR "Predictive Analytics") AND ("Criminal Justice" OR "Policing" OR "Court System") AND ("UK" OR "United Kingdom")',
    "2-c": '("Artificial Intelligence" OR "AI") AND "criminal*" AND ("UK" OR "Britain")',
    "2-d": '"Predictive Policing" AND ("England and Wales")',
    "2-e": '("AI" OR "Artificial Intelligence") AND ("Predictive Policing" OR "Risk Assessment") AND ("Justice System" OR "Judicial System") AND ("England and Wales")',
    "2-f": '"Sentencing Algorithms" AND ("England and Wales" OR "British Courts")',
    "2-g": '("Predictive Analytics" OR "Risk Assessment" OR "Recidivism Prediction") AND ("Justice System" OR "Criminal Justice") AND ("England and Wales")',

    "3-a": '"AI Bias" AND "Criminal Justice" AND ("England and Wales")',
    "3-b": '"Ethical Implications" AND "AI" AND ("Law Enforcement" OR "Justice System") AND ("England and Wales")',
    "3-c": '"Algorithmic Fairness" AND ("Criminal Justice" OR "Sentencing") AND ("England and Wales")',
    "3-d": '("Bias in AI" OR "Algorithmic Bias") AND ("Justice System" OR "Courts") AND ("England and Wales")',
    "3-e": '("Privacy" OR "Ethics") AND ("AI" OR "Machine Learning") AND ("Criminal Justice" OR "Law Enforcement") AND ("England and Wales")',
    "3-f": '("Ethics" OR "Privacy" OR "Bias" OR "Transparency") AND ("Artificial Intelligence" OR "Machine Learning") AND ("Justice System" OR "Criminal Justice") AND ("England and Wales")',

    "4-a": '"AI Oversight" AND ("Criminal Justice System") AND ("England and Wales")',
    "4-b": '"Policy Framework" AND "Artificial Intelligence" AND ("England and Wales")',
    "4-c": '"Data Privacy" AND "AI" AND ("Criminal Justice System") AND ("England and Wales")',
    "4-d": '("AI Governance" OR "Policy Framework" OR "Legal Oversight") AND ("Artificial Intelligence" OR "Machine Learning") AND ("Justice System" OR "Public Sector") AND ("UK" OR "England")',

    "5-a": '"Artificial Intelligence" AND "Criminal Justice System"',
    "5-b": '("Artificial Intelligence" OR "AI" OR "Machine Learning") AND ("Criminal Justice" OR "Justice System" OR "Law Enforcement" OR "Policing") AND ("UK" OR "United Kingdom" OR "Britain")'
}


def fetch_arxiv_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error: {response.status_code}")
        return None


def parse_arxiv_data(xml_data):
    root = ET.fromstring(xml_data)
    entries = []

    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        authors = ', '.join([author.find('{http://www.w3.org/2005/Atom}name').text for author in
                             entry.findall('{http://www.w3.org/2005/Atom}author')])
        published_date = entry.find('{http://www.w3.org/2005/Atom}published').text
        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text if entry.find(
            '{http://www.w3.org/2005/Atom}summary') is not None else ''

        title = title.replace('\n', ' ').strip()
        summary = summary.replace('\n', ' ').strip()

        pdf_link_element = entry.find('{http://arxiv.org/schemas/atom}link[@title="pdf"]')
        pdf_url = pdf_link_element.attrib['href'] if pdf_link_element is not None else 'No PDF available'

        entries.append([title, authors, published_date, summary, pdf_url])

    return entries


def save_to_csv(data, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Authors", "Published Date", "Abstract", "Link"])
        writer.writerows(data)
    print(f"Results saved to {filename}")


for search_key, query in search_queries.items():
    encoded_query = query.replace(' ', '+')

    api_url = f'http://export.arxiv.org/api/query?search_query={encoded_query}&max_results=1000'

    xml_data = fetch_arxiv_data(api_url)
    if xml_data:
        parsed_data = parse_arxiv_data(xml_data)
        if parsed_data:
            save_to_csv(parsed_data, f'arxiv-{search_key}.csv')
