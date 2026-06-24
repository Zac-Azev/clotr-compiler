#!/bin/bash
# Check if file argument is provided
if [ -z "$1" ]; then
    echo "Usage: ./compile-sam.sh <file.clotr>"
    exit 1
fi

INPUT_FILE="$1"
BASE_NAME="${INPUT_FILE%.*}"
SAM_FILE="${BASE_NAME}.sam"

echo "Compiling $INPUT_FILE to $SAM_FILE..."
python3 -m src.compiler "$INPUT_FILE" "$SAM_FILE"
if [ $? -ne 0 ]; then
    echo "Compilation failed!"
    exit 1
fi

# Set the scaling factor for HiDPI/high-resolution displays (default to 2)
UI_SCALE="${UI_SCALE:-2}"

echo "Opening $SAM_FILE in the SaM UI with scaling factor ${UI_SCALE}..."
java -Dsun.java2d.uiScale="${UI_SCALE}" -jar material-sam/SaM-2.6.3.jar -gui "$SAM_FILE"
