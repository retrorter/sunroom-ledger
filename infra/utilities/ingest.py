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
    logs_dir = repo_root / "logs"
    archive_dir = logs_dir / "archive"
    docs_dir = repo_root / "docs"
    catch_all_file = repo_root / "unclassified-logs.md"
    offtopic_file = logs_dir / "offtopic_history.md"

    # Ensure targeted spatial directories exist
    incoming_dir.mkdir(exist_ok=True)
    inventory_dir.mkdir(exist_ok=True)
    prop_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    archive_dir.mkdir(exist_ok=True)
    docs_dir.mkdir(exist_ok=True)

    # 2. Dynamically Locate All Ingestion Sources (Sorted Chronologically)
    source_files = sorted(list(incoming_dir.glob("*.md")), key=os.path.getmtime)
    if not source_files:
        print(f"[ERROR] No markdown data export found within: {incoming_dir.relative_to(repo_root)}/")
        print("Drop your browser markdown export files directly into that directory to proceed.")
        return
    
    print(f"[INFO] Found {len(source_files)} file(s) queued for ingestion. Processing pipeline...")

    # Define Category-Level Classification Routing Matrix
    ROUTING_MATRIX = [
        {
            "target_file": inventory_dir / "arids.md",
            "keywords": ["aloe", "pup", "debridement", "heirloom", "terracotta", "crassula", "ovata", "ripple", "jade", "kalanchoe", "apical", "succulent", "succulents", "top dress", "sansevieria"]
        },
        {
            "target_file": inventory_dir / "tropicals.md",
            "keywords": ["ficus", "audrey", "ruby", "tineke", "stipula", "stipule", "girdling", "layering", "auxin", "monstera", "deliciosa", "happy frog", "propagation", "philodendron", "bop", "strelitzia", "nicolai", "bird of paradise", "unfurling", "sheathed", "aroid"]
        },
        {
            "target_file": inventory_dir / "infrastructure.md",
            "keywords": ["lighting", "utilitech", "tray", "pvc", "pp", "hdpe", "pots", "orchid", "ballast", "rainsoft", "carbon", "hardware", "racks", "plastic", "embrittlement", "welding", "creep", "fatigue", "uv"]
        },
        {
            "target_file": inventory_dir / "crops.md",
            "keywords": ["jalapeno", "pepper", "ginger", "rhizome", "macronutrient", "monty", "emulsion", "nightshades", "banana", "blossom-end", "calcium"]
        },
        {
            "target_file": inventory_dir / "herbs.md",
            "keywords": ["thyme", "basil", "rosemary", "mint", "spearmint", "death plug", "herbs", "arugula", "sowing", "1020", "biomass", "pinching"]
        },
        {
            "target_file": repo_root / "technical-deep-dives.md",
            "keywords": ["btrfs", "snapper", "ntp", "stratum", "linux", "y2k", "git", "ingest.py", "geany", "database", "wc", "awk", "sql", "regex", "pipeline", "parser"]
        }
    ]

    def execute_routing(prompt_block, response_block):
        prompt_str = "".join(prompt_block).strip()
        response_str = "".join(response_block).strip()
        combined_payload = f"{prompt_str}\n\n{response_str}"
        search_payload = combined_payload.lower()

        constructed_record = (
            f"## Interaction Record\n\n"
            f"### User Prompt\n>{prompt_str}\n\n"
            f"### System Response\n{response_str}\n\n"
            f"---\n\n"
        )

        # Step A: Global Intercept -> Siphon OFFTOPIC commentary immediately
        if "offtopic" in search_payload:
            with open(offtopic_file, "a", encoding="utf-8") as out_f:
                out_f.write(constructed_record)
            print(f"   [OFFTOPIC SIPHON] -> logs/{offtopic_file.name}")
            return

        # Step B: Evaluate explicit developer-overridden tags: ## [ROUTING: filename]
        explicit_match = re.search(r"##\s+\[ROUTING:\s*([\w-]+)\]", combined_payload)

        if explicit_match:
            override_name = f"{explicit_match.group(1)}.md"
            override_path = prop_dir / override_name
            with open(override_path, "a", encoding="utf-8") as out_f:
                out_f.write(constructed_record)
            print(f"   [EXPLICIT OVERRIDE] -> propagation-logs/{override_name}")
            return

        # Step C: Drop through to standard keyword matrix scan
        for route in ROUTING_MATRIX:
            if any(keyword in search_payload for keyword in route["keywords"]):
                with open(route["target_file"], "a", encoding="utf-8") as out_f:
                    out_f.write(constructed_record)
                print(f"   [ROUTED] -> {route['target_file'].relative_to(repo_root)}")
                return

        # Step D: Fallback bucket for unclassified content
        with open(catch_all_file, "a", encoding="utf-8") as out_f:
            out_f.write(constructed_record)
        print(f"   [CATCH-ALL] -> {catch_all_file.name}")

    # 3. Iterate through every file found in the incoming directory queue
    for raw_file_path in source_files:
        print(f"\n[PROCESSING FILE] -> {raw_file_path.name}")
        
        with open(raw_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        start_index = 0
        found_anchor = False
        boundary_index = 0

        # Forward scan from top-to-bottom to catch the historical instance first
        for idx, line in enumerate(lines):
            if "galaxy phone through the search widget" in line.lower():
                # Rewind to the parent prompt header (# you asked)
                start_index = idx
                while start_index > 0 and not lines[start_index].lower().startswith("# you asked"):
                    start_index -= 1
                
                boundary_index = start_index
                found_anchor = True
                print(f"   [SUCCESS] Baseline anchor located at line {idx}. Slicing history from line {boundary_index}.")
                break

        if found_anchor:
            active_lines = lines[boundary_index:]
        else:
            print("   [WARN] Unique baseline anchor not found. Processing raw text from index 0.")
            active_lines = lines
        if found_anchor:
            print(f"   [SUCCESS] Boundary anchor verified at line {start_index}. Truncating legacy drift.")
            active_lines = lines[start_index:]
        else:
            print("   [WARN] No standard boundary anchors found. Processing raw text from index 0.")
            active_lines = lines

        # State-Machine Turn Parser Loop for current file
        current_prompt = []
        current_response = []
        state = None

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

        # Handle remaining buffer trailing turn at EOF for current file
        if current_prompt and current_response:
            execute_routing(current_prompt, current_response)

        # Step E: Safe post-processing archival move execution
        archive_target_path = archive_dir / raw_file_path.name
        if archive_target_path.exists():
            archive_target_path.unlink()  # Prevent collision errors on repeated filename testing
        raw_file_path.rename(archive_target_path)
        print(f"   [ARCHIVED] -> logs/archive/{raw_file_path.name}")

    print("\n[STATUS] Synchronization matrix pipeline run complete for all files.")

if __name__ == "__main__":
    run_unified_ingestion()