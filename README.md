# lab-deck-toolkit

<!-- WRITE THIS YOURSELF. Required sections from the assignment are below. -->

## What it does
<!-- The no-rewrite skill: what it checks, when it triggers (see its `description` in skills/no-rewrite/SKILL.md). -->
<!-- The week_evidence MCP tool: what it returns (see the docstring in progress_ledger/server.py). -->

## Why: evidence from my prompt logs
<!-- Checker (repeated instruction), 12 scope restrictions across HW6 and HW7, e.g.:
     Whitespace/prompt_log.md:434, Whitespace/prompt_log.md:96, Whitespace/prompt_log.md:207,
     HW7/Pocket-Planks/prompt_log.md:46 -->
<!-- MCP tool (what the agent kept not knowing):
     Inside-Dose-/PROMPT_LOG.md:45 ("find out where I left off");
     github.io prompt-log (HW3) lines ~988-989 (rebuilding what each prompt did from git log by hand) -->

## Install
<!-- Skill: copy skills/no-rewrite/ into ~/.claude/skills/ (personal) or <project>/.claude/skills/ (project). -->
<!-- Server: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
     Register: mcp.example.json (replace /ABSOLUTE/PATH/TO, machine-specific), or
     claude mcp add progress-ledger -- /ABSOLUTE/PATH/.venv/bin/python /ABSOLUTE/PATH/progress_ledger/server.py
     Config: config.example.json -> config.json (repo path, template path: machine-specific) -->

## Confirmed working in
<!-- Claude Code 2.1.319 on macOS (doer: default model; checker: --model sonnet). -->

## Borrowed or adapted
<!-- no-rewrite idea: course skill-ideas list. Output-format/rules style: course spec-check example.
     MCP server: modelcontextprotocol.io Python quickstart (note: SDK 2.x renamed FastMCP to MCPServer). -->

## How I used AI
<!-- Cite the Claude chat(s) used; say which files Claude drafted (server.py, skills, scripts,
     docs/SETUP_NOTES.md) and what you decided/changed yourself. -->
