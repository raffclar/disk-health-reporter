#!/bin/bash
# run_daily.sh - A wrapper to run the disk-health-reporter via uv

# Set the directory to the project root (where the script is located)
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$PROJECT_DIR"

# Ensure uv is in the PATH (if installed in a non-standard location)
# export PATH="$HOME/.local/bin:$PATH"

# Run the reporter. Replace recipient@example.com with the target email address.
# Or better, pass it as an argument to this script.
if [ -z "$1" ]; then
    echo "Usage: $0 <recipient-email> [extra-args]"
    exit 1
fi

RECIPIENT_EMAIL=$1
shift # remove the first argument, remaining are extra args

# Run the tool
# We use 'uv run' to ensure the correct virtual environment is used
uv run disk-health-reporter --email "$RECIPIENT_EMAIL" "$@"
