#!/bin/bash

# AI Desktop Assistant Startup Script

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/ai_assistant_env" ]; then
    source "$SCRIPT_DIR/ai_assistant_env/bin/activate"
fi

# Change to script directory
cd "$SCRIPT_DIR"

# Run the assistant
python3 main.py