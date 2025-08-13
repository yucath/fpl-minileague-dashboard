#!/bin/bash

# Define the session name
SESSION_NAME="fantasy_session"

# Define the path to your Streamlit application
APP_PATH="/home/achyut/Achyut/Projects/fantasy/fpl_live.py"

# Define the path to your virtual environment's Python interpreter
VENV_PYTHON="/home/achyut/venv/bin/python"

# Change to the directory containing your Streamlit application
cd "$(dirname "$APP_PATH")" || { echo "Failed to change directory"; exit 1; }

# Check if the tmux session already exists
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    # If the session exists, send the command to run the Streamlit app
    tmux send-keys -t $SESSION_NAME "$VENV_PYTHON -m streamlit run $APP_PATH --server.port=8504" C-m
    echo "Tmux session '$SESSION_NAME' already exists. Sent command to start Streamlit app."
else
    # If the session doesn't exist, create a new detached session and run the Streamlit app
    tmux new-session -d -s $SESSION_NAME "$VENV_PYTHON -m streamlit run $APP_PATH --server.port=8504"
    echo "Created new tmux session '$SESSION_NAME' and started Streamlit app."
fi
