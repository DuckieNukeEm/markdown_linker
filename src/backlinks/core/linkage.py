from urllib.parse import urlparse

from backlinks.collector.book import BookDictionary
from backlinks.collector.document import DocumentDictionary
from backlinks.logging import logging

# ###
# Variables
# ###


###
# Functions
# ###
def post_linkage(
    source: DocumentDictionary,
    target: DocumentDictionary,
    link_type: str,
    link_status: str = "invalid",
) -> dict:
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


def make_Crosslink(Book: BookDictionary):
    """builds the links between markdown files and external files

    Args:
        markdown_dict (_type_): markdown dict
    """
    Crosslinks_list = Book.STORAGE_ENGINE.CROSSLINK

    for source_lnk, source_dic in BookDictionary.PAGES:
        for lnk, lnk_type in source_dic["LINKS"].keys():
            if lnk_type == "URL":
                Crosslinks_list.append(
                    post_linkage(
                        source_dic,
                        {"REL_PATH": lnk, "TITLE": urlparse(lnk).netloc},
                        "URL LINK",
                        "Valid",
                    )
                )
                continue

            try:
                if lnk in BookDictionary.PAGES.keys():

                    target_dic = BookDictionary.PAGES[lnk]
                    logging.debug(f"The {lnk} does have a target file")
                    Crosslinks_list.append(
                        post_linkage(
                            source_dic, target_dic, "Markedon Link", "Valid"
                        )
                    )
                    # Checking if we want backlinks
                    if target_dic["BACKLINK"] is not True:
                        logging.debug(
                            f"The {lnk} does have a target file, but doesn't want to backlink to it"
                        )
                        continue

                    if lnk in target_dic["BACKLINKS_PATH"]:
                        logging.debug(
                            f"backlinks exists from {lnk} to {source_lnk}"
                        )
                        Crosslinks_list.append(
                            post_linkage(
                                target_dic,
                                source_dic,
                                "Markdown Backlink",
                                "Valid",
                            )
                        )
                    else:
                        logging.debug(
                            f"backlinks DOES NOT exists from {lnk} to {source_lnk}"
                        )
                        target_dic.add_backlink(lnk)
                        Crosslinks_list.append(
                            post_linkage(
                                target_dic,
                                source_dic,
                                "Markdown Backlink",
                                "Added",
                            )
                        )
                    continue
                else:
                    Crosslinks_list.append(
                        post_linkage(
                            source_dic,
                            {"REL_PATH": lnk, "TITLE": ""},
                            "Unknown LINK",
                            "Invalid",
                        )
                    )
            except Exception as e:
                logging.error(f"Exception found when processing link {lnk}")
                print(f"Caught this error: {e}")


def markdown_crossrefrence(system_dict):
    """allows checking cross refrences between markdown files

    Args:
        system_dict (_type_): system dict with all the info
    """
    logging.info("Checking the link connections between all markdown documents")
    system_dict["LINKS_DATA"], crosswalk_update_list = (
        markdown_link_crosswalker(system_dict["MARKDOWNS_DICT"])
    )

    system_dict["UPDATE"] = {}
    system_dict["UPDATE"]["BACKLINKS"] = list(set(crosswalk_update_list))

    IDX = []
    for v, x in system_dict["UPDATE"].items():
        IDX = IDX + [y for y in x]

    system_dict["UPDATE"]["IDX"] = list(set(IDX))
    # system_dict['UPDATE']['IDX'] = list(set(system_dict['UPDATE'].values()))

    return system_dict
