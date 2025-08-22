# Build Windows EXE (no install required)
pip install pyinstaller==6.10 psutil requests
pyinstaller --onefile --noconsole agent.py

# Output in `dist/agent.exe`
# Place `config.json` alongside `agent.exe` and double-click to run.
