import re

from backlinks.logging import logging
from backlinks.io.markdown import read_markdown_doc, write_markdown_doc
from backlinks.path.path import get_scan_relative_path
from backlinks.lib import type_of_link
 

# Constants

MARKDOWN_LINK_REGEX = r"\[([^\]]*)\]\(([^)]*\.md)\)"
LINK_REGEX = r"\[([^\]]+)\]\(([^)]+)\)"
MARKDOWN_HEADER_FINDERR = r"title:.*"
BACKLINKS_REGEX = r"# Backlinks\n"
# BACKLINKS_SECTION = r"# Backlinks\n(.*?)(?=\n# |\Z)"

BACKLINKS_SECTION = BACKLINKS_REGEX + r"(.*?)(?=\n# |\Z)"


logging.getLogger(__name__)



# ###
# Links
# ###
def find_backlinks_section(content, backlinks_regex_section=BACKLINKS_SECTION):
    """Extract backlinks section from content"""
    backlinks_match = re.search(backlinks_regex_section, content, re.DOTALL)
    if backlinks_match:
        logging.debug("Found backlinks section")
        return backlinks_match.group(1)
    logging.debug("Didn't find backlinks section")
    return ""


def split_on_backlinks_section(content, backlinks_regex=BACKLINKS_REGEX):
    """Extract backlinks section from content"""
    splitter = re.split(backlinks_regex, content)
    if len(splitter) == 1:
        logging.debug("Didn't find backlinks section")
        return [content, ""]

    main_body = "".join(splitter[0:-1])
    backlinks = splitter[-1]
    logging.debug("Found backlinks section")
    return [main_body, backlinks]


def find_markdown_links(content, markdown_link_reges=MARKDOWN_LINK_REGEX):
    """Find all markdown links in content"""
    if content == "":
        return []
    return re.findall(markdown_link_reges, content)


def find_links(content, link_regex=LINK_REGEX):
    """Find all markdown links in content"""
    if content == "":
        return {}
    res = re.findall(link_regex, content)
    return type_of_link(res)


def get_links(content: str, markdown_only: bool = True) -> tuple:
    """Extract markdown links from content

    Args:
        content (str): _description_
        markdown_only (bool, optional): _description_. Defaults to True.

    Returns:
        tuple: returns a tuple of two list,
                1 - all the links before backlings
                2 - all the links after backlings (empty list if backlinks doesn't exists)


    """
    if content == "":
        return find_links(""), find_links("")

    split_md = split_on_backlinks_section(content)

    if markdown_only:
        regex_pattern = MARKDOWN_LINK_REGEX
    else:
        regex_pattern = LINK_REGEX

    if len(split_md) <= 1:
        return [], []
    elif len(split_md) == 1:
        return find_links(split_md[0], regex_pattern), find_links("")
    else:
        return find_links(split_md[0], regex_pattern), find_links(
            split_md[1], regex_pattern
        )

_ = """
# ###
# markdown
# ###
def get_markdown_information(
    md_file_link: str, markdown_dict: dict, system_path: str
):

    knowledge_dict: dict = {
        "PATH": None,
        "REL_PATH": None,
        "BACKLINKS": [],
        "BACKLINKS_PATH": [],
        "LINKS": [],
        "LINKS_PATH": [],
        "NEED2UPDATE": False,
    }

    logging.debug(f"Generating the necessary infromation from {md_file_link}")
    md_content = read_markdown_doc(md_file_link)

    knowledge_dict["PATH"] = md_file_link
    knowledge_dict["REL_PATH"] = get_scan_relative_path(
        md_file_link, system_path
    )
    knowledge_dict["ID"] = None

    knowledge_dict["LINKS"], knowledge_dict["BACKLINKS"] = get_links(md_content)

    if len(knowledge_dict["BACKLINKS"]) > 0:
        knowledge_dict["BACKLINKS_PATH"] = [
            x for x in knowledge_dict["BACKLINKS"].keys()
        ]
    if len(knowledge_dict["LINKS"]) > 0:
        knowledge_dict["LINKS_PATH"] = [x for x in knowledge_dict["LINKS"].keys()]

    knowledge_dict["NEED2UPDATE"] = False

    yaml_dict = get_yaml_dict(md_content)
    knowledge_dict.update(yaml_dict)

    markdown_dict[knowledge_dict["REL_PATH"]] = knowledge_dict.copy()

    return markdown_dict
"""