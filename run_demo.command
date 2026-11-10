#!/bin/bash
# Double-click to: copy the lab-meeting template from Drive, list its layouts,
# and run the two demo weeks. Output is mirrored to ../labdeck-demo/ for review.
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
DEMO="$(cd .. && pwd)/labdeck-demo"; mkdir -p "$DEMO"
exec > >(tee "$DEMO/demo.log") 2>&1
echo "== $(date)"
echo "== claude: $(command -v claude || echo MISSING) $(claude --version 2>/dev/null)"
if [ ! -f template.pptx ]; then
  # Exact folder, no recursive search ("11/09" shows up as "11:09" on disk, so glob that char).
  for T in "$HOME"/Library/CloudStorage/GoogleDrive-*/"My Drive"/"Lab Meeting Materials 11"?"09"/Lab_Meeting_11_09_26_Phelps_v5.pptx; do
    [ -e "$T" ] || continue
    echo "== template: $T"
    ( cp "$T" template.pptx ) & CP=$!
    for i in $(seq 1 60); do kill -0 $CP 2>/dev/null || break; sleep 2; done
    kill $CP 2>/dev/null && echo "== template copy timed out (Drive download)" && rm -f template.pptx
  done
  [ -f template.pptx ] && ls -la template.pptx || echo "== NO TEMPLATE: using a plain deck"
fi
echo "== layouts"
.venv/bin/python .claude/skills/weekly-lab-deck/scripts/build_deck.py --list-layouts
echo "== run 1: 2026-10-19 -> 2026-10-26"
./run_weekly.sh 2026-10-19T13:00 2026-10-26T13:00
echo "== run 2: 2026-11-02 -> 2026-11-09"
./run_weekly.sh 2026-11-02T13:00 2026-11-09T13:00
rm -rf "$DEMO/runs" "$DEMO/decks"
cp -R "$HOME/Library/Logs/labdeck" "$DEMO/runs"
cp -R "$HOME/LabDecks" "$DEMO/decks"
echo "== DONE. Results copied to $DEMO"
