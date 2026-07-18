#!/usr/bin/env python3
"""
GOLDEN_STATE PRODUCTION SCRIPT: ingest_light.py
Description: Interactive CLI wizard to record photosynthetically active radiation (PAR)
             measurements across selectable path scopes, handle dynamic ad-hoc node additions,
             compute Daily Light Integral (DLI), and save structured Markdown logs.
Version: 2.3.0
State: GOLDEN_STATE
"""

import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class BotanicalNode:
    """Immutable data definition for a physical spatial anchor point."""
    id: str
    zone: str
    desc: str
    photo: str

# Immutable Master Registry mapping all 29 valid property nodes
GLOBAL_NODE_REGISTRY = [
    # I. ZONE: HOUSE BED & STEPS (Exterior - CCW Traversal)
    BotanicalNode("V1", "House Bed", "Spigot Corner (0,0)", "housebed-v1-spigot-MCU.jpg"),
    BotanicalNode("V_drop", "House Bed", "Step 0 / Porch Pad Drop-off", "front-view-PP-b_drop-V_drop-view"),
    BotanicalNode("Step 1", "House Bed", "Diagonal Shadow Collection Point", "porch-stair-transition-mid-first-step-collecion-point-MS.jpg"),
    BotanicalNode("V2", "House Bed", "Step 1 & 2 Vertex (Porch Front Edge)", "porchpad-step-1-diagonal-housebed.jpg"),
    BotanicalNode("Step 4", "House Bed", "Outer Front Edge Midpoint (6,7)", "step-4-outer-midpoint-CU.jpg"),
    BotanicalNode("V4", "House Bed", "Driveway Brick Corner (12,0)", "housebed-v4-garage-MS.jpg"),
    BotanicalNode("Vmid", "House Bed", "Mid-Bed Canopy (6,3.5) [Last Exterior CCW Station]", "housebed-vmid-canopy-MS.jpg"),

    # II. ZONE: BASEMENT BED (Exterior - Linear Traversal)
    BotanicalNode("B_drop", "Basement Bed", "12\" Porch Drop-off (0,3)", "basementbed-bdrop-edge-MS.jpg"),
    BotanicalNode("B1", "Basement Bed", "Herb/Succulent Core (1.5,1.5)", "basementbed-b1-herbs-MCU.jpg"),
    BotanicalNode("B_mp", "Basement Bed", "Midpoint Stone Drop-off (6.5,3)", "basement-bed-6.5-3-coord-1659.jpg"),
    BotanicalNode("B_edge", "Basement Bed", "House Corner Wall (13,0)", "basement-edge-NNW.jpg"),
    BotanicalNode("Bmax", "Basement Bed", "Cul-de-sac Corner (13,3)", "basementbed-bmax-culdesac-WS.jpg"),

    # III. ZONE: SUNROOM COHORT WALLS (Interior - Clockwise Traversal)
    BotanicalNode("LW1", "Sunroom", "Left Wall / NNW - Node 1", "sunroom-LW-NNW-1-facing-WS.jpg"),
    BotanicalNode("LW2", "Sunroom", "Left Wall / NNW - Node 2", "sunroom-LW-NNW-2-facing-WS.jpg"),
    BotanicalNode("LW3", "Sunroom", "Left Wall / NNW - Node 3", "sunroom-LW-NNW-3-facing-WS.jpg"),
    BotanicalNode("LFV", "Sunroom", "Left-Front Vertex Corner", "sunroom-LFV-corner-MS.jpg"),
    BotanicalNode("FW1", "Sunroom", "Front Wall / ENE - Node 1", "sunroom-FW-ENE-1-facing-WS.jpg"),
    BotanicalNode("FW2", "Sunroom", "Front Wall / ENE - Node 2", "sunroom-FW-ENE-2-facing-WS.jpg"),
    BotanicalNode("FW3", "Sunroom", "Front Wall / ENE - Node 3", "sunroom-FW-ENE-3-facing-WS.jpg"),
    BotanicalNode("FW4", "Sunroom", "Front Wall / ENE - Node 4", "sunroom-FW-ENE-4-facing-WS.jpg"),
    BotanicalNode("FRV", "Sunroom", "Front-Right Vertex Corner", "sunroom-FRV-corner-MS.jpg"),
    BotanicalNode("RW1", "Sunroom", "Right Wall / SSE - Node 1 (Pothos)", "sunroom-RW-SSE-1-facing-WS.jpg"),
    BotanicalNode("RW2", "Sunroom", "Right Wall / SSE - Node 2 (Door)", "sunroom-RW-SSE-2-facing-WS.jpg"),

    # IV. ZONE: LIVING ROOM PROPAGATION
    BotanicalNode("LV1", "Living Room", "Left Window Frame Casement Anchor", "livingroom-LV1-left-MS.jpg"),
    BotanicalNode("LV2", "Living Room", "Right Window Frame Casement Anchor", "livingroom-LV2-right-MS.jpg"),

    # V. ZONE: SYSTEM LIGHT ARRAYS
    BotanicalNode("LA1", "Light Arrays", "SF1000 Fixture Enclosure 1", "hardware-la1-setup-CU.jpg"),
    BotanicalNode("LA2", "Light Arrays", "SF1000 Fixture Enclosure 2", "hardware-la2-setup-CU.jpg"),
    BotanicalNode("LA3", "Light Arrays", "SF1000 Fixture Enclosure 3", "hardware-la3-setup-CU.jpg"),
    BotanicalNode("LA4", "Light Arrays", "SF1000 Fixture Enclosure 4", "hardware-la4-setup-CU.jpg")
]

def parse_node_string(raw_string: str) -> tuple[str, Optional[str]]:
    """Splits node string at the first hyphen to separate base ID from environmental modifier."""
    parts = raw_string.split('-', 1)
    base_id = parts[0].strip()
    modifier = parts[1].strip() if len(parts) > 1 else None
    return base_id, modifier

def calculate_dli(par: float, photoperiod: float) -> float:
    """Computes DLI (mol/m²/day): PAR * photoperiod * 3600 / 1,000,000"""
    return round((par * photoperiod * 3600) / 1000000, 2)

def lookup_registered_node(base_id: str) -> Optional[BotanicalNode]:
    """Retrieves standard metadata definitions matching a base node token query."""
    for node in GLOBAL_NODE_REGISTRY:
        if node.id.upper() == base_id.upper():
            return node
    return None

def capture_node_metrics(node: BotanicalNode, active_mod: Optional[str], full_id: str, photoperiod: float, sky_cond: str) -> dict:
    """Executes the standardized internal parameter terminal input entry loop for a target node."""
    while True:
        try:
            par_input = input(f"  PAR value for {full_id} (umol/m^2/s): ").strip()
            par_val = float(par_input)
            break
        except ValueError:
            print("  [ERROR] Invalid input. Please enter a numerical PAR value.")

    photo_prompt = f"  Photo Reference [Default: {node.photo}]: "
    photo_ref = input(photo_prompt).strip()
    final_photo = photo_ref if photo_ref else node.photo

    notes = input("  Notes [Default: Normal]: ").strip() or "Normal"
    if active_mod:
        notes = f"[{active_mod.upper()} MODIFIER] {notes}"
    
    node_dli = calculate_dli(par_val, photoperiod)
    
    return {
        "id": full_id,
        "zone": node.zone,
        "par": par_val,
        "dli": node_dli,
        "photo": final_photo,
        "notes": notes
    }

def run_wizard():
    print("==========================================================")
    print("      GOLDEN_STATE PAR Data Ingestion Wizard (v2.3.0)     ")
    print("==========================================================")
    
    # 1. Global Metadata Initialization
    log_date = input("Enter log date (YYYY-MM-DD) [Default: today]: ").strip()
    if not log_date:
        log_date = datetime.now().strftime("%Y-%m-%d")
        
    time_start = input("Enter start time (HHMM, e.g., 0930): ").strip()
    time_end = input("Enter end time (HHMM, e.g., 0945): ").strip()
    temp_f = input("Enter outdoor temperature (°F, e.g., 78): ").strip()
    sky_conditions = input("Sky conditions (S=Sunny, PC=Partly Cloudy, MC=Mostly Cloudy, R=Rain): ").strip().upper()
    photoperiod = float(input("Photoperiod basis (hours) [Default: 14.0]: ") or 14.0)

    # 2. Scope Matrix Selector Configuration
    PATH_SCOPES = {
        "1": ("Full Property Master Loop (All 29 Registered Nodes)", ["House Bed", "Basement Bed", "Sunroom", "Living Room", "Light Arrays"]),
        "2": ("Exterior Infrastructure Tracking Only (HB + BB)", ["House Bed", "Basement Bed"]),
        "3": ("Sunroom Interior Cohort Only (Clockwise 11-Station Sweep)", ["Sunroom"]),
        "4": ("Living Room & Light Arrays Expansion Array Only (LR + LA)", ["Living Room", "Light Arrays"]),
    }

    print("\nSelect Active Walkpath Scope Path Profile:")
    for key, (name, _) in PATH_SCOPES.items():
        print(f"  [{key}] {name}")
    
    scope_choice = input("Select scope profile index [Default: 1]: ").strip() or "1"
    active_zones = PATH_SCOPES.get(scope_choice, PATH_SCOPES["1"])[1]
    
    # Filter global sequence to track targeted path profiles cleanly
    scoped_walkpath = [node for node in GLOBAL_NODE_REGISTRY if node.zone in active_zones]
    logged_data = []

    # 3. Main Scoped Traversal Processing Execution Loop
    print(f"\n--- Beginning Scoped Execution Path ({len(scoped_walkpath)} Registry Targets) ---")
    for idx, node in enumerate(scoped_walkpath, 1):
        print(f"\n[{idx:02d}/{len(scoped_walkpath)}] Scoped Anchor Station: {node.id} ({node.zone})")
        print(f"       Description Hint: {node.desc}")
        
        mod_input = input(f"  Condition modifier suffix (optional, e.g., shade): ").strip()
        full_node_id = f"{node.id}-{mod_input}" if mod_input else node.id
        _, active_mod = parse_node_string(full_node_id)
        
        metrics = capture_node_metrics(node, active_mod, full_node_id, photoperiod, sky_conditions)
        logged_data.append(metrics)

    # 4. Open-Ended Dynamic Ad-Hoc Intercept Phase
    print("\n--- Initializing Ad-Hoc Checkpoint Target Acquisition Phase ---")
    print("Type any Node ID manually to append targeted captures on-the-fly.")
    print("To terminate data ingestion and build the final ledger entry, type 'q'.")
    
    while True:
        adhoc_input = input("\nEnter Ad-Hoc Node ID (or 'q' to compile ledger): ").strip()
        if adhoc_input.lower() in ['q', 'quit']:
            break
        if not adhoc_input:
            continue
            
        base_id, active_mod = parse_node_string(adhoc_input)
        existing_node = lookup_registered_node(base_id)
        
        if existing_node:
            print(f"  [+] Registered target matching '{base_id}' extracted from global database.")
            current_node = existing_node
        else:
            print(f"  [!] Dynamic Target Unregistered: '{base_id}' falls outside standard configuration profiles.")
            adhoc_zone = input("  Assign Category/Zone classification for this ledger trace: ").strip() or "Dynamic Verification"
            adhoc_desc = input("  Provide unique structural landmark description details: ").strip() or "Ad-hoc manual tracking marker"
            current_node = BotanicalNode(id=base_id, zone=adhoc_zone, desc=adhoc_desc, photo="adhoc-untracked-capture.jpg")
            
        metrics = capture_node_metrics(current_node, active_mod, adhoc_input, photoperiod, sky_conditions)
        logged_data.append(metrics)

    # 5. Front Matter Generation Block Assembly Execution
    markdown_output = f"""---
layout_id: "property-grid-v2"
log_date: {log_date}
operator_time_offset: "EDT (UTC-4)"
sky_conditions: "{sky_conditions}"
---

# Physical Light Log: {log_date}

## Sequence Metadata
* Start Time: {time_start}
* End Time: {time_end}
* Temp: {temp_f} F
* Photoperiod Basis: {photoperiod} hours

## Logged Nodes
"""
    for item in logged_data:
        markdown_output += f"""* Node: {item['id']}
  - Zone: {item['zone']}
  - PAR: {item['par']} ({sky_conditions})
  - DLI: {item['dli']}
  - Photo: {item['photo']}
  - Notes: {item['notes']}
"""

    # 6. File Compression Generation Assembly & Local Disk Writing Path Routing
    bucket_dir = os.path.join("logs", "PAR-bucket")
    os.makedirs(bucket_dir, exist_ok=True)

    safe_time = re.sub(r"[^\d]", "", time_start)
    filename = os.path.join(bucket_dir, f"{log_date}_{safe_time}_light_log.md")

    with open(filename, "w") as f:
        f.write(markdown_output)

    print("\n==========================================================")
    print(f"Log successfully compiled and appended into local ledger storage:\n--> {filename}")
    print("==========================================================")

if __name__ == "__main__":
    run_wizard()
