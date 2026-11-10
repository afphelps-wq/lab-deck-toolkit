#!/bin/bash
# Weekly run: snapshot -> doer (MCP tool + weekly-lab-deck skill) -> no-rewrite checker
# in a separate session on a different model -> macOS notification.
#   ./run_weekly.sh                         # this week (launchd uses this)
#   ./run_weekly.sh 2026-11-02T13:00 2026-11-09T13:00   # a past week, for demo runs
set -uo pipefail
TOOLKIT="$(cd "$(dirname "$0")" && pwd)"
cd "$TOOLKIT"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
PY="$TOOLKIT/.venv/bin/python"
CFG="$TOOLKIT/config.json"
SINCE="${1:-}"; UNTIL="${2:-}"
cfg() { "$PY" -c "import json,os;print(os.path.expanduser(json.load(open('$CFG'))['$1']))"; }
REPO=$(cfg repo); DECKS=$(cfg decks_dir)
# Same window logic as the MCP server, so folder names and tool output agree.
WEEK=$(LAB_DECK_CONFIG="$CFG" "$PY" -c "import sys;sys.path.insert(0,'progress_ledger');import server;s,_=server._window(sys.argv[1] or None,sys.argv[2] or None);y,w,_=s.isocalendar();print(f'{y}-W{w:02d}')" "$SINCE" "$UNTIL")
# Run records live outside every watched folder, so the checker never sees them.
OUT="$DECKS/$WEEK"; RUN="${LABDECK_RUNS:-$HOME/Library/Logs/labdeck}/$WEEK-$(date +%H%M%S)"
mkdir -p "$OUT" "$RUN"
exec >>"$RUN/run.log" 2>&1
echo "=== run $(date) week=$WEEK since=${SINCE:-default} until=${UNTIL:-now}"
notify() { osascript -e "display notification \"$1\" with title \"Lab deck $WEEK\"" || true; }

# Fetch every branch (figures pushed from CRC). Fetch only touches .git, never the
# checked-out files, so it can't trip the no-rewrite check or disturb her work.
git -C "$REPO" fetch --all --prune || echo "WARN: git fetch failed; using last fetched state"

# What the doer is allowed to touch. Everything else under the watched roots is off limits.
cat > "$RUN/ALLOWED.txt" <<EOF
# weekly-lab-deck may write only its own week folder
$OUT/**
EOF
"$PY" .claude/skills/no-rewrite/scripts/snapshot.py take "$RUN/before.json" "$REPO" "$TOOLKIT" "$DECKS"

SK="$TOOLKIT/.claude/skills"
BUILD="$PY $SK/weekly-lab-deck/scripts/build_deck.py"
LINT="$PY $SK/weekly-lab-deck/scripts/lint_deck.py"
DIFF="$PY $SK/no-rewrite/scripts/snapshot.py diff $RUN/before.json"
WINDOW=""
[ -n "$SINCE" ] && WINDOW="Call week_evidence with since=\"$SINCE\" until=\"$UNTIL\"."
claude -p "Use the weekly-lab-deck skill to build the lab meeting deck and progress log. Output folder: $OUT. BUILD command: $BUILD . LINT command: $LINT . $WINDOW" \
  --mcp-config "$TOOLKIT/mcp.json" --strict-mcp-config \
  --allowedTools mcp__progress-ledger__week_evidence Read Write Edit \
    "Bash($BUILD:*)" "Bash($LINT:*)" \
  | tee "$RUN/doer.txt"

# Checker: fresh session, different model, no MCP tools, read-only.
claude -p "Use the no-rewrite skill. Snapshot: $RUN/before.json. Allowed paths: $RUN/ALLOWED.txt. Diff command: $DIFF" \
  --model sonnet --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --allowedTools Read "Bash($DIFF)" \
  | tee "$RUN/check.txt"

if head -1 "$RUN/check.txt" | grep -q "VERDICT: PASS"; then
  notify "Deck ready in $OUT; no-rewrite PASS"
else
  notify "no-rewrite did not pass: read $RUN/check.txt"
fi
