import re

from backlinks.logging import logging

# Constants
YAML_FIELDS = [
    "ID",
    "TITLE",
    "DESCRIPTION",
    "PUBLISHED",
    "DATE",
    "TAGS",
    "EDITOR",
    "DATECREATED",
]
MARKDOWN_LINK_FINDER = r"\[([^\]]*)\]\(([^)]*\.md)\)"
LINK_FINDER = r"\[([^\]]+)\]\(([^)]+)\)"
MARKDOWN_HEADER_FINDERR = r"title:.*"
BACKLINKS_SELECTOR = r"# Backlinks\n(.*?)(?=\n# |\Z)"
BACKLINKS_FINDER = r"# Backlinks\n"


logging.getLogger(__name__)


# ###
# Markdown operators functions
# ###
def find_yaml_header(content):
    """Find YAML header in markdown content"""
    yaml_match = re.search(r"---\n(.*?)\n---", content, re.DOTALL)
    if yaml_match:
        logging.debug(f"Found yaml headers {yaml_match}")
        return yaml_match.group(1)
    logging.debug("No yaml headers found")
    return ""


def yaml_to_dict(yaml_content, capitalize_keys: bool = False) -> dict:
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
    """Extract YAML front matter as a dictionary

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


def find_backlinks_section(content):
    """Extract backlinks section from content"""
    backlinks_match = re.search(BACKLINKS_SELECTOR, content, re.DOTALL)
    if backlinks_match:
        logging.debug("Found backlinks section")
        return backlinks_match.group(1)
    logging.debug("Didn't find backlinks section")
    return ""


def split_on_backlinks_section(content):
    """Extract backlinks section from content"""
    splitter = re.split(BACKLINKS_FINDER, content)
    if len(splitter) == 1:
        logging.debug("Didn't find backlinks section")
        return [content, ""]

    main_body = "".join(splitter[0:-1])
    backlinks = splitter[-1]
    logging.debug("Found backlinks section")
    return [main_body, backlinks]


def find_markdown_links(content):
    """Find all markdown links in content"""
    return re.findall(MARKDOWN_LINK_FINDER, content)


def find_links(content):
    """Find all markdown links in content"""
    if content == "":
        return []
    return re.findall(LINK_FINDER, content)


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


def get_markdown_information(
    md_file_link: str, markdown_dict: dict, system_path: str
):
    """get's relevent information for each markdown file

    Args:
        md_file_link (_type_): _description_
        markdown_dict (dict): _description_
        system_dict (dict): _description_
    """
    knowledge_dict: dict[str, Any] = {
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
            x[1] for x in knowledge_dict["BACKLINKS"]
        ]
    if len(knowledge_dict["LINKS"]) > 0:
        knowledge_dict["LINKS_PATH"] = [x[1] for x in knowledge_dict["LINKS"]]

    knowledge_dict["NEED2UPDATE"] = False

    yaml_dict = get_yaml_dict(md_content)
    knowledge_dict.update(yaml_dict)

    markdown_dict[knowledge_dict["REL_PATH"]] = knowledge_dict.copy()

    return markdown_dict
