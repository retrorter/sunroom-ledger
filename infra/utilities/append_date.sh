#!/bin/bash
# ==============================================================================
# append_date.sh
# Bulk appends file modification date (MMDDYYYY) to JPG/JPEG files.
# Usage: ./append_date.sh [target_directory]
# ==============================================================================

# Default to ~/Downloads/jpgs if no directory is specified
TARGET_DIR="${1:-$HOME/Downloads/jpgs}"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' does not exist."
    exit 1
fi

# Enable case-insensitive globbing to capture .jpg, .JPG, .jpeg, etc.
shopt -s nocaseglob

echo "Processing images in: $TARGET_DIR"
echo "--------------------------------------------------"

for file in "$TARGET_DIR"/*.jpg "$TARGET_DIR"/*.jpeg; do
    # Ensure the glob matched actual files
    [ -e "$file" ] || continue

    # Extract components
    dir=$(dirname "$file")
    base=$(basename "$file")
    filename="${base%.*}"
    ext="${base##*.}"

    # Get modification date in MMDDYYYY format
    date_suffix=$(date -r "$file" +"%m%d%Y")

    # Guard rail: Skip if the filename already ends in an 8-digit date (e.g., _07162026)
    if [[ "$filename" =~ _[0-9]{8}$ ]]; then
        echo "  [SKIPPED] Already timestamped: $base"
        continue
    fi

    # Construct the new path
    new_name="${dir}/${filename}_${date_suffix}.${ext}"

    # Rename safely (do not overwrite existing files)
    mv -n "$file" "$new_name"
    echo "  [RENAMED] $base -> $(basename "$new_name")"
done

# Restore default shell options
shopt -u nocaseglob
echo "--------------------------------------------------"
echo "Batch process complete."
