#!/usr/bin/env python3
import os

# Define paths matching your exact repository layout
WORKSPACE_DIR = os.path.expanduser("~/sunroom-ledger")
INVENTORY_DIR = os.path.join(WORKSPACE_DIR, "inventory")
PROP_DIR = os.path.join(WORKSPACE_DIR, "propagation-logs")

# Ensure complete directory tree exists
os.makedirs(INVENTORY_DIR, exist_ok=True)
os.makedirs(PROP_DIR, exist_ok=True)

# Strict Taxonomy Routing Matrix
ROUTING_MATRIX = [
    {
        "target_file": os.path.join(INVENTORY_DIR, "ficus-trifecta.md"),
        "keywords": ["ficus", "audrey", "ruby", "tineke", "stipula", "stipule", "girdling", "layering", "auxin"]
    },
    {
        "target_file": os.path.join(INVENTORY_DIR, "strelitzia-nicolai.md"),
        "keywords": ["strelitzia", "nicolai", "bird of paradise", "bop", "unfurling", "sheathed"]
    },
    {
        "target_file": os.path.join(INVENTORY_DIR, "monstera-deliciosa.md"),
        "keywords": ["monstera", "deliciosa", "happy frog", "propagation"]
    },
    {
        "target_file": os.path.join(INVENTORY_DIR, "zz-collection.md"),
        "keywords": ["zz", "zamioculcas", "rhizome"]
    },
    {
        "target_file": os.path.join(INVENTORY_DIR, "heirloom-aloes.md"),
        "keywords": ["aloe", "pup", "debridement", "heirloom", "terracotta"]
    },
    {
        "target_file": os.path.join(PROP_DIR, "2026-june-succulents.md"),
        "keywords": ["crassula", "ovata", "ripple", "jade", "kalanchoe", "apical", "succulent", "succulents", "top dress"]
    },
    {
        "target_file": os.path.join(PROP_DIR, "2026-june-herbs.md"),
        "keywords": ["thyme", "basil", "rosemary", "mint", "spearmint", "death plug", "herbs", "arugula", "sowing", "1020"]
    },
    {
        "target_file": os.path.join(WORKSPACE_DIR, "technical-deep-dives.md"),
        "keywords": ["btrfs", "snapper", "ntp", "stratum", "linux", "y2k", "git", "ingest.py", "geany", "database", "wc", "awk", "sql"]
    }
]

CATCH_ALL_FILE = os.path.join(WORKSPACE_DIR, "unclassified-logs.md")
RAW_EXPORT_PATH = os.path.expanduser("~/Downloads/Gemini-_53.md")

def route_turn_block(prompt_text, response_text):
    """Evaluates combined block text against the matrix and appends to the target file."""
    if not prompt_text.strip() and not response_text.strip():
        return

    combined_content = (
        f"## Interaction Record\n\n"
        f"### User Prompt\n>{prompt_text.strip()}\n\n"
        f"### System Response\n{response_text.strip()}\n\n"
        f"---\n\n"
    )
    search_payload = (prompt_text + " " + response_text).lower()
    
    # Check regular routing matrix
    for route in ROUTING_MATRIX:
        if any(keyword in search_payload for keyword in route["keywords"]):
            with open(route["target_file"], "a") as out_file:
                out_file.write(combined_content)
            print(f"[ROUTED] -> {os.path.basename(route['target_file'])}")
            return

    # Fallback to catch-all if no keywords match
    with open(CATCH_ALL_FILE, "a") as out_file:
        out_file.write(combined_content)
    print(f"[CATCH-ALL] -> {os.path.basename(CATCH_ALL_FILE)}")

def parse_export():
    if not os.path.exists(RAW_EXPORT_PATH):
        print(f"Error: Target file {RAW_EXPORT_PATH} not found.")
        return

    with open(RAW_EXPORT_PATH, "r") as f:
        lines = f.readlines()

    print(f"Processing {len(lines)} pre-trimmed lines from your Geany export.")
    
    current_prompt = []
    current_response = []
    state = None

    for line in lines:
        if line.startswith("# you asked"):
            if current_prompt and current_response:
                route_turn_block("".join(current_prompt), "".join(current_response))
                current_prompt = []
                current_response = []
            state = "PROMPT"
            continue
        elif line.startswith("# gemini response"):
            state = "RESPONSE"
            continue
        
        if state == "PROMPT":
            current_prompt.append(line)
        elif state == "RESPONSE":
            current_response.append(line)

    # Catch the trailing block at End of File
    if current_prompt and current_response:
        route_turn_block("".join(current_prompt), "".join(current_response))

if __name__ == "__main__":
    parse_export()
