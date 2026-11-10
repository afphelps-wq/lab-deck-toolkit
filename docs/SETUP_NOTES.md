> Setup notes drafted by Claude (Opus 5.5) during the build; see README for my own write-up.

# lab-deck-toolkit

> **WRITE THIS YOURSELF:** the evidence section (quotes from HW6/HW7 logs), the
> demonstration notes, and the failure-and-revision write-up. This README only
> documents how the toolkit works.

Every Sunday at 8 PM my Mac builds the deck for Monday's 1 PM Bruno Lab meeting
from what I actually committed that week. A separate agent on a different model
then checks that the builder touched only what it was allowed to.

```
launchd (Sun 8 PM) -> run_weekly.sh
  1. git fetch --all               (every branch; never touches checked-out files)
  2. snapshot.py take              (repo, toolkit, decks folder)
  3. doer   (default model):  week_evidence MCP tool + weekly-lab-deck skill -> deck + log
  4. checker (--model sonnet, fresh session, no MCP): no-rewrite skill -> VERDICT
  5. macOS notification
```

## The graded pieces

| Requirement | Piece | Path |
|---|---|---|
| Skill (checker, reports only) | `no-rewrite` | `skills/no-rewrite/` (symlinked at `.claude/skills`) |
| MCP server, one tool | `progress-ledger` → `week_evidence(since, until)` | `progress_ledger/server.py` |
| Real task | weekly lab deck | `.claude/skills/weekly-lab-deck/` |

- **Why `no-rewrite` is a skill:** it needs no new capability, only a procedure
  (diff the snapshot, match against allowed globs, report, never fix).
- **Why `week_evidence` is an MCP server:** it gives the agent structured access
  it doesn't have otherwise: commits in a date window, which figures have
  caption sidecars, and my weekly notes, dated by git, not by file mtimes.

## Setup (Mac, ~15 min)

1. `cp config.example.json config.json`; set `repo` and `template` (the Drive-synced
   path to `Lab_Meeting_11_09_26_Phelps_v5.pptx`).
2. `./install.sh` (venv, `mcp.json`, LaunchAgent).
3. `.venv/bin/python .claude/skills/weekly-lab-deck/scripts/build_deck.py --list-layouts`
   and put your template's layout names in `title_layouts` / `content_layouts`.
4. Check registration: `claude mcp list --mcp-config mcp.json`, or start `claude`
   in this folder with `--mcp-config mcp.json` and ask it to call `week_evidence`.

## Demo runs on past weeks (no waiting)

```
./run_weekly.sh 2026-10-19T13:00 2026-10-26T13:00   # main: rebuild v3 (5 commits)
./run_weekly.sh 2026-11-02T13:00 2026-11-09T13:00   # protect-lineage-markers: v4 (3 commits)
```
`week_evidence` reads every local and remote branch without checking any out.
Each run leaves `~/Library/Logs/labdeck/<week>-<time>/`: `before.json`, `ALLOWED.txt`,
`doer.txt` (what the agent did), `check.txt` (the verdict), `run.log`.

## Weekly habit

- Save figures with `save_fig(p, name, caption = "...")` (`helpers/`) and commit
  PNG + JSON. Under 1 MB each; never commit `.rds`/`.h5ad`.
- Commit messages say what you decided ("chose res 0.8"); they become slide text.
- Optional `notes/<YYYY-Www>.md` in the repo for blockers and questions for the lab.

## Limits

- The checker only sees the watched roots (repo, toolkit, decks folder). A write
  elsewhere in `~` would go unnoticed.
- Files over 50 MB are compared by size+mtime, not hash.
- `lint_deck.py` overflow is a character-count estimate, not a render.
- The research repo must stay private: unpublished lab data.
