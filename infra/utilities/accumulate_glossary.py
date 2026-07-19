#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[CODE_SYNC: accumulate_glossary.py | STATUS: GOLDEN_COPY]
Version     : v2.5.2
Date        : 2026-07-19
Description : Automated token aggregation and spatial taxonomy validation compiler.
"""
import os
import re
import sys

# 1. Locate the physical script file, resolving any symlinks 6/26/modifications 
SCRIPT_PATH = os.path.realpath(__file__)  # e.g., .../infra/utilities/accumulate_glossary.py
UTILITIES_DIR = os.path.dirname(SCRIPT_PATH)  # .../infra/utilities

# 2. Navigate up to the repository root and target the docs directory
REPO_ROOT = os.path.abspath(os.path.join(UTILITIES_DIR, "..", ".."))
GLOSSARY_FILE = os.path.join(REPO_ROOT, "docs", "glossary.md")

# 3. Defensive check: Ensure the docs directory exists
os.makedirs(os.path.dirname(GLOSSARY_FILE), exist_ok=True)

SCHEMA_PATTERN = re.compile(r"^###\s+(.+?)\s+::\s+(.+?)$")

def load_existing_glossary(glossary_path):
    """
    Parses the existing glossary.md file into a structured dictionary.
    Returns: {term_lower: (case_preserved_term, category, definition_paragraph)}
    """
    entries = {}
    if not os.path.exists(glossary_path):
        return entries

    with open(glossary_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split content by the level 3 header token to isolate term definitions
    chunks = content.split("### ")
    for chunk in chunks:
        if not chunk.strip():
            continue
        lines = chunk.split("\n")
        header = lines[0].strip()
        
        # Reconstruct the header line to validate against schema
        match = SCHEMA_PATTERN.match(f"### {header}")
        if match:
            term = match.group(1).strip()
            category = match.group(2).strip()
            # Join the remaining lines of the chunk as a single paragraph definition
            definition = " ".join(lines[1:]).strip()
            # Remove any accidental double spacing caused by joining newlines
            definition = re.sub(r'\s+', ' ', definition)
            entries[term.lower()] = (term, category, definition)
    return entries

def parse_source_log(source_path):
    """
    Scans a raw log file for new glossary entries, respecting markdown code blocks.
    Returns: list of tuples (term, category, definition)
    """
    discovered = []
    if not os.path.exists(source_path):
        print(f"[-] Error: Source file {source_path} not found.")
        sys.exit(1)

    # The missing block that populates the 'lines' variable
    with open(source_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    idx = 0
    in_code_block = False

    while idx < len(lines):
        line = lines[idx].strip()

        if line.startswith("```"):
            in_code_block = not in_code_block
            idx += 1
            continue

        if in_code_block:
            idx += 1
            continue

        match = SCHEMA_PATTERN.match(line)
        if match:
            term = match.group(1).strip()
            category = match.group(2).strip()

            definition_lines = []
            next_idx = idx + 1
            while next_idx < len(lines):
                next_line = lines[next_idx].strip()
                if next_line.startswith("#") or next_line == "---" or not next_line:
                    if definition_lines:
                        break
                    next_idx += 1
                    continue
                definition_lines.append(next_line)
                next_idx += 1

            definition = " ".join(definition_lines).strip()
            definition = re.sub(r'\s+', ' ', definition)
            discovered.append((term, category, definition))
            idx = next_idx - 1
        idx += 1

    return discovered

def main():
    if len(sys.argv) < 2:
        print("[!] Usage: python accumulate_glossary.py <source_log.md>")
        sys.exit(1)

    source_log = sys.argv[1]
    glossary_path = GLOSSARY_FILE

    # 1. Load baseline state from disk
    all_entries = load_existing_glossary(glossary_path)
    print(f"[+] Loaded {len(all_entries)} baseline terms from {glossary_path}.")

    # 2. Extract entries from the target incoming log
    new_discoveries = parse_source_log(source_log)
    
    # 3. Merge new discoveries into master dictionary mapping
    new_count = 0
    for term, category, definition in new_discoveries:
        term_lower = term.lower()
        if term_lower not in all_entries:
            all_entries[term_lower] = (term, category, definition)
            print(f"[Identified New] {term} :: {category}")
            new_count += 1

    if new_count == 0 and os.path.exists(glossary_path):
        print(f"[+] Glossary up to date. No new terms written to {glossary_path}.")
        return

    # 4. Sort vocabulary alphabetically by lower keys and rewrite target file cleanly
    sorted_keys = sorted(all_entries.keys())

    with open(glossary_path, 'w', encoding='utf-8') as f:
        f.write("# Sunroom Ledger Central Glossary\n\n")
        for key in sorted_keys:
            term, category, definition = all_entries[key]
            f.write(f"### {term} :: {category}\n")
            f.write(f"{definition}\n\n")

    print(f"[+] Sync Complete. {glossary_path} updated. Total alphabetized terms: {len(sorted_keys)}")

if __name__ == "__main__":
    main()
