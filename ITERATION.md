# Iteration: the failure and the fix
Failure 1. docs/revisions/failure_run1_W43/check.txt. The checker’s verdict was VERDICT: CANNOT CHECK. 


## What went wrong
It says “Both attempts to run the script were blocked at the permission step. The first was a compound command, the second a single call.”
It tried this command: /Users/…/lab-deck-toolkit/.venv/bin/python .claude/skills/no-rewrite/scripts/snapshot.py diff /Users/…/before.json
In the same round a different week checker issues the command in a different form and it matched and passed. 
This meant that the outcome was inconsistent. in both weeks, the build and lint commands were “held for your approval”, so no .pptx was produced (failure_run1_W43/doer.txt).


## Why (my diagnosis)
There were conflicting instructions with the v1 skill text that said “Run python3 .claude/skills/no-rewrite/scripts/snapshot.py diff <before.json>” (no-rewrite_v1_SKILL.md). 
The prompt separately said “Run the script with $PY”. The agent combined them in different ways on different runs: absolute Python with a relative script, an absolute script path, and once a chained ls … && … command. Only some of those forms matched the rule.
the skill described what to run loosely and left the agent to assemble the exact command which is where the problem occured
## What I changed, and the rerun
run_weekly.sh: the exact commands are built once as absolute strings:
BUILD="$PY $SK/weekly-lab-deck/scripts/build_deck.py"
LINT=…
DIFF="$PY $SK/no-rewrite/scripts/snapshot.py diff $RUN/before.json"
The same string goes into both the prompt and the permission rule: Bash($BUILD:*), Bash($LINT:*), and an exact Bash($DIFF) for the checker.
skills/no-rewrite/SKILL.md was changed so that “Run the diff command given in the prompt exactly as written, as one command. Do not chain commands (&&, ;, |), do not add ls/cat checks first, and do not rewrite the paths… If that one command is refused, output VERDICT: CANNOT CHECK with the refusal and stop.”
skills/weekly-lab-deck/SKILL.md was changed using the same idea
The result was that both checker returned PASS and allowed both decks to be built.
