import re
from secrets import token_hex

from backlinks.collector import CallableDict
from backlinks.io.document import read_document
from backlinks.logging import logging
from backlinks.path.path import empty_path, get_scan_relative_path

logging.getLogger(__name__)


YAML_REGEX = r"---\n(.*?)\n---"
DOCUMENT_FIELDS = {'PATH': empty_path(),
 'REL_PATH': '',
 'BACKLINKS': [],
 'BACKLINKS_PATH': [],
 'LINKS': [],
 'LINKS_PATH': [],
 'NEED2UPDATE': False,
 'CONTENT': '',
 'ID': None,
 'DESCRIPTION': '',
 'TAGS': [],
 'EDITOR': 'markdown',
 'TITLE': '',
 'DATECREATED': '',
 'PUBLISHED': '',
 'DATE': ''}


class DocumentDictionary(CallableDict):
    """A dictionary used for holding document meta data

    Args:
        callabledict (callabledict): _description_
    """

    def __init__(self, initial_data=None, call_on_get=False):
        if initial_data is None or not isinstance(initial_data, dict):
            initial_data = DOCUMENT_FIELDS.copy()
        super().__init__(initial_data=initial_data, call_on_get=call_on_get)
        self.MARKDOWN_LINK_FINDER = r"\[([^\]]*)\]\(([^)]*\.md)\)"
        self.LINK_FINDER = r"\[([^\]]+)\]\(([^)]+)\)"
        self.MARKDOWN_HEADER_FINDERR = r"title:.*"
        self.BACKLINKS_SELECTOR = r"# Backlinks\n(.*?)(?=\n# |\Z)"
        self.BACKLINKS_FINDER = r"# Backlinks\n"
        self.document_type = "markdown"


    def generate_id(self, print : bool =False) -> str:
        """Generates a unique ID for the document if it does not already have one

        Returns:
            None: The unique ID
        """
        self['ID'] = token_hex(nbytes=16)
        if print:
            logging.debug(f"Generated new ID for document: {self['ID']}")
    
    def find_links(self, *) -> list:
        """Find all links in content"""
        if self.document_type == "markdown":
            self._md_find_links(, *)

    def split_on_backlinks_section(self, content):
        """Extract backlinks section from content"""
        if self.document_type == "markdown":
            self._md_split_on_backlinks_section()

    def get_links(Self, *args, **kwargs) -> tuple:
        """Extract markdown links from content

        Args:
            markdown_only (bool, optional): _description_. Defaults to True.

        Returns:
            tuple: returns a tuple of two list,
                    1 - all the links before backlings
                    2 - all the links after backlings (empty list if backlinks doesn't exists)
        """
        if self.document_type == "markdown":
            self._md_get_links(*args, **kwargs)

    def yaml_headers(self, *args, **kwargs):
        """Extract YAML top portion as a dictionary"""
        if self.document_type == "markdown":
            self._md_yaml_dict(*args, **kwargs)

    def _md_yaml_header(self, content: str = '') -> str:
        """Find YAML header in document content"""
        if content != '':
            yaml_match = re.search(YAML_REGEX, content, re.DOTALL)
        else:
            yaml_match = re.search(YAML_REGEX, self['CONTENT'], re.DOTALL)

        if yaml_match:
            logging.debug(f"Found yaml headers {yaml_match}")
            return yaml_match.group(1)
        logging.debug("No yaml headers found")
        return ""


def yaml_to_dict(self, content: str = '', capitalize_keys: bool = False) -> dict:
    """Convert YAML content to dictionary"""
    logging.debug("Converting Yaml Headers to a dictionary")
    yaml_dict = {}
    for line in yaml_content.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            if capitalize_keys:
                key = key.upper()
            yaml_dict[key.strip()] = value.strip()
    return yaml_dict


def get_yaml_dict(content) -> dict:
    """Extract YAML top portion as a dictionary

    :param content: input markdown content
    :return: a dictionary of YAML fields, with the keys capitalized and all fields of YAML_FIELDS included
    :rtype: dict
    """
    logging.info("Begging to extract yaml headers")
    yaml_content = find_yaml_header(content)
    source_yaml_dict = yaml_to_dict(yaml_content, capitalize_keys=True)
    all_yaml_fields = set(YAML_FIELDS + list(source_yaml_dict.keys()))
    yaml_dict = {}
    for yf in all_yaml_fields:
        yaml_dict[yf] = source_yaml_dict.get(yf, None)

    yaml_dict["TAGS"] = (
        yaml_dict["TAGS"].split(",") if yaml_dict["TAGS"] else []
    )
    return yaml_dict





    def _md_find_links(self, content: str = '') -> list:
        """Find all markdown links in content"""
        if content != '':
            return re.findall(self.LINK_FINDER, content)
        
        return re.findall(self.LINK_FINDER, self['CONTENT'])
    

    def _md_split_on_backlinks_section(self, content: str = ''):
        """Extract backlinks section from markdown content"""
        if content != '':
            splitter = re.split(self.BACKLINKS_FINDER, content)
        else:
            splitter = re.split(self.BACKLINKS_FINDER, self['CONTENT'])

        if len(splitter) == 1:
            logging.debug("Didn't find backlinks section")
            return [content, ""]

        main_body = "".join(splitter[0:-1])
        backlinks = splitter[-1]
        logging.debug("Found backlinks section")
        return [main_body, backlinks]
 
    def _md_get_links(self, content: str, markdown_only: bool = True) -> tuple:
        """Extract markdown links from content

        Args:
            content (str): _description_
            markdown_only (bool, optional): _description_. Defaults to True.

        Returns:
            tuple: returns a tuple of two list,
                    1 - all the links before backlings
                    2 - all the links after backlings (empty list if backlinks doesn't exists)
        """
        if self['CONTENT'] == "":
            return self._md_find_links(""), self._md_find_links("")

        split_md = self._md_split_on_backlinks_section(content)
        if len(split_md) <= 1:
            return [], []
        elif len(split_md) == 1:
            if markdown_only:
                return find_markdown_links(split_md[0]), find_markdown_links("")
            return find_links(split_md[0]), find_links("")
        else:
            if markdown_only:
                return find_markdown_links(split_md[0]), find_markdown_links(
                    split_md[1]
                )
            return find_links(split_md[0]), find_links(split_md[1])


    def populate_from_file(self, path: Path, system_path: str, store_content: bool = False):
        """Populates the DocumentDictionary from a given dictionary

        Args:
            data_dict (dict): The dictionary to populate from
       """
        logging.debug(f"Generating the necessary infromation from {path}")
        self['CONTENT'] = self.read_document(path)
        self['PATH'] = path
        self["REL_PATH"] = get_scan_relative_path(
            path, system_path
        )

        self["LINKS"], self["BACKLINKS"] = self.get_links(self['CONTENT'])

        if len(self["BACKLINKS"]) > 0:
            self["BACKLINKS_PATH"] = [
                x[1] for x in self["BACKLINKS"]
            ]
        if len(self["LINKS"]) > 0:
            self["LINKS_PATH"] = [x[1] for x in self["LINKS"]]

        self["NEED2UPDATE"] = False

        yaml_dict = get_yaml_dict(self['CONTENT'])
        knowledge_dict.update(yaml_dict)

        markdown_dict[knowledge_dict["REL_PATH"]] = knowledge_dict.copy()


    def get_markdown_information(
        md_file_link: str, markdown_dict: dict, system_path: str
    ):
        """get's relevent information for each markdown file

        Args:
            md_file_link (_type_): _description_
            markdown_dict (dict): _description_
            system_dict (dict): _description_
        """
        return 
    






def find_markdown_links(content):
    """Find all markdown links in content"""
    return re.findall(MARKDOWN_LINK_FINDER, content)


def find_links(content):
    """Find all markdown links in content"""
    if content == "":
        return []
    return re.findall(LINK_FINDER, content)

