#!/bin/bash
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
LOG="$(cd .. && pwd)/labdeck-demo/push.log"
exec > >(tee "$LOG") 2>&1
git add README.md DEMONSTRATION.md ITERATION.md .gitignore push.command
git commit -m "Add README, DEMONSTRATION and ITERATION write-ups

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01XnNMwz1ZbfooECLkKFfSJG"
git push origin main && echo "== PUSHED" && git log --oneline -3
git status --short
