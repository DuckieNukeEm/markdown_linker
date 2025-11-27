#!/usr/bin/env python3
import argparse
import csv
import logging
import os
import re
from collections import defaultdict
from pathlib import Path

# Hard-coded scan path - modify this as needed
SCAN_PATH = (
    None  # Set to your desired scan path, e.g., "/path/to/scan" or "C:\\MyDocs"
)
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
BACKLINKS_SELECTOR=r'# Backlinks\n(.*?)(?=\n# |\Z)'
BACKLINKS_FINDER=r'# Backlinks\n'

# Testing purposes only
SYS_PATH = Path("/home/asmodi/Code/git/markdown_linker/test/markdown/SlipBox")

# ###
# System functions
# ###


def setup_logging(log_level, log_file=None):
    """Setup logging configuration"""
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    handlers = []

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(levelname)s: %(message)s")
    )
    handlers.append(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=level_map.get(log_level.upper(), logging.INFO),
        handlers=handlers,
        force=True,
    )


def generate_sys_dict() -> dict:
    return {"SYSTEM_PATH": SYS_PATH, "MARKDOWNS_DICT": {}}


def quote_it(Input_String: str) -> str:
    """Quote string for CSV"""
    if not Input_String.startswith('"'):
        Input_String = '"' + Input_String

    if not Input_String.endswith('"'):
        Input_String = Input_String + '"'

    return Input_String


def add_headers_dict(Headers_Dict, file_path, title):
    if Headers_Dict.get(file_path) is not None:
        return Headers_Dict
    elif Headers_Dict.get(file_path) is None:
        Headers_Dict[file_path] = title
    else:
        logging.debug(f"No header found in {file_path.name}")
        Headers_Dict[file_path] = (
            file_path.stem
        )  # Fallback to filename without extension
    return Headers_Dict


# ###
# CSV functions
# ###
def load_csv_data(csv_path):
    """Load existing CSV data"""
    data = {}
    if csv_path.exists():
        logging.info(f"Loading existing CSV data from {csv_path}")
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["source_file"], row["target_file"])
                data[key] = row
        logging.debug(f"Loaded {len(data)} existing link records")
    else:
        logging.info("No existing CSV file found, starting fresh")
    return data


def save_csv_data(csv_path, links_data):
    """Save links data to CSV"""
    logging.info(f"Saving {len(links_data)} link records to {csv_path}")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "source_file",
            "source_title",
            "target_file",
            "target_title",
            "link_text",
            "status",
            "hierarchy_level",
            "link_type",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Sort by hierarchy level then by file path
        sorted_data = sorted(
            links_data, key=lambda x: (x["hierarchy_level"], x["source_file"])
        )
        writer.writerows(sorted_data)
    logging.debug("CSV file saved successfully")


# ###
# Path functions
# ###


def get_hierarchy_level(file_path, scan_path):
    """Get hierarchy level relative to scan path"""
    try:
        rel_path = Path(file_path).relative_to(scan_path)
        return len(rel_path.parts) - 1
    except ValueError:
        return -1  # Outside scan path


def get_scan_relative_path(file_path, scan_path):
    """Convert absolute path to scan-relative path"""
    try:
        logging.debug(
            f"Converting {file_path} to relative path from {scan_path}"
        )
        rel_path = Path(file_path).relative_to(scan_path)
        return str(Path("/") / scan_path.name / rel_path)
    except ValueError:
        return str(file_path)  # Return absolute if outside scan path


def get_scan_absolute_path(file_path, scan_path):
    """Convert scan-relative path to absolute path"""
    logging.debug(f"Converting {file_path} to absolute path from {scan_path}")
    str_file_path = str(file_path)
    offset = 0
    if str_file_path.startswith("/"):
        offset = 1
    if str_file_path.startswith(scan_path.name) or str_file_path.startswith(
        "/" + scan_path.name
    ):
        file_path = str_file_path[offset + len(scan_path.name) :].lstrip("/")
    abs_path = (Path(scan_path) / Path(file_path)).resolve()
    return abs_path


def generate_link_list(scan_path):
    """Generates a list of markdown files to run through"""
    scan_path = Path(scan_path).resolve()
    logging.info(f"Scanning documents in {scan_path}")
    md_links = list(scan_path.rglob("*.md"))
    logging.info(f"Found {len(md_links)} markdown files")
    return md_links


def abs_to_relative_path(link_path, base_path, modifier_path="/"):
    """Convert absolute path to relative path and clean up"""
    try:
        logging.debug(
            f"Converting {link_path} to relative path from {base_path}"
        )
        rel_path = Path(link_path).relative_to(base_path)
        return rel_path
    except ValueError:
        return link_path  # Return absolute if outside base path


def relative_to_abs_path(file_path, scan_path):
    """Convert scan-relative path to absolute path"""
    logging.debug(f"Converting {file_path} to absolute path from {scan_path}")
    str_file_path = str(file_path)
    offset = 0
    if str_file_path.startswith("/"):
        offset = 1
    if str_file_path.startswith(scan_path.name) or str_file_path.startswith(
        "/" + scan_path.name
    ):
        file_path = str_file_path[offset + len(scan_path.name) :].lstrip("/")
    abs_path = (Path(scan_path) / Path(file_path)).resolve()
    return abs_path


# ###
# Markdown operators functions
# ###
def find_yaml_header(content):
    """Find YAML header in markdown content"""
    yaml_match = re.search(r"---\n(.*?)\n---", content, re.DOTALL)
    if yaml_match:
        logging.debug(f"Found yaml headers {yaml_match}")
        return yaml_match.group(1)
    logging.debug(f"No yaml headers found")
    return ""


def yaml_to_dict(yaml_content, capitalize_keys: bool = False) -> dict:
    """Convert YAML content to dictionary"""
    logging.debug(f"Converting Yaml Headers to a dictionary")
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
    logging.info(f"Begging to extract yaml headers")
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



def read_markdown_doc(markdon_doc_filepath: str):
    """Function that opens a markdown file"""
    # logging.debug(f"Processing {markdon_doc_filepath}")
    with open(markdon_doc_filepath, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    return markdown_content


def write_markdown_doc(markdon_doc_filepath: str, content: str):
    """Function that writes a markdown file"""
    with open(markdon_doc_filepath, "w", encoding="utf-8") as f:
        f.write(content)
    logging.debug(f"Wrote updated content to {markdon_doc_filepath}")


def find_backlinks_section(content):
    """Extract backlinks section from content"""
    backlinks_match = re.search(
        BACKLINKS_SELECTOR, content, re.DOTALL
    )
    if backlinks_match:
        logging.debug(f"Found backlinks section")
        return backlinks_match.group(1)
    logging.debug(f"Didn't find backlinks section")
    return ""


def split_on_backlinks_section(content):
    """Extract backlinks section from content"""
    splitter = re.split(BACKLINKS_FINDER, content)
    if len(splitter) == 1:
        logging.debug(f"Didn't find backlinks section")
        return [content, ""]

    main_body = "".join(splitter[0:-1])
    backlinks = splitter[-1]
    logging.debug(f"Found backlinks section")
    return [main_body, backlinks]


def find_markdown_links(content):
    """Find all markdown links in content"""
    return re.findall(MARKDOWN_LINK_FINDER, content)


def find_links(content):
    """Find all markdown links in content"""
    return re.findall(LINK_FINDER, content)


def get_links(content: str, markdown_only: bool = True) -> tuple[list]:
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
        return [], []
    
    split_md = split_on_backlinks_section(content)
    if len(split_md) <= 1:
        return [], []
    elif len(split_md) == 1:
        if markdown_only:
            return find_markdown_links(split_md[0]), []
        return find_links(split_md[0]), []
    else:
        if markdown_only:
            return find_markdown_links(split_md[0]), find_markdown_links(
                split_md[1]
            )
        return find_links(split_md[0]), find_links(split_md[1])


def get_existing_backlinks(backlink_section):
    """Extract existing backlinks from backlink section"""
    if backlink_section == "":
        return []
    return find_markdown_links(backlink_section)


def get_markdown_information(
    md_file_link: str, markdown_dict: dict, system_path: str
):
    """get's relevent information for each markdown file

    Args:
        md_file_link (_type_): _description_
        markdown_dict (dict): _description_
        system_dict (dict): _description_
    """
    knowledge_dict: dict[str] = {
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


# ###
# Internal Logic
# ###


def populate_markdown_dictionary(md_file_links, system_dict: str):
    """Populates a dictionary with markdown file information

    Args:
        md_file_links (_type_): _description_
    """
    logging.info(f"Loading all {len(md_file_links)} markdown information")
    sys_path = system_dict["SYSTEM_PATH"]

    markdown_dict = system_dict["MARKDOWNS_DICT"]
    for md_file in md_file_links:
        markdown_dict = get_markdown_information(
            md_file, markdown_dict, sys_path
        )

    system_dict["MARKDOWNS_DICT"] = markdown_dict
    return system_dict


def post_linkage(
    source: dict, target: dict, link_type: str, link_status: str = "invalid"
):
    return {
        "source_file": source["REL_PATH"],
        "source_title": source["TITLE"],
        "target_file": target["REL_PATH"],
        "target_title": target["TITLE"],
        "status": link_status,
        "link_type": link_type,
    }


def pull_markdown_link_list(markdown_dict):
    link_list = {}
    for md, md_dic in markdown_dict.items():
        link_list[md] = md_dic["LINKS_PATH"].copy()
    return link_list


def markdown_link_crosswalker(markdowns_dict):
    """builds the links between markdown files and external files

    Args:
        markdown_dict (_type_): markdown dict
    """

    Crosslinks_list = []
    markdown_list = list(markdowns_dict.items())
    update_list = []
    link_list = pull_markdown_link_list(markdowns_dict)

    tracker_idx = 0

    # checking that these files do crosslink
    while tracker_idx < len(markdowns_dict):
        # Getting current source markdown file and its data
        source_md, source_dic = markdown_list[tracker_idx]
        next_tracker_idx = tracker_idx + 1

        while next_tracker_idx < len(markdowns_dict):
            target_md, target_dic = markdown_list[next_tracker_idx]

            # Check if source links to target
            if target_md in source_dic["LINKS_PATH"]:
                logging.debug(f"found {target_md} is in the link list of {source_md}")
                link_list[source_md].remove(target_md)
                Crosslinks_list.append(
                    post_linkage(source_dic, target_dic, "To Markdown", "Valid")
                )

                # if the source does link to the target, then the target NEEDS to backlink to source
                if source_md not in target_dic["BACKLINKS_PATH"]:
                    logging.debug(f"{source_md} is NOT in the backlinks section for {target_md}")
                    update_list.append(target_md)
                    target_dic["NEED2UPDATE"] = True
                    target_dic["BACKLINKS_PATH"].append(
                        (source_dic["TITLE"], source_md)
                    )
                Crosslinks_list.append(
                    post_linkage(
                        target_dic, source_dic, "Markdown Backlink", "Valid"
                    )
                )

            # same as above, just flipped
            if source_md in target_dic["LINKS_PATH"]:
                logging.debug(f"found {source_md} is in the link list of {target_md}")
                link_list[target_md].remove(source_md)
                Crosslinks_list.append(
                    post_linkage(target_dic, source_dic, "To Markdown", "Valid")
                )

                if target_md not in source_dic["BACKLINKS_PATH"]:
                    logging.debug(f"{target_md} is NOT in the backlinks section for {source_md}")
                    update_list.append(source_md)
                    source_dic["NEED2UPDATE"] = True
                    source_dic["BACKLINKS_PATH"].append(
                        (target_dic["TITLE"], target_md)
                    )
                Crosslinks_list.append(
                    post_linkage(
                        source_dic, target_dic, "Markdown Backlink", "Valid"
                    )
                )
            next_tracker_idx += 1
        tracker_idx += 1
        if link_list[source_md] == []:
            del link_list[source_md]

    # Now, we've gone through all the markdown docs, and there are records that don't tie to anything
    # either due to files don't exists, or are formatted wrong, or otherwise
    for md_file, md_link_list in link_list:
        md_dict = markdowns_dict[md_file]
        for links in md_link_list:
            if links.lower().starts_with("http"):
                tar = {"REL_PATH": links, "TITLE": links}
                Crosslinks_list.append(
                    post_linkage(md_dict, tar, "http", "Valid")
                )
            elif links.lower().ends_with(".md"):
                tar = {"REL_PATH": links, "TITLE": links}
                Crosslinks_list.append(
                    post_linkage(md_dict, tar, "To Markdown", "Broken")
                )

    # update_list = list(set(update_list))
    update_list
    return Crosslinks_list, update_list


def markdown_crossrefrence(system_dict):
    """allows checking cross refrences between markdown files

    Args:
        system_dict (_type_): system dict with all the info
    """
    logging.info(f"Checking the link connections between all markdown documents")
    system_dict["LINKS_DATA"], crosswalk_update_list = (
        markdown_link_crosswalker(system_dict["MARKDOWNS_DICT"])
    )

    system_dict['UPDATE'] = {} 
    system_dict['UPDATE']['BACKLINKS'] = list(set(crosswalk_update_list))
    
    IDX = []
    for v, x in system_dict['UPDATE'].items():
        IDX = IDX + [y for y in x]

    system_dict['UPDATE']['IDX'] = list(set(IDX)) 
    #system_dict['UPDATE']['IDX'] = list(set(system_dict['UPDATE'].values()))

    return system_dict


# ###
# Updater
# ###

# ###
# OLD CODE
# ###


def find_markdown_title(content):
    """Find all markdown links in content"""
    ret_str = re.findall(MARKDOWN_HEADER_FINDERR, content)[0]
    ret_str = ret_str.replace("title:", "").strip()
    # ret_str = quote_it(ret_str)
    return ret_str


def scan_documents(scan_path):
    """Scan all markdown files and build comprehensive link data"""
    scan_path = Path(scan_path).resolve()
    logging.info(f"Scanning documents in {scan_path}")
    csv_path = scan_path / "backlinks.csv"
    # existing_data = load_csv_data(csv_path)

    markdown_header = {}  # Map of file path to its header/title
    links_data = []
    backlinks_map = defaultdict(set)
    md_files = list(scan_path.rglob("*.md"))

    logging.info(f"Found {len(md_files)} markdown files")

    for md_file in md_files:
        content = read_markdown_doc(md_file)

        links_found = find_markdown_links(content)
        if links_found:
            logging.debug(f"Found {len(links_found)} links in {md_file.name}")
        print(links_found)
        for link_text, target_file in links_found:
            # Handle links relative to scan directory
            if target_file.startswith("/"):
                # Link is scan-relative (e.g., /TESTDIR/docs/file.md)
                target_parts = Path(target_file).parts[1:]  # Remove leading '/'
                if (
                    target_parts
                    and target_parts[0].upper() == scan_path.name.upper()
                ):
                    # Link points within scan structure - convert to absolute path
                    rel_path = (
                        Path(*target_parts[1:])
                        if len(target_parts) > 1
                        else Path(".")
                    )
                    target_path = (scan_path / rel_path).resolve()
                    logging.debug(
                        f"Resolved scan-relative link {target_file} to {target_path}"
                    )
                else:
                    # Link points outside scan structure
                    target_path = Path(target_file)
            else:
                # Link is relative to current file location
                target_path = (md_file.parent / target_file).resolve()

            # Determine status - check existence with absolute path
            if target_path.exists():
                if scan_path in target_path.parents or target_path == scan_path:
                    status = "Valid"
                else:
                    status = "Outside Root"
                    logging.warning(
                        f"Link outside scan path: {md_file.name} -> {target_file}"
                    )
            else:
                status = "Broken"
                logging.error(
                    f"Broken link: {md_file.name} -> {target_file} (resolved to {target_path})"
                )

            # Convert to scan-relative paths for CSV
            source_rel = get_scan_relative_path(md_file, scan_path)
            target_rel = get_scan_relative_path(target_path, scan_path)

            # Get or find titles/headers
            title_found = find_markdown_title(content)
            if title_found:
                logging.debug(f"Found header in {md_file.name}: {title_found}")

            markdown_header = add_headers_dict(
                markdown_header, md_file, title_found
            )

            if (
                markdown_header.get(target_path) is None
                and target_path.exists()
            ):
                with open(target_path, "r", encoding="utf-8") as tf:
                    tcontent = tf.read()
                ttitle_found = find_markdown_title(tcontent)

                markdown_header = add_headers_dict(
                    markdown_header, target_path, ttitle_found
                )

            # Add original link
            links_data.append(
                {
                    "source_file": source_rel,
                    "source_title": markdown_header[md_file],
                    "target_file": target_rel,
                    "target_title": markdown_header[target_path],
                    "link_text": link_text,
                    "status": status,
                    "hierarchy_level": get_hierarchy_level(md_file, scan_path),
                    "link_type": "original",
                }
            )

            # Add backlink entry regardless of validity
            links_data.append(
                {
                    "source_file": target_rel,
                    "source_title": markdown_header[target_path],
                    "target_file": source_rel,
                    "target_title": markdown_header[md_file],
                    "link_text": "",
                    "status": status,  # Use same status as original link
                    "hierarchy_level": get_hierarchy_level(
                        target_path, scan_path
                    ),
                    "link_type": "backlink",
                }
            )

            if status == "Valid":
                backlinks_map[target_rel].add(
                    (source_rel, markdown_header[md_file])
                )

    save_csv_data(csv_path, links_data)
    return backlinks_map


def add_backlinks(scan_path):
    """Add backlinks to markdown files"""
    scan_path = Path(scan_path).resolve()
    backlinks_map = scan_documents(scan_path)

    files_updated = 0
    for target_file_rel, source_files_rel in backlinks_map.items():
        # Convert scan-relative path back to absolute for file operations
        if target_file_rel.startswith("/" + scan_path.name):
            rel_part = target_file_rel[len("/" + scan_path.name) :].lstrip("/")
            target_path = scan_path / rel_part if rel_part else scan_path
        else:
            target_path = Path(target_file_rel)  # Outside scan path, use as-is

        logging.debug(f"Processing backlinks for {target_path.name}")

        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()

        existing_backlinks = get_existing_backlinks(content)

        # Remove existing backlinks section
        content = re.sub(
            r"\n# Backlinks\n.*?(?=\n# |\Z)", "", content, flags=re.DOTALL
        )

        # Build new backlinks section with only new links
        new_backlinks = []
        for source_file_rel in source_files_rel:
            # Convert scan-relative path back to absolute for path calculations
            if False:
                print(source_file_rel)
                if source_file_rel[0].startswith("/" + scan_path.name):
                    rel_part = source_file_rel[0][
                        len("/" + scan_path.name) :
                    ].lstrip("/")
                    print(rel_part)
                    source_path = (
                        scan_path / rel_part if rel_part else scan_path
                    )
                    print(rel_part, source_path)
                else:
                    source_path = Path(
                        source_file_rel[0]
                    )  # Outside scan path, use as-is
            # source_path = Path(source_file_rel[0])  # Outside scan path, use as-is
            # rel_path = os.path.relpath(source_path, target_path.parent)
            rel_path = source_file_rel[0]
            if rel_path not in existing_backlinks:
                # source_name = source_path.stem
                new_backlinks.append(f"- [{source_file_rel[1]}]({rel_path})")
            # print(source_path, source_path.stem, rel_path, existing_backlinks)

        if new_backlinks:
            # Remove existing backlinks section
            content = re.sub(
                r"\n# Backlinks\n.*?(?=\n# |\Z)", "", content, flags=re.DOTALL
            )

            logging.info(
                f"Adding {len(new_backlinks)} backlinks to {target_path.name}"
            )
            backlinks_section = (
                "\n# Backlinks\n\n" + "\n".join(new_backlinks) + "\n"
            )

            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content + backlinks_section)
            files_updated += 1

    logging.info(f"Updated {files_updated} files with backlinks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate backlinks for markdown files"
    )
    parser.add_argument(
        "scan_path", nargs="?", help="Folder path to scan for markdown files"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level",
    )
    parser.add_argument("--log-file", help="Log file path (optional)")

    args = parser.parse_args()

    setup_logging(args.log_level, args.log_file)

    # Use SCAN_PATH if defined, otherwise use command line arg or prompt
    if SCAN_PATH:
        scan_path = SCAN_PATH
        logging.info(f"Using hard-coded SCAN_PATH: {SCAN_PATH}")
    else:
        scan_path = args.scan_path or input("Enter scan folder path: ").strip()

    try:
        add_backlinks(scan_path)
        logging.info("Backlinks processing completed successfully!")
        print(
            "Backlinks added successfully! Check backlinks.csv for link analysis."
        )
    except Exception as e:
        logging.error(f"Error processing backlinks: {e}")
        raise
