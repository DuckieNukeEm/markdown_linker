from backlinks.logging import logging

logging.getLogger(__name__)


# ###
# CSV functions
# ###
def load_csv_data(csv_path):
    """Load existing CSV data"""
    data = {}
    if csv_path.exists():
        logging.info(f"Loading existing CSV data from {csv_path}")
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["source_file"], row["target_file"])
                data[key] = row
        logging.debug(f"Loaded {len(data)} existing link records")
    else:
        logging.info("No existing CSV file found, starting fresh")
    return data


def save_csv_data(csv_path, links_data):
    """Save links data to CSV"""
    logging.info(f"Saving {len(links_data)} link records to {csv_path}")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "source_file",
            "source_title",
            "target_file",
            "target_title",
            "link_text",
            "status",
            "hierarchy_level",
            "link_type",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Sort by hierarchy level then by file path
        sorted_data = sorted(
            links_data, key=lambda x: (x["hierarchy_level"], x["source_file"])
        )
        writer.writerows(sorted_data)
    logging.debug("CSV file saved successfully")


def read_markdown_doc(markdon_doc_filepath: str):
    """Function that opens a markdown file"""
    # logging.debug(f"Processing {markdon_doc_filepath}")
    with open(markdon_doc_filepath, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    return markdown_content


def write_markdown_doc(markdon_doc_filepath: str, content: str):
    """Function that writes a markdown file"""
    with open(markdon_doc_filepath, "w", encoding="utf-8") as f:
        f.write(content)
    logging.debug(f"Wrote updated content to {markdon_doc_filepath}")
