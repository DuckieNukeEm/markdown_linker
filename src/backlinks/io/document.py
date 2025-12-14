from backlinks.logging import logging

logger = logging.getLogger(__name__)


def read_document(doc_filepath: str):
    """Function that opens a file"""
    logging.debug(f"Loading {doc_filepath}")
    with open(doc_filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def write_doc(doc_filepath: str, content: str):
    """Function that writes a markdown file"""
    with open(doc_filepath, "w", encoding="utf-8") as f:
        f.write(content)
    logging.debug(f"Wrote updated content to {doc_filepath}")
