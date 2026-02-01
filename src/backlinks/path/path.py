from logging import logging
from pathlib import Path

logging.getLogger(__name__)


def empty_path():
    """Returns an empty PosixPath"""
    return Path("")


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


def generate_file_list(scan_path):
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
