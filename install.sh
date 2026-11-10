#!/bin/bash
# One-time setup on the Mac: venv, mcp.json with absolute paths, weekly launchd job.
set -euo pipefail
TOOLKIT="$(cd "$(dirname "$0")" && pwd)"
cd "$TOOLKIT"
[ -f config.json ] || { cp config.example.json config.json; echo "Edit config.json (repo, template path), then re-run."; exit 1; }

python3 -m venv .venv
.venv/bin/pip install -q mcp python-pptx

cat > mcp.json <<EOF
{"mcpServers": {"progress-ledger": {
  "command": "$TOOLKIT/.venv/bin/python",
  "args": ["$TOOLKIT/progress_ledger/server.py"],
  "env": {"LAB_DECK_CONFIG": "$TOOLKIT/config.json"}}}}
EOF

PLIST="$HOME/Library/LaunchAgents/com.afphelps.labdeck.plist"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.afphelps.labdeck</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$TOOLKIT/run_weekly.sh</string></array>
  <key>StartCalendarInterval</key><dict>
    <key>Weekday</key><integer>0</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer>
  </dict>
  <key>StandardOutPath</key><string>/tmp/labdeck.out</string>
  <key>StandardErrorPath</key><string>/tmp/labdeck.err</string>
</dict></plist>
EOF
launchctl bootout "gui/$(id -u)/com.afphelps.labdeck" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Installed. Weekly run: Sundays 8 PM. Test now with: launchctl kickstart gui/$(id -u)/com.afphelps.labdeck"
echo "Check template layouts with: .venv/bin/python .claude/skills/weekly-lab-deck/scripts/build_deck.py --list-layouts"
