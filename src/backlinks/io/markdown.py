from backlinks.logging import logging

logger = logging.getLogger(__name__)


def read_markdown_doc(markdon_doc_filepath: str):
    """Function that opens a markdown file"""
    # logging.debug(f"Processing {markdon_doc_filepath}")
    logging.debug(f"Reading markdown document from {markdon_doc_filepath}")
    with open(markdon_doc_filepath, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    return markdown_content


def write_markdown_doc(markdon_doc_filepath: str, content: str):
    """Function that writes a markdown file"""
    with open(markdon_doc_filepath, "w", encoding="utf-8") as f:
        f.write(content)
    logging.debug(f"Wrote updated content to {markdon_doc_filepath}")
