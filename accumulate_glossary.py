#!/usr/bin/env python3
import sys
import re
import pathlib

GLOSSARY_PATTERN = re.compile(r'^###\s+(?P<term>.+?)\s+::\s+(?P<category>.+?)\s*$')

def parse_lines(lines):
    entries = {}
    in_code_block = False
    
    for idx, line in enumerate(lines):
        # Toggle code block tracking to shield the regex from code snippets
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
            
        if in_code_block:
            continue
            
        match = GLOSSARY_PATTERN.match(line)
        if match:
            term = match.group('term').strip()
            category = match.group('category').strip()
            if idx + 1 < len(lines):
                definition = lines[idx + 1].strip()
                if definition and not definition.startswith('#'):
                    # Keying by lowercase ensures absolute deduplication
                    entries[term.lower()] = (term, category, definition)
                    
    return list(entries.values())

def generate_markdown(entries):
    """Compiles the structured data blocks into a clean Markdown table."""
    if not entries:
        return "No glossary terms found.\n"
    
    # Sort alphabetically by term
    sorted_entries = sorted(entries, key=lambda x: x[0].lower())
    
    output = [
        "# Master Glossary Index\n",
        "| Term | Category | Definition |",
        "| :--- | :--- | :--- |"
    ]
    for term, category, definition in sorted_entries:
        output.append(f"| **{term}** | `{category}` | {definition} |")
    
    return "\n".join(output) + "\n"

def main():
    # Scenario A: Standard Unix Pipe Input (e.g., cat file.md | python3 script.py)
    if not sys.stdin.isatty():
        lines = sys.stdin.readlines()
        entries = parse_lines(lines)
    
    # Scenario B: Target Path Argument (File or Directory)
    elif len(sys.argv) > 1:
        target_path = pathlib.Path(sys.argv[1])
        entries = []
        
        if target_path.is_file():
            with open(target_path, 'r', encoding='utf-8') as f:
                entries.extend(parse_lines(f.readlines()))
        elif target_path.is_dir():
            for md_file in target_path.glob('**/*.md'):
                # Avoid recursively scanning the generated glossary itself
                if md_file.name == "glossary_master.md":
                    continue
                with open(md_file, 'r', encoding='utf-8') as f:
                    entries.extend(parse_lines(f.readlines()))
    else:
        print("Usage: ./accumulate_glossary.py [file_or_directory_path] or pipe stdin", file=sys.stderr)
        sys.exit(1)

    # Output the compiled layout straight to stdout
    sys.stdout.write(generate_markdown(entries))

if __name__ == "__main__":
    main()
