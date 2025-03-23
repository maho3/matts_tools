import bibtexparser
import ads
import time
from tqdm import tqdm

# Replace with your actual ADS API token
ADS_API_TOKEN = "API_TOKEN_HERE"

# Configure ADS API
ads.config.token = ADS_API_TOKEN


def fetch_ads_bibtex(entry):
    """Fetch the correct BibTeX from ADS using DOI or title."""
    doi = entry.get("doi", "").strip()
    title = entry.get("title", "").strip("{}")

    if doi:
        query = ads.SearchQuery(doi=doi, fl=["bibtex"])
    elif title:
        query = ads.SearchQuery(title=title, fl=["bibtex"])
    else:
        print(f"Skipping entry {entry['ID']} (no DOI or title)")
        return None

    try:
        for paper in query:
            return paper.bibtex
    except Exception as e:
        print(f"Error fetching ADS BibTeX for {entry['ID']}: {e}")
        return None


def update_bibtex(input_file, output_file):
    """Read a BibTeX file, update entries using ADS, and save the result."""
    with open(input_file, "r") as f:
        bib_database = bibtexparser.load(f)

    updated_entries = []

    for entry in tqdm(bib_database.entries):
        # print(f"Fetching ADS BibTeX for {entry['ID']}...")
        ads_bibtex = fetch_ads_bibtex(entry)

        if ads_bibtex:
            # Parse ADS BibTeX and replace while keeping the same tag
            ads_db = bibtexparser.loads(ads_bibtex)
            if ads_db.entries:
                ads_entry = ads_db.entries[0]
                ads_entry["ID"] = entry["ID"]  # Preserve original tag
                updated_entries.append(ads_entry)
        else:
            updated_entries.append(entry)  # Keep original if not found

        time.sleep(1)  # To avoid ADS rate limits

    bib_database.entries = updated_entries

    with open(output_file, "w") as f:
        bibtexparser.dump(bib_database, f)

    print(f"Updated BibTeX saved to {output_file}")


# Usage example
update_bibtex("input.bib", "output.bib")

