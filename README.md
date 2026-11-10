# lab-deck-toolkit


## What it does
This is a a no-rewrite skill that reports if a file an agent created, modified, or deleted is outside an allowed-paths list. 
It compares a snapshot taken before the task against the file system after. The output either passes
or fails and is follwed by numbered violations and allowed changes. The MCP tool week_evidence returns for a date window the following:
commits from every local and remote branch, captioned figures and uncaptioned ones, weekly notes. This builds a record for me in powerpoint
form so I can keep track of everything I've done for the week and makes it easiser for me to put together presentations in the future. 

## Why: evidence from my prompt logs
The checker evidence I found was in my HW6 and HW7. I repeated "don't modify/touch the files", "don't build/run X yet" and
"only do/run this step" in different forms various times. 
Quotes: Whitespace/prompt_log.md:434: “The code is frozen: do NOT modify app.py, config.py, db.py, scoring.py, llm.py, or ingest.py. If a test reveals a bug, record it in the report — don’t fix it.”
Whitespace/prompt_log.md:96: “Two things, both read-only. Don’t modify find_targets.py or inspect_data.py”
HW7/Pocket-Planks/prompt_log.md:46: “Don’t change GRAVITY, JUMP_SPEED, SPRING_SPEED, PLAYER_SPEED, or block sizes unless the prompt says to.”
I restated some of these restrictions multiple times but I never verified if it changed any of this or not. 
For the MCP evidence: I have a hard time keeping track of where I've left off from a previous week or finding data
I have previously produced. 
Quotes: Inside-Dose-/PROMPT_LOG.md:45: “read all the files and find out where I left off and what errors”
Inside-Dose-/PROMPT_LOG.md:55: “commit. Then read spec.md and figure out what the next step is”


## Install
Skill: copy skills/no-rewrite/ to ~/.claude/skills/no-rewrite/ (all projects) or <project>/.claude/skills/no-rewrite/ (one project). It needs Python 3 for scripts/snapshot.py. In this repo it’s linked as .claude/skills → skills
Server: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt (requirements: mcp>=1.9, python-pptx>=1.0).
Register it with claude mcp add progress-ledger -- /ABS/PATH/.venv/bin/python /ABS/PATH/progress_ledger/server.py, or with mcp.example.json plus --mcp-config.
Machine-specific: the absolute paths, LAB_DECK_CONFIG, and in config.json the repo, decks_dir and template paths.

## Confirmed working in
I confirmed in worked in Claude Code on macOS with python 3.13. The check works with sonnet and the doer works with a default model. 
I didn't test in Codex or in Cursor. I also ran a BANANA trivial-skill test and tool-visibility check to confirm it was working correctly. 


## Borrowed or adapted
The no-rewrite idea came from my prompt logs and also the course's skill-ideas. 
The spec-check example in the assignment gave me ideas for the structure
The server started as FastMCP and the mcp.io Python quickstart 
python-pptx to build decks. 

## How I used AI
I used Claude (Opus 5.5) for brainstorming and helping me mine through my past chats and prompt logs. 
I also used it to help write the code server.py, both skills, snapshot/build/lint scripts, run_weekly.sh, install.sh, .command files
I used it to run demos on my Mac and to diagnose any failures. 
