#!/bin/sh
set -e
# Ensure PYTHONPATH includes the app directory
export PYTHONPATH="/app:${PYTHONPATH:-}"

# Execute the script with any CMD arguments
exec python3 /app/main.py "$@"