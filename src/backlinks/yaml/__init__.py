from re import DOTALL, search
from backlinks.logging import logging

# ###
# Variables
# ###

logging.getLogger(__name__)
META_REGEX = r"---\n(.*?)\n---"


META_FIELDS = [
    "ID",
    "TITLE",
    "DESCRIPTION",
    "PUBLISHED",
    "DATE",
    "TAGS",
    "EDITOR",
    "DATECREATED",
]


# ###
# Functions
# ###
def isolate_metadata(content: str, meta_regex=META_REGEX) -> str:
    """Find metada header in markdown content"""
    meta_match = search(meta_regex, content, DOTALL)
    if meta_match:
        logging.debug(f"Found metadata content {meta_match}")
        return meta_match.group(1)
    logging.debug("No yaml content found")
    return ""


def load_meta_to_dict(meta_content, capitalize_keys: bool = False) -> dict:
    """Convert meta content to dictionary"""
    logging.debug("Converting Yaml Headers to a dictionary")
    meta_dict = {}
    for line in meta_content.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            if capitalize_keys:
                key = key.upper()
            meta_dict[key.strip()] = value.strip()
    return meta_dict


def meta_to_dict(content) -> dict:
    """Extract metadat headers and returns it as a dictionary

    :param content: input markdown content
    :return: a dictionary of metadat fields, with the keys capitalized and all fields of META_FIELDS included
    :rtype: dict
    """
    logging.info("Begging to extract metadata headers")
    meta_content = isolate_metadata(content)
    source_dict = load_meta_to_dict(meta_content, capitalize_keys=True)

    missing_fields = [x for x in META_FIELDS if x not in source_dict.keys()]
    for mf in missing_fields:
        source_dict[mf] = None

    return source_dict
