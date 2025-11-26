#!/usr/bin/env python3
import re
from pathlib import Path


def find_markdown_links(content):
    """Find all markdown links in content"""
    return re.findall(r"\[([^\]]*)\]\(([^)]*\.md)\)", content)


def generate_mermaid_graph(folder_path):
    """Generate mermaid graph code for markdown document relationships"""
    relationships = []

    for md_file in Path(folder_path).rglob("*.md"):
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        source_name = md_file.stem.replace(" ", "_").replace("-", "_")

        # Find all links in this file
        for link_text, target_file in find_markdown_links(content):
            target_path = (md_file.parent / target_file).resolve()
            if target_path.exists():
                target_name = target_path.stem.replace(" ", "_").replace(
                    "-", "_"
                )
                relationships.append(f"    {source_name} --> {target_name}")

    # Generate mermaid code
    mermaid_code = "graph TD\n"
    for relationship in sorted(set(relationships)):
        mermaid_code += relationship + "\n"

    return mermaid_code


if __name__ == "__main__":
    folder_path = input("Enter folder path: ").strip()
    mermaid_graph = generate_mermaid_graph(folder_path)
    print(mermaid_graph)
