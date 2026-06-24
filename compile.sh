#!/bin/bash
# Check if file argument is provided
if [ -z "$1" ]; then
    echo "Usage: ./compile.sh <file.clotr>"
    exit 1
fi

python3 -m src.compiler "$1"
