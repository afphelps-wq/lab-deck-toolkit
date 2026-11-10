#!/bin/bash
# Evidence capture + publish. Output mirrored to ../labdeck-demo/publish.log
cd "$(dirname "$0")"; T="$(pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
LOG="$(cd .. && pwd)/labdeck-demo/publish.log"; mkdir -p "$(dirname "$LOG")" docs/evidence docs/runs
exec > >(tee "$LOG") 2>&1
echo "== $(date)"

echo "== 1. trivial skill test (Step 2)"
TD=$(mktemp -d); mkdir -p "$TD/.claude/skills/banana"
cat > "$TD/.claude/skills/banana/SKILL.md" <<'S'
---
name: banana
description: Use for every reply in this project, no matter the question.
---
Start every reply with the word BANANA in capitals, then answer normally.
S
( cd "$TD" && claude -p "What is 2+2?" ) | tee docs/evidence/trivial_skill_test.txt
cp "$TD/.claude/skills/banana/SKILL.md" docs/evidence/trivial_skill_SKILL.md

echo "== 2. MCP tool visible to the agent (Step 5)"
claude -p "List the MCP tools available to you by exact name, with one line on what each does. Do not call any of them." \
  --mcp-config "$T/mcp.json" --strict-mcp-config | tee docs/evidence/mcp_tools_visible.txt

echo "== 3. full transcript of a doer run, showing the week_evidence call (Step 6)"
PY="$T/.venv/bin/python"; SK="$T/.claude/skills"
BUILD="$PY $SK/weekly-lab-deck/scripts/build_deck.py"; LINT="$PY $SK/weekly-lab-deck/scripts/lint_deck.py"
claude -p "Use the weekly-lab-deck skill to build the lab meeting deck and progress log. Output folder: $HOME/LabDecks/2026-W45. BUILD command: $BUILD . LINT command: $LINT . Call week_evidence with since=\"2026-11-02T13:00\" until=\"2026-11-09T13:00\"." \
  --mcp-config "$T/mcp.json" --strict-mcp-config --output-format stream-json --verbose \
  --allowedTools mcp__progress-ledger__week_evidence Read Write Edit "Bash($BUILD:*)" "Bash($LINT:*)" \
  > docs/evidence/transcript_W45.jsonl
"$PY" - docs/evidence/transcript_W45.jsonl > docs/evidence/transcript_W45.md <<'P'
import json, sys
print("# Doer transcript, week of Nov 2-9 (tool calls and results, trimmed)\n")
for line in open(sys.argv[1]):
    try: e = json.loads(line)
    except ValueError: continue
    t = e.get("type")
    if t == "assistant":
        for c in e["message"].get("content", []):
            if c.get("type") == "tool_use":
                print(f"**→ {c['name']}** `{json.dumps(c.get('input'))[:400]}`\n")
            elif c.get("type") == "text" and c["text"].strip():
                print(f"> {c['text'].strip()[:600]}\n")
    elif t == "user":
        for c in e["message"].get("content", []):
            if isinstance(c, dict) and c.get("type") == "tool_result":
                body = c.get("content")
                if isinstance(body, list): body = " ".join(x.get("text","") for x in body if isinstance(x, dict))
                print(f"```\n{str(body)[:1200]}\n```\n")
    elif t == "result":
        print(f"## Final reply\n\n{e.get('result','')}\n")
P
echo "transcript lines: $(wc -l < docs/evidence/transcript_W45.jsonl)"

echo "== 4. copy run records"
for W in 2026-W43 2026-W45; do
  R=$(ls -d "$HOME/Library/Logs/labdeck/$W"-* | sort | tail -1)
  rm -rf "docs/runs/$W"; cp -R "$R" "docs/runs/$W"; cp "$HOME/LabDecks/$W/"* "docs/runs/$W/"
  echo "$W <- $R"
done

echo "== 5. git"
[ -d .git ] || git init -q -b main
git add -A
git commit -q -m "lab-deck-toolkit: no-rewrite checker skill + progress-ledger MCP server

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01XnNMwz1ZbfooECLkKFfSJG" && git log --oneline | head -3
git ls-files | sed 's/^/  /'
if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
  echo "== gh user: $(gh api user -q .login)"
  git remote get-url origin >/dev/null 2>&1 || gh repo create lab-deck-toolkit --public --source . --remote origin --description "Checker skill (no-rewrite) + MCP server (progress-ledger) for 15-113"
  git push -u origin main && echo "== PUSHED: $(gh repo view --json url -q .url)"
else
  echo "== NO_GH: gh CLI missing or not logged in; repo committed locally only"
  git remote -v
fi
echo "== DONE"
