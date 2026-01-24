from secrets import token_hex

from backlinks.collector import CallableDict
from backlinks.io.document import read_document, write_document
from backlinks.logging import logging
from backlinks.markdown.markdown import get_links
from backlinks.path.path import empty_path, get_scan_relative_path
from backlinks.yaml import meta_to_dict
from backlinks.lib import type_of_link

# ###
# Variables
# ###

logging.getLogger(__name__)

DOCUMENT_FIELDS = {
    "PATH": empty_path(),
    "REL_PATH": "",
    "BACKLINKS": [],
    "BACKLINKS_PATH": [],
    "LINKS": {},
    "LINKS_PATH": [],
    "NEED2UPDATE": False,
    "CONTENT": "",
    "ID": None,
    "DESCRIPTION": "",
    "TAGS": [],
    "EDITOR": "markdown",
    "TITLE": "",
    "DATECREATED": "",
    "PUBLISHED": "",
    "DATE": "",
}

###
# Class
# ###


class DocumentDictionary(CallableDict):
    """A dictionary used for holding document meta data

    Args:
        callabledict (callabledict): _description_
    """

    def __init__(self, initial_data=None, call_on_get=False):
        if initial_data is None or not isinstance(initial_data, dict):
            initial_data = DOCUMENT_FIELDS.copy()
        super().__init__(initial_data=initial_data, call_on_get=call_on_get)
        self.MARKDOWN_HEADER_FINDERR = r"title:.*"
        self.document_type = "markdown"

    def generate_id(self, print: bool = False):
        """Generates a unique ID for the document if it does not already have one

        Returns:
            None: The unique ID
        """
        self["ID"] = token_hex(nbytes=16)
        if print:
            logging.debug(f"Generated new ID for document: {self['ID']}")

    def load_links(self, *args, **kwargs):
        """Extract markdown links from content

        Args:
            markdown_only (bool, optional): _description_. Defaults to True.

        Returns:
            tuple: returns a tuple of two list,
                    1 - all the links before backlings
                    2 - all the links after backlings (empty list if backlinks doesn't exists)
        """
        if self.document_type == "markdown":
            LNK, BACKLNK = get_links(*args, **kwargs)
            self.LINKS = LNK
            self.BACKLINKS = BACKLNK

    def load_headers(self, *args, **kwargs):
        """Extract headers as a dictionary"""
        if self.document_type == "markdown":
            header = meta_to_dict(*args, **kwargs)
        for x in header.keys():
            self[x] = header[x]

    def add_link(self, link: str):
        """adds a link to the dictionary"""
        if link not in self['LINKS'].keys():
            self['LNKS'][link] =  type_of_link(link)

    def add_backlink(self, link: str):
        """adds a backlink to the dictionary"""
        if link not in self['BACKLINKS'].keys():
            self['BACKLNKS'][link] =  type_of_link(link)

    
    def load_file(
        self, path: Path, system_path: str, default_values: dict = None, set_values: dict = None, store_content: bool = True
    ):
        """Populates the DocumentDictionary from a given dictionary

        Args:
            data_dict (dict): The dictionary to populate from
        """
        logging.debug(f"Generating the necessary infromation from {path}")
        loaded_content = read_document(path)
        self["PATH"] = path
        self["REL_PATH"] = get_scan_relative_path(path, system_path)

        self.load_links(loaded_content)

        if len(self["BACKLINKS"]) > 0:
            self["BACKLINKS_PATH"] = self["BACKLINKS"].keys()
        if len(self["LINKS"]) > 0:
            self["LINKS_PATH"] = self["LINKS"].keys()

        self["NEED2UPDATE"] = False

        self.load_headers(loaded_content)
        if store_content:
            self["CONTENT"] = loaded_content

        if self["ID"] == "":
            self.generate_id()

        for k,v in default_values.items():
            self[k] = self.get(k,v)
        
        for k,v in set_values.items():
            self[k] = v
        
    def save_file(self, path: Path = None):
        """Populates the DocumentDictionary from a given dictionary

        Args:
            data_dict (dict): The dictionary to populate from
        """
        logging.debug(f"Writing document to {self['PATH']}")
        write_document(self["CONTENT"], path if path else self["PATH"])
