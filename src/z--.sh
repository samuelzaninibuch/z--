#!/bin/bash

# Check if the correct number of arguments is provided
if [ -z "$1" ]; then
    echo "Usage: z-- filename"
    exit 1
fi

# Get the full path of the script
SCRIPT_DIR="$(dirname "$(realpath "$0")")"

# Run the Python script with the provided filename
python3 "$SCRIPT_DIR/z--.py" "$1"
