from dataclasses import dataclass, field

# from json import dump, load
from pathlib import Path
from typing import Any

from backlinks.collector.document import FileDictionary, JsonDictionary
from backlinks.logging import logging
from backlinks.path.path import empty_path, generate_file_list

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
    DOCUMENT_COLLECTOR: FileDictionary
    STORAGE_ENGINE: JsonDictionary
    JSON_PATH: Path = field(defauly=Path("./crosswalk.json"))
    PAGES: dict[Path, Any] = field(default=dict)
    SAVE_PATH: Path = field(defauly=Path())
    CROSSLINK: dict = field(default={"CROSSLINK": []})

    def load(
        self,
        default_value: dict = None,
        set_value: dict = None,
        store_content: bool = True,
    ):
        """Loads the book structure by scanning the root path for markdown files"""
        if self.JSON_PATH.exists():
            self.STORAGE_ENGINE(PATH=self.JSON_PATH)
            self.STORAGE_ENGINE.load()

        if self.PAGES:
            return None

        self.PAGES = dict.fromkeys(generate_file_list(self.PATH), None)
        for md_file in self.PAGES.keys():
            logging.debug(f"Processing markdown file: {md_file}")
            # Further processing can be added here
            try:
                DC = self.DOCUMENT_COLLECTOR.copy()
                self.PAGES[md_file] = DC.load_document(
                    md_file,
                    self.PATH,
                    default_value=default_value,
                    set_values=set_value,
                    store_content=store_content,
                )
            except Exception as e:
                logging.error(f"Exception found: {e}")
