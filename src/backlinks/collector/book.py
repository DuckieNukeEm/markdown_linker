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
    PATH: Path 
    ROOT_PATH: Path 
    PAGES: dict[Path,DocumentDictionary] = field(default=dict)
    SAVE_PATH: Path = field(defauly=Path())
    CROSSLINK: list[str] = field(default=list)

    def load(self, default_value: dict = None, set_value: dict = None, store_content: bool = True):
        """Loads the book structure by scanning the root path for markdown files"""
        if self.PAGES:
            return None
        
        self.PAGES = dict.fromkeys(generate_link_list(self.PATH),None)
        for md_file in self.PAGES.keys():
            logging.debug(f"Processing markdown file: {md_file}")
            # Further processing can be added here
            try:
                self.PAGES[md_file] = DocumentDictionary().load_document(
                md_file, 
                self.PATH,
                default_value = default_value,
                set_values = set_value,
                store_content = store_content
                )
            except Exception as e:
                logging.error(f"Exception found: {e}")


