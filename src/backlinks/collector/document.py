from dataclasses import dataclass, field
from json import dump, load
from pathlib import Path
from secrets import token_hex

from backlinks.collector import CallableDict
from backlinks.lib import type_of_link
from backlinks.logging import logging
from backlinks.markdown.markdown import add_backlinks_section, get_links
from backlinks.path.path import empty_path, get_scan_relative_path
from backlinks.yaml import meta_to_dict

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
    # "ID": None,
    # "DESCRIPTION": "",
    # "TAGS": [],
    # "EDITOR": "markdown",
    # "TITLE": "",
    # "DATECREATED": "",
    # "PUBLISHED": "",
    # "DATE": "",
}


def id():
    return token_hex(nbytes=16)


###
# Class
# ###


class FileDictionary(CallableDict):
    """A dictionary used for holding document meta data

    Args:
        callabledict (callabledict): _description_
    """

    def __init__(self, initial_data=None, call_on_get=False):
        if initial_data is None or not isinstance(initial_data, dict):
            initial_data = DOCUMENT_FIELDS.copy()
        super().__init__(initial_data=initial_data, call_on_get=call_on_get)
        # self.MARKDOWN_HEADER_FINDERR = r"title:.*"
        self.document_type = "markdown"
        self.update_content = False

    def generate_id(self):
        """Generates a unique ID for the document if it does not already have one

        Returns:
            None: The unique ID
        """
        self["ID"] = id()
        logging.info(f"Generated new ID for document: {self['ID']}")

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
            self["LINKS"] = LNK
            self["BACKLINKS"] = BACKLNK
            if len(BACKLNK) > 0:
                self["BACKLINKS_PATH"] = BACKLNK.keys()
            if len(LNK) > 0:
                self["LINKS_PATH"] = LNK.keys()

    def load_headers(self, *args, **kwargs) -> None:
        """Extract headers as a dictionary"""
        if self.document_type == "markdown":
            header = meta_to_dict(*args, **kwargs)
        for x in header.keys():
            self[x] = header[x]

    def add_link(self, link: str):
        """adds a link to the dictionary"""
        if link not in self["LINKS"].keys():
            self["LNKS"][link] = type_of_link(link)
            self.update_content = True

    def add_backlink(self, link: str):
        """adds a backlink to the dictionary"""
        if link not in self["BACKLINKS"].keys():
            self["BACKLNKS"][link] = type_of_link(link)
            self.update_content = True

    def delete_content(self):
        """deletes any conetent that is stored, just leaving keys"""
        self["CONTENT"] = ""
        self.update_content = False
        logging.debug(f"Deleteign content from {self['REL_PATH']}")

    def save_content(self, content: str):
        self["CONTENT"] = content
        self.update_content = True

    def _read_document(self, doc_filepath: str):
        """Function that opens a file"""
        logging.debug(f"Loading {doc_filepath}")
        with open(doc_filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content

    def _write_document(doc_filepath: str, content: str):
        """Function that writes a markdown file"""
        with open(doc_filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logging.debug(f"Wrote updated content to {doc_filepath}")

    def load_document(
        self,
        path: Path,
        system_path: str,
        default_values: dict = None,
        set_values: dict = None,
        store_content: bool = True,
    ):
        """Populates the DocumentDictionary from a given dictionary

        Args:
            data_dict (dict): The dictionary to populate from
        """
        logging.debug(f"Generating the necessary infromation from {path}")
        loaded_content = self._read_document(path)
        self["PATH"] = path
        self["REL_PATH"] = get_scan_relative_path(path, system_path)

        self.load_links(loaded_content)

        self["NEED2UPDATE"] = False

        self.load_headers(loaded_content)

        if store_content:
            self.save_content(loaded_content)
            self.update_content = False

        if self["ID"] == "":
            self.generate_id()

        for k, v in default_values.items():
            self[k] = self.get(k, v)

        for k, v in set_values.items():
            self[k] = v

    def save_file(self, path: Path = None, Raw: bool = False):
        """Populates the DocumentDictionary from a given dictionary

        Args:
            data_dict (dict): The dictionary to populate from
        """
        logging.debug(f"Writing document to {self['PATH']}")
        if self.update_content is True:
            self["CONTENT"] = add_backlinks_section(
                self["CONTENT"], self["BACKLINKS"]
            )

        self._write_document(self["CONTENT"], path if path else self["PATH"])


JSON_FIELDS = {"CROSSLINK": [], "ITEMS": {}}


@dataclass
class JsonDictionary:
    """A dictionary used for holding meta data

    Args:
        callabledict (callabledict): _description_
    """

    FILE: Path = field(default=Path())
    CROSSLINK: dict = field(default=JSON_FIELDS.copy())

    def load(self, file_path):
        """Load JSON data from a file."""
        with open(file_path, "r", encoding="utf-8") as f:
            self.CROSSLINK = load(f)

    def dump(self, file_path):
        """Dump JSON data to a file."""
        with open(file_path, "w", encoding="utf-8") as f:
            dump(self.CROSSLINK, f, indent=4)
