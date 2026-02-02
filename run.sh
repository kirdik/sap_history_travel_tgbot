#!/bin/bash
# Change directory to the script's location to ensure correct relative paths
cd "$(dirname "$0")"

# Run the bot using the virtual environment's python
.venv/bin/python -m bot.main
