from dataclasses import dataclass, field
from pathlib import Path

from backlinks.collector.document import DocumentDictionary
from backlinks.logging import logging
from backlinks.path.path import empty_path, generate_link_list

# ###
# Variables
# ###

logging.getLogger(__name__)

BOOK_FIELDS = {"PATH": empty_path(), "ROOT_PATH": empty_path(), "DOCUMENTS": {}}


###
# Class
# ###


@dataclass
class BookDictionary:
    """A dictionary used for holding DocumentsDictionary and meta about the process

    Args:
        PATH (Path): the invocation pint of the program
        root_path (Path): the root path of the scan
        documents (dict): A dictionary of DocumentDictionary objects
    """

    PATH: empty_path
    documents: dict[DocumentDictionary]
    link_dictionary: dict = field(init=False)

    def __post_init__(self):
        self.load()

    def load(self):
        """Loads the book structure by scanning the root path for markdown files"""
        link_list = generate_link_list(self.PATH)
        for md_file in link_list:
            logging.debug(f"Processing markdown file: {md_file}")
            # Further processing can be added here
            self.documents[md_file] = DocumentDictionary().load_document(
                md_file, self.PATH
            )
