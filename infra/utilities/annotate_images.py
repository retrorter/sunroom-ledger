#!/usr/bin/env python3
import os
import re
from pathlib import Path

def interactive_binder():
    # Detect repository root dynamically
    repo_root = Path(__file__).resolve().parents[2]
    media_dir = repo_root / "media"
    
    if not media_dir.exists():
        print(f"[ERROR] Media directory not found at {media_dir}")
        return

    # 36-character UUID regex pattern
    uuid_pattern = re.compile(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})')
    
    # 1. Collect all local UUID image files
    jpeg_files = sorted(list(media_dir.glob("*.jpg")))
    uuids_to_process = []
    
    for f in jpeg_files:
        match = uuid_pattern.search(f.name)
        if match:
            uuids_to_process.append((match.group(1), f.name))

    if not uuids_to_process:
        print("No UUID-named JPEG images found in media/.")
        return

    print(f"Loaded {len(uuids_to_process)} images from media/. Starting interactive session.")
    print("Commands: Type your blurb and hit Enter. Press Enter on blank to skip. Type 'q' to save and exit.\n")

    # 2. Step through each image one by one
    for uuid, filename in uuids_to_process:
        found_context = None
        target_file = None
        full_text = ""
        
        # Search for this UUID across all ledger markdown files
        for md_path in repo_root.glob("**/*.md"):
            if "media/" in str(md_path) or ".git" in str(md_path):
                continue
                
            with open(md_path, "r", encoding="utf-8") as stream:
                content = stream.read()
                if uuid in content:
                    target_file = md_path
                    full_text = content
                    # Extract the specific paragraph block containing the UUID
                    blocks = content.split("\n\n")
                    for block in blocks:
                        if uuid in block:
                            found_context = " ".join(block.strip().split())
                    break

        # UI Display for the current loop step
        print("=" * 80)
        print(f"📷 IMAGE: {filename}")
        
        if not target_file:
            print("⚠️  STATUS: Orphaned binary (Not found in any markdown ledger files). Skipping.")
            continue
            
        print(f"📍 LOG:   {target_file.relative_to(repo_root)}")
        print(f"📝 AI CONTEXT:\n   \"{found_context}\"\n")
        
        # ─── FEH AUTOMATION & X11 FOCUS RETENTION ──────────────────────
        import subprocess
        import shutil

        # Interrogate X11 for the terminal window ID before feh alters the state
        try:
            term_id_dec = subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()
            term_window_hex = f"0x{int(term_id_dec):08x}"
        except Exception as e:
            term_id_dec = term_window_hex = None
            print(f"⚠️ Focus Warning: Failed to parse terminal window ID: {e}")

        # Open feh completely decoupled from the terminal's STDIN
        feh_proc = subprocess.Popen(
            ["feh", "--geometry", "400x400+1200+0", str(repo_root / "media" / filename)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Asynchronously force focus back *after* python settles into input()
        if term_id_dec:
            has_wmctrl = shutil.which("wmctrl") is not None
            focus_executor = f"wmctrl -i -a {term_window_hex}" if has_wmctrl else f"xdotool windowactivate {term_id_dec}"
            
            # Stripped xdotool search to eliminate background subshell deadlocks.
            # The 0.5 sleep gives Cinnamon total freedom to map the window before we yank focus.
            focus_cmd = f"sleep 0.35 && {focus_executor} && xdotool windowfocus {term_id_dec}"
            
            subprocess.Popen(
                focus_cmd, 
                shell=True, 
                stdin=subprocess.DEVNULL, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
        # ────────────────────────────────────────────────────────────────
        
        # Check if a markdown image link already exists for this UUID
        link_pattern = re.compile(r'!\[(.*?)\]\((../)?media/' + re.escape(filename) + r'\)')
        existing_link_match = link_pattern.search(full_text)
        
        if existing_link_match:
            current_alt = existing_link_match.group(1)
            print(f"➔ Current Alt-Text: \"{current_alt}\"")
        else:
            print("➔ Current Alt-Text: [NONE - No markdown link generated yet]")

        # Prompt the user for input
        user_input = input("\nEnter Description (or 'q' to quit): ").strip()
        
        # ─── AUTO-CLOSE FEH ─────────────────────────────────────────────
        feh_proc.terminate()
        # ────────────────────────────────────────────────────────────────
        
        if user_input.lower() == 'q':
            print("\nExiting session. Progress saved in modified ledger files.")
            break
        elif user_input == "":
            print("Skipped.")
            continue
            
        # Update or Insert the Markdown Link
        new_link_string = f"![{user_input}](../media/{filename})"
        
        if existing_link_match:
            # Replace existing markdown link inline
            updated_text = link_pattern.sub(new_link_string, full_text)
        else:
            # Insert the link right below the line containing the UUID
            lines = full_text.splitlines()
            updated_lines = []
            for line in lines:
                updated_lines.append(line)
                if uuid in line and "media/" not in line:
                    # Append the markdown link right underneath the file signature line
                    updated_lines.append(new_link_string)
            updated_text = "\n".join(updated_lines)
            
        # Write modification back to disk in-place
        with open(target_file, "w", encoding="utf-8") as stream:
            stream.write(updated_text)
            
        print("💾 Bound successfully to ledger.")

if __name__ == "__main__":
    interactive_binder()
