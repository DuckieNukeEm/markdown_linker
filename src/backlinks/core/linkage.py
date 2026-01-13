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
                logging.debug(
                    f"found {target_md} is in the link list of {source_md}"
                )
                link_list[source_md].remove(target_md)
                Crosslinks_list.append(
                    post_linkage(source_dic, target_dic, "To Markdown", "Valid")
                )

                # if the source does link to the target, then the target NEEDS to backlink to source
                if source_md not in target_dic["BACKLINKS_PATH"]:
                    logging.debug(
                        f"{source_md} is NOT in the backlinks section for {target_md}"
                    )
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
                logging.debug(
                    f"found {source_md} is in the link list of {target_md}"
                )
                link_list[target_md].remove(source_md)
                Crosslinks_list.append(
                    post_linkage(target_dic, source_dic, "To Markdown", "Valid")
                )

                if target_md not in source_dic["BACKLINKS_PATH"]:
                    logging.debug(
                        f"{target_md} is NOT in the backlinks section for {source_md}"
                    )
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
