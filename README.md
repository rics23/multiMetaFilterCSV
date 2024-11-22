![Project Logo](static/metaFilterCSV.webp)

_A tool for streamlining systematic literature reviews by combining CSV data from diverse databases and arXiv, standardising results on a local web page for efficient duplicate detection, inclusion/exclusion tracking, and PRISMA-aligned visualisations and supporting files._

## Project Overview

Systematic literature reviews are essential for synthesising research findings across various studies. However, managing and filtering vast amounts of data from multiple databases can be time-consuming and prone to errors. **multiMetaFilterCSV** addresses these challenges by automating the process of data aggregation, duplicate detection, and record management, all while adhering to the PRISMA methodology.

## Features

- **Data Aggregation**: Combine CSV data from multiple databases seamlessly.
- **Duplicate Detection**: Automatically identify and manage duplicate records to ensure data integrity.
- **Inclusion/Exclusion Tracking**: Easily mark records as included or excluded with reasons for exclusion.
- **Local Web Interface**: View and manage your data through a standardised and user-friendly local web page.
- **Supporting Files Generation**: Automatically create files necessary for further systematic literature review tasks.

### Prerequisites

- **Python 3.9+**
- **pip** (Python package installer)

## Usage

1. **Uploading CSV Files**

   Before running the application,
   - Place your CSV files in the designated `sources` directory within your project folder.
   - The application will automatically process these files, detect duplicates, and consolidate the data.
   
2. **Fetching Data from arXiv**

   Use the pre_01_arxiv_search_strings_download_results.py script to fetch academic papers related to your systematic review. This script:

   - Executes predefined search queries to interact with the arXiv API.
   - Downloads relevant metadata (title, authors, abstract, publication date, and PDF link) for up to 1,000 results per query.
   - Saves the results as CSV files in the project directory, named according to the search query (e.g., arxiv-1-a.csv).
   - PS: Remember to move these files to the appropriate folder within your project folder.

3. **Launching the Application**

   - Run the application: `uvicorn main:app --port 8022 --reload`
   - Navigate to `http://127.0.0.1:8022/` in your web browser.

4. **Managing Records**

   - **Include Records**: Mark records as included, assigning them a level of importance.
   - **Exclude Records**: Mark records as excluded, providing reasons for exclusion.

5. **Visualisations and Reports**

   - **Step 1 - `post_01_venn_diagram.py`**:
     - **Read Input Data**: Combines CSV files from multiple sources (e.g., `processed_sources` folder and `inclusions.csv`).
     - **Detect Overlaps**: Matches entries based on fields like `EID`, `DOI`, or `Abstract` to detect duplicates or related records.
     - **Create Visuals**:
        - **Venn Diagram**: For up to 6 data sets, shows overlapping and unique records between sources.
        - **UpSet Plot**: For larger datasets, visualises complex overlaps.
     - **Save Outputs**:
        - Saves the overlap data (`venn_diagram_data.csv`) for further analysis.
        - Outputs Venn and UpSet diagram images in the project directory.

   - **Step 2 - `post_02_download_inclusions.py`**:
     - **Read Inclusion Data**: Loads `inclusions.csv` and filters DOIs with their respective importance ratings.
     - **Organise by Priority**: Groups studies into folders based on `Inclusion_Importance` for easier management.
     - **Fetch Metadata**: Uses services like Unpaywall to fetch metadata and links for DOIs.
     - **Download PDFs**: Attempts automatic downloads of PDFs. If unsuccessful, resolves DOIs for manual browsing.
     - **Save Outputs**: Saves metadata (`dois.csv`) and PDFs in organised directories.

   - **Step 3 - `post_03_generate_inclusions_csv.py`**:
     - **Load Inclusion Data**: Reads `inclusions.csv`.
     - **Filter Fields**: Selects key fields like `Authors`, `Title`, `Document Title`, `DOI`, and `Inclusion_Importance`.
     - **Sort by Importance**: Orders studies by their importance for clarity.
     - **Export Final Dataset**: Saves the filtered data as `filtered_inclusions.csv`.

This modular design ensures systematic, reproducible, and efficient management of literature review data.

## Project Structure

```
multiMetaFilterCSV/
├── main.py
├── auxiliary_01.py
├── auxiliary_02.py
├── pre_01_arxiv_search_strings_download_results.py
├── post_01_venn_diagram.py
├── post_02_download_inclusions.py
├── post_03_generate_inclusions_csv.py
├── static/
│   ├── styles.css
│   ├── script.js
│   └── metaFilterCSV.webp
├── templates/
│   └── index.html
├── projects/
│   ├── project1/
│   │   ├── sources/
│   │   ├── processed_sources/
│   │   └── inc_exc_criteria.txt
│   └── project2/
│       ├── sources/
│       ├── processed_sources/
│       └── inc_exc_criteria.txt
├── requirements.txt
├── COPYING
└── README.md
```

## License

This project is licensed under the [GNU General Public License v3.0](COPYING).

## Contact

**Ricardo Lopes**

- Email: [rics.23@gmail.com](mailto:rics.23@gmail.com)
- GitHub: [https://github.com/rics23](https://github.com/rics23)

Feel free to reach out for any questions, suggestions, or collaborations!