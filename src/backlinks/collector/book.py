from dataclasses import dataclass

from backlinks.logging import logging
from backlinks.path.path import empty_path

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
    root_path: empty_path
    documents: dict
