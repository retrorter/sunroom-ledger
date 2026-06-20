#!/usr/bin/env python3
import os
import re
from pathlib import Path

def run_unified_ingestion():
    # 1. Coordinate Repository Environment Paths
    repo_root = Path(__file__).parent.resolve()
    incoming_dir = repo_root / "incoming"
    inventory_dir = repo_root / "inventory"
    prop_dir = repo_root / "propagation-logs"
    glossary_file = repo_root / "docs" / "glossary.md"
    catch_all_file = repo_root / "unclassified-logs.md"

    # Ensure targeted spatial directories exist
    incoming_dir.mkdir(exist_ok=True)
    inventory_dir.mkdir(exist_ok=True)
    prop_dir.mkdir(exist_ok=True)
    glossary_file.parent.mkdir(exist_ok=True)

    # 2. Dynamically Locate Ingestion Source (Saves download suffix collisions)
    source_files = sorted(list(incoming_dir.glob("*.md")), key=os.path.getmtime)
    if not source_files:
        print(f"[ERROR] No markdown data export found within: {incoming_dir.relative_to(repo_root)}/")
        print("Drop your browser markdown export file directly into that directory to proceed.")
        return
    
    raw_file_path = source_files[-1]  # Pulls the most recently modified markdown file
    print(f"[INFO] Initializing ingestion matrix from target: {raw_file_path.name}")
    
    with open(raw_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 3. Establish the Structural Classification Routing Matrix
    ROUTING_MATRIX = [
        {
            "target_file": inventory_dir / "ficus-canopy.md",
            "keywords": ["ficus", "audrey", "ruby", "tineke", "stipule", "girdling", "layering", "auxin", "bop"]
        },
        {
            "target_file": inventory_dir / "heirloom-aloes.md",
            "keywords": ["aloe", "pup", "rhizome", "debridement", "heirloom", "vascular"]
        },
        {
            "target_file": inventory_dir / "monstera-deliciosa.md",
            "keywords": ["monstera", "deliciosa", "happy frog", "propagation"]
        },
        {
            "target_file": prop_dir / "2026-june-herbs.md",
            "keywords": ["thyme", "basil", "rosemary", "mint", "spearmint", "bolting", "death plug", "herbs", "arugula", "brassica", "sow"]
        },
        {
            "target_file": repo_root / "technical-deep-dives.md",
            "keywords": ["btrfs", "snapper", "ntp", "stratum", "linux", "y2k", "git", "ingest.py", "geany", "database", "wc", "awk", "tmux", "powerline", "vscodium", "alias", "dotfiles", "less", "vim"]
        }
    ]

    # 4. Determine Truncation Bounds (Anchors)
    start_index = 0
    found_anchor = False
    
    # Priority A: Check for the Contiguous System Sync Point Marker
    for idx, line in enumerate(lines):
        if "SYSTEM_SYNC_POINT" in line:
            start_index = idx
            found_anchor = True
            break
            
    # Priority B: Fall back to historical text anchor if no system token exists
    if not found_anchor:
        for idx, line in enumerate(lines):
            if "plastic pot happy frog potting soil" in line:
                start_index = idx
                # Backtrack to catch the preceding "# you asked" block cleanly
                while start_index > 0 and not lines[start_index].lower().startswith("# you asked"):
                    start_index -= 1
                found_anchor = True
                break

    if found_anchor:
        print(f"[SUCCESS] Boundary anchor verified at line {start_index}. Truncating legacy log drift.")
        active_lines = lines[start_index:]
        # line below used for full dump to catch exception for fallthrough else
        # active_lines = lines
    else:
        print("[WARN] No standard boundary anchors found. Processing raw text from index 0.")
        active_lines = lines

    # 5. Core State-Machine Turn Parser & Dynamic Router
    current_prompt = []
    current_response = []
    state = None

    def execute_routing(prompt_block, response_block):
        prompt_str = "".join(prompt_block).strip()
        response_str = "".join(response_block).strip()
        combined_payload = f"{prompt_str}\n\n{response_str}"
        search_payload = combined_payload.lower()

        # Step 5a: Sift for and isolate Glossary Entries natively on the fly
        glossary_pattern = r"(###\s+[^:\n]+\s+::\s+[^\n]+)\n+([^\n#]+)"
        glossary_entries = re.findall(glossary_pattern, response_str)
        if glossary_entries:
            with open(glossary_file, "a", encoding="utf-8") as gf:
                if glossary_file.stat().st_size == 0:
                    gf.write("# Sunroom & Technical Glossary\n\n")
                for header, definition in glossary_entries:
                    gf.write(f"{header}\n{definition}\n\n")
            print(f"   [GLOSSARY] -> Extracted {len(glossary_entries)} term(s) to docs/{glossary_file.name}")

        # Step 5b: Evaluate explicit developer-overridden tags: ## [ROUTING: filename]
        explicit_match = re.search(r"##\s+\[ROUTING:\s*([\w-]+)\]", combined_payload)
        
		# Extract the replacement out of the f-string expression to avoid pre-3.12 backslash limits
        formatted_prompt = prompt_str.replace('\n', '\n>')
        
        constructed_record = (
            f"## Interaction Record\n\n"
            f"### User Prompt\n>{formatted_prompt}\n\n"
            f"### System Response\n{response_str}\n\n"
            f"---\n\n"
        )

        if explicit_match:
            override_name = f"{explicit_match.group(1)}.md"
            override_path = prop_dir / override_name
            with open(override_path, "a", encoding="utf-8") as out_f:
                out_f.write(constructed_record)
            print(f"[EXPLICIT OVERRIDE] -> {override_name}")
            return

        # Step 5c: Drop through to standard keyword matrix scan
        for route in ROUTING_MATRIX:
            if any(keyword in search_payload for keyword in route["keywords"]):
                with open(route["target_file"], "a", encoding="utf-8") as out_f:
                    out_f.write(constructed_record)
                print(f"[ROUTED] -> {route['target_file'].relative_to(repo_root)}")
                return

        # Step 5d: Fallback bucket for unclassified content
        with open(catch_all_file, "a", encoding="utf-8") as out_f:
            out_f.write(constructed_record)
        print(f"[CATCH-ALL] -> {catch_all_file.name}")

    # Run state machine loop across text stream
    for line in active_lines:
        line_lower = line.lower()
        if line_lower.startswith("# you asked"):
            if current_prompt and current_response:
                execute_routing(current_prompt, current_response)
                current_prompt = []
                current_response = []
            state = "PROMPT"
            continue
        elif line_lower.startswith("# gemini response"):
            state = "RESPONSE"
            continue

        if state == "PROMPT":
            current_prompt.append(line)
        elif state == "RESPONSE":
            current_response.append(line)

    # Process final segment remaining in buffer at EOF
    if current_prompt and current_response:
        execute_routing(current_prompt, current_response)

    print("[STATUS] Synchronization matrix pipeline run complete.")

if __name__ == "__main__":
    run_unified_ingestion()
