#!/usr/bin/env python3
import argparse
import csv
import re
from pathlib import Path


def sanitize_node_name(file_path):
    """Convert file path to valid Mermaid node name"""
    # Remove leading slash and file extension, replace special chars
    name = Path(file_path).stem
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)


def read_csv_links(csv_path):
    """Read CSV file and extract original links only"""
    links = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["link_type"] == "original":
                links.append(
                    {
                        "source": row["source_file"],
                        "target": row["target_file"],
                        "status": row["status"],
                        "text": row["link_text"],
                    }
                )
    return links


def generate_mermaid_chart(links):
    """Generate Mermaid flowchart from links"""
    chart_lines = ["```mermaid", "flowchart TD"]

    # Track nodes to avoid duplicates
    nodes = set()

    for link in links:
        source_node = sanitize_node_name(link["source"])
        target_node = sanitize_node_name(link["target"])

        # Add node definitions
        if source_node not in nodes:
            source_display = Path(link["source"]).stem
            chart_lines.append(f'    {source_node}["{source_display}"]')
            nodes.add(source_node)

        if target_node not in nodes:
            target_display = Path(link["target"]).stem
            chart_lines.append(f'    {target_node}["{target_display}"]')
            nodes.add(target_node)

    # Add links with styling based on status
    for link in links:
        source_node = sanitize_node_name(link["source"])
        target_node = sanitize_node_name(link["target"])

        if link["status"] == "Valid":
            chart_lines.append(f"    {source_node} --> {target_node}")
        elif link["status"] == "Broken":
            chart_lines.append(f"    {source_node} -.-> {target_node}")
        else:  # Outside Root
            chart_lines.append(f"    {source_node} ==> {target_node}")

    chart_lines.append("```")
    return "\n".join(chart_lines)


def add_chart_to_markdown(md_path, chart_content):
    """Add or update Mermaid chart in markdown file"""
    md_path = Path(md_path)

    if md_path.exists():
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = ""

    # Remove existing chart
    content = re.sub(
        r"## Link Chart\n\n```mermaid\n.*?\n```", "", content, flags=re.DOTALL
    )

    # Add new chart
    chart_section = f"\n\n## Link Chart\n\n{chart_content}\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content + chart_section)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Mermaid chart from backlinks CSV"
    )
    parser.add_argument("csv_path", help="Path to backlinks CSV file")
    parser.add_argument("output_md", help="Output markdown file path")

    args = parser.parse_args()

    links = read_csv_links(args.csv_path)
    chart = generate_mermaid_chart(links)
    add_chart_to_markdown(args.output_md, chart)

    print(f"Mermaid chart added to {args.output_md}")
