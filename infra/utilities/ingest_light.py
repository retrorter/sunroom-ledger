#!/usr/bin/env python3
"""
GOLDEN_STATE PRODUCTION SCRIPT: ingest_light.py
Description: Ultra-low-friction CLI wizard to capture PAR measurements. 
             Supports single-line inline notes parsing (e.g. '185.2 maple shade').
Version: 2.5.2
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

# Immutable Master Registry mapping all updated property nodes
GLOBAL_NODE_REGISTRY = [
    # I. ZONE: HOUSE BED & STEPS (Exterior - CCW Traversal)
    BotanicalNode("Spigot", "House Bed", "Spigot Corner (0,0)", "hb_spigot_ws.jpg"),
    BotanicalNode("h_drop", "House Bed", "Porch Pad 16-inch drop-off", "hb_h_drop_top.jpg"),
    BotanicalNode("Step 1", "House Bed", "Inner stone boundary baseline", "hb_step1_boundary_ms.jpg"),
    BotanicalNode("Step 2", "House Bed", "Diagonal vector crossing point", "hb_step2_diagonal_ms.jpg"),
    BotanicalNode("Step 3", "House Bed", "1/4 along lower front stone edge", "hb_step3_quarter_edge_ms.jpg"),
    BotanicalNode("Step 4", "House Bed", "Physical midpoint of front stone edge", "hb_step4_midpoint_cu.jpg"),
    BotanicalNode("Drv", "House Bed", "Outside vertex corner at driveway line", "hb_driveway_vertex_ws.jpg"),
    BotanicalNode("h_mid", "House Bed", "Interior mid-bed canopy center", "hb_mid_canopy_ms.jpg"),

    # II. ZONE: BASEMENT BED (Exterior - Linear Traversal Refactored)
    BotanicalNode("b_drop", "Basement Bed", "Porch step 12-inch drop-off activity hub", "bb_drop_activity_ws.jpg"),
    BotanicalNode("b_core", "Basement Bed", "High-intensity vector zone past drop-off", "bb_core_vector_ms.jpg"),
    BotanicalNode("b_mid", "Basement Bed", "True physical midpoint of foundation wall length", "bb_mid_window_ms.jpg"),
    BotanicalNode("b_max", "Basement Bed", "Cul-de-sac solar corner retaining wall", "bb_max_retaining_ws.jpg"),

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

def calculate_dli(par: float, photoperiod: float) -> float:
    """Computes DLI (mol/m²/day): PAR * photoperiod * 3600 / 1,000,000"""
    return round((par * photoperiod * 3600) / 1000000, 2)

def lookup_registered_node(base_id: str) -> Optional[BotanicalNode]:
    """Retrieves standard metadata definitions matching a base node token query."""
    for node in GLOBAL_NODE_REGISTRY:
        if node.id.upper() == base_id.upper():
            return node
    return None

def capture_default_node(node: BotanicalNode, photoperiod: float) -> dict:
    """Fast-path entry loop logic. Single line parses both float and optional inline notes."""
    while True:
        raw_input = input("    PAR [Val + Note / Enter to skip]: ").strip()
        
        if not raw_input or raw_input.lower() in ['nan', 'skip', 'x']:
            return {
                "id": f"{node.id}-offline",
                "zone": node.zone,
                "par": 0.0,
                "dli": 0.0,
                "photo": node.photo,
                "notes": "[OFFLINE] Fixture or station currently inactive/unmeasured"
            }
        
        # Parse inline notes split by first space segment
        input_segments = raw_input.split(maxsplit=1)
        numeric_part = input_segments[0]
        parsed_note = input_segments[1] if len(input_segments) > 1 else "Normal"
        
        try:
            par_val = float(numeric_part)
            break
        except ValueError:
            print("  [ERROR] Invalid structure. Input numeric PAR values (optional inline notes text allowed).")

    return {
        "id": node.id,
        "zone": node.zone,
        "par": par_val,
        "dli": calculate_dli(par_val, photoperiod),
        "photo": node.photo,
        "notes": parsed_note
    }

def capture_adhoc_node(node: BotanicalNode, photoperiod: float, explicit_id: str) -> dict:
    """Deep inspection data parsing for standalone ad-hoc additions at end of run."""
    while True:
        raw_input = input(f"    PAR value for {explicit_id}: ").strip()
        try:
            par_val = float(raw_input)
            break
        except ValueError:
            print("  [ERROR] Ad-hoc entries require a valid numeric PAR value.")

    modifier = input("    Modifier/Context (e.g., maple shade, cloud edge) [Enter for None]: ").strip()
    notes = input("    Detailed Notes [Enter for Normal]: ").strip() or "Normal"
    
    final_id = f"{explicit_id}-{modifier.replace(' ', '_')}" if modifier else explicit_id
    final_notes = f"[{modifier.upper()} MODIFIER] {notes}" if modifier else notes

    return {
        "id": final_id,
        "zone": node.zone,
        "par": par_val,
        "dli": calculate_dli(par_val, photoperiod),
        "photo": node.photo,
        "notes": final_notes
    }

def run_wizard():
    print("==========================================================")
    print("      GOLDEN_STATE PAR Data Ingestion Wizard (v2.5.2)     ")
    print("==========================================================")
    
    # 1. Global Metadata Initialization
    log_date = input("Enter log date (YYYY-MM-DD) [Default: today]: ").strip()
    if not log_date:
        log_date = datetime.now().strftime("%Y-%m-%d")
        
    time_start = input("Enter start time (HHMM, e.g., 1745): ").strip()
    time_end = input("Enter end time (HHMM, e.g., 1751): ").strip()
    temp_f = input("Enter outdoor temperature (°F, e.g., 90): ").strip()
    sky_conditions = input("Sky conditions (S=Sunny, PC=Partly Cloudy, MC=Mostly Cloudy, R=Rain): ").strip().upper()
    photoperiod = float(input("Photoperiod basis (hours) [Default: 14.0]: ") or 14.0)

    # 2. Scope Matrix Selector Configuration
    PATH_SCOPES = {
        "1": ("Full Property Master Loop (All 26 Registered Nodes)", ["House Bed", "Basement Bed", "Sunroom", "Living Room", "Light Arrays"]),
        "2": ("Exterior Infrastructure Tracking Only (HB + BB)", ["House Bed", "Basement Bed"]),
        "3": ("Sunroom Interior Cohort Only (Clockwise 11-Station Sweep)", ["Sunroom"]),
        "4": ("Living Room & Light Arrays Expansion Array Only (LR + LA)", ["Living Room", "Light Arrays"]),
    }

    print("\nSelect Active Walkpath Scope Path Profile:")
    for key, (name, _) in PATH_SCOPES.items():
        print(f"  [{key}] {name}")
    
    scope_choice = input("Select scope profile index [Default: 1]: ").strip() or "1"
    active_zones = PATH_SCOPES.get(scope_choice, PATH_SCOPES["1"])[1]
    
    scoped_walkpath = [node for node in GLOBAL_NODE_REGISTRY if node.zone in active_zones]
    logged_data = []

    # 3. Main Scoped Traversal Ingestion Loop
    print(f"\n--- Beginning Scoped Execution Path ({len(scoped_walkpath)} Registry Targets) ---")
    for idx, node in enumerate(scoped_walkpath, 1):
        # UI Fix: Injected node.desc directly into the loop header block
        print(f"\n[{idx:02d}/{len(scoped_walkpath)}] {node.zone} -> {node.id} | {node.desc}")
        metrics = capture_default_node(node, photoperiod)
        logged_data.append(metrics)

    # 4. Open-Ended Dynamic Ad-Hoc Intercept Phase
    print("\n--- Initializing Ad-Hoc Checkpoint Target Acquisition Phase ---")
    print("Type any Node ID manually to append targeted captures with custom modifiers/notes.")
    print("To terminate data ingestion and build the final ledger entry, type 'q'.")
    
    while True:
        adhoc_input = input("\nEnter Ad-Hoc Node ID (or 'q' to compile ledger): ").strip()
        if adhoc_input.lower() in ['q', 'quit']:
            break
        if not adhoc_input:
            continue
            
        existing_node = lookup_registered_node(adhoc_input)
        
        if existing_node:
            print(f"  [+] Registered target matching '{adhoc_input}' extracted from global database.")
            current_node = existing_node
        else:
            print(f"  [!] Dynamic Target Unregistered: '{adhoc_input}' falls outside standard configuration profiles.")
            adhoc_zone = input("  Assign Category/Zone classification for this ledger trace: ").strip() or "Dynamic Verification"
            current_node = BotanicalNode(id=adhoc_input, zone=adhoc_zone, desc="Ad-hoc manual tracking marker", photo="adhoc-untracked-capture.jpg")
            
        metrics = capture_adhoc_node(current_node, photoperiod, adhoc_input)
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

    # 6. Output Assembly & Local Disk Writing Path Routing
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
