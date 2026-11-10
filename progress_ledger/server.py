"""progress-ledger: a one-tool MCP server that gives an agent structured,
read-only access to one week of research progress in a git repo.

The agent can't otherwise answer "what did I actually do this week?" reliably:
it would guess from file mtimes or memory. This tool reads git history and
figure caption sidecars and returns only what is on record.
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

try:  # mcp SDK 2.x renamed FastMCP to MCPServer; the course example uses 1.x
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP

CONFIG_PATH = Path(os.environ.get(
    "LAB_DECK_CONFIG", Path(__file__).resolve().parent.parent / "config.json"))


def _cfg() -> dict:
    cfg = json.loads(CONFIG_PATH.read_text())
    for k in ("repo", "decks_dir", "template"):
        if k in cfg:
            cfg[k] = str(Path(cfg[k]).expanduser())
    return cfg


def _git(*args: str) -> str:
    out = subprocess.run(["git", "-C", _cfg()["repo"], *args],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def _window(since: str | None, until: str | None) -> tuple[datetime, datetime]:
    """Default: the most recent past lab meeting (Monday 13:00 local) to now."""
    end = datetime.fromisoformat(until) if until else datetime.now()
    if since:
        return datetime.fromisoformat(since), end
    cfg = _cfg()
    wd, hr = cfg.get("meeting_weekday", 0), cfg.get("meeting_hour", 13)
    start = (end - timedelta(days=(end.weekday() - wd) % 7)).replace(
        hour=hr, minute=0, second=0, microsecond=0)
    if start >= end:
        start -= timedelta(days=7)
    return start, end


def _branch_args() -> list[str]:
    """Which refs to read. Default: every local and remote branch, so work on a
    feature branch counts even when main is checked out. Never checks anything out."""
    branches = _cfg().get("branches", "all")
    return ["--branches", "--remotes"] if branches == "all" else list(branches)


def _commits(start: datetime, end: datetime) -> list[dict]:
    raw = _git("log", *_branch_args(), "--source",
               f"--since={start.isoformat()}", f"--until={end.isoformat()}",
               "--name-only", "--format=\x1e%h\x1f%cI\x1f%S\x1f%s\x1f%b\x1f")
    commits = []
    for rec in raw.split("\x1e")[1:]:
        h, date, ref, subj, body, files = rec.split("\x1f")
        commits.append({"hash": h, "date": date, "branch": ref.strip(),
                        "subject": subj.strip(), "body": body.strip(),
                        "files": [f for f in files.split("\n") if f.strip()]})
    return commits


def _figures(commits: list[dict]) -> tuple[list[dict], list[dict]]:
    cfg = _cfg()
    fig_dir = cfg.get("figures_dir", "figures").rstrip("/") + "/"
    repo = Path(cfg["repo"])
    seen: dict[str, dict] = {}
    for c in commits:  # newest first, so the first hit is the latest version
        for f in c["files"]:
            if (f.startswith(fig_dir) and f.lower().endswith((".png", ".jpg", ".jpeg"))
                    and f not in seen):
                seen[f] = {"path": f, "commit": c["hash"], "commit_date": c["date"]}
    eligible, ineligible = [], []
    cache = Path(os.path.expanduser(cfg.get("figure_cache", "~/Library/Caches/labdeck")))
    for f, rec in seen.items():
        # Read from the commit, not the working tree: the figure may live on a
        # branch that isn't checked out. Extract to a cache outside the repo.
        blob = subprocess.run(["git", "-C", str(repo), "show", f"{rec['commit']}:{f}"],
                              capture_output=True)
        if blob.returncode != 0:
            continue  # deleted in that commit
        img = cache / rec["commit"] / f
        img.parent.mkdir(parents=True, exist_ok=True)
        img.write_bytes(blob.stdout)
        rec["abs_path"] = str(img)
        side_path = str(Path(f).with_suffix(".json"))
        side = subprocess.run(["git", "-C", str(repo), "show", f"{rec['commit']}:{side_path}"],
                              capture_output=True, text=True)
        if side.returncode != 0:
            rec["reason"] = "no caption sidecar (.json) in that commit; re-save with save_fig()"
            ineligible.append(rec)
            continue
        try:
            rec["sidecar"] = json.loads(side.stdout)
        except json.JSONDecodeError as e:
            rec["reason"] = f"sidecar is not valid JSON: {e}"
            ineligible.append(rec)
            continue
        if str(rec["sidecar"].get("caption", "")).strip():
            eligible.append(rec)
        else:
            rec["reason"] = "sidecar has no caption"
            ineligible.append(rec)
    return eligible, ineligible


mcp = FastMCP("progress-ledger")


@mcp.tool()
def week_evidence(since: str | None = None, until: str | None = None) -> dict:
    """Return everything on record about Anabella's research progress for one
    reporting window, read from her git repo. Read-only.

    Default window: from the last Bruno Lab meeting (Monday 1 PM) until now.
    Pass ISO datetimes for `since`/`until` to report a past week.

    Returns:
      window: start, end, ISO week label (e.g. 2026-W46), next meeting date
      commits: hash, date, branch, subject, body, changed files, from every
        local and remote branch (no checkout). Commit messages are her
        own description of the work; do not infer results beyond them.
      figures.eligible: figures committed in the window that have a caption
        sidecar from save_fig(). Only these may appear in a deck, and only their
        caption may be used to describe them.
      figures.ineligible: figures committed in the window without a usable
        caption, with the reason.
      notes: her own notes for the week (blockers, questions), or "".
    Dates come from git commits, never from file modification times.
    """
    start, end = _window(since, until)
    y, w, _ = start.isocalendar()
    week = f"{y}-W{w:02d}"
    commits = _commits(start, end)
    eligible, ineligible = _figures(commits)
    cfg = _cfg()
    notes_p = Path(cfg["repo"]) / cfg.get("notes_dir", "notes") / f"{week}.md"
    return {
        "window": {"start": start.isoformat(timespec="minutes"),
                   "end": end.isoformat(timespec="minutes"),
                   "week": week,
                   "meeting_date": (start + timedelta(days=7)).date().isoformat()},
        "commits": commits,
        "figures": {"eligible": eligible, "ineligible": ineligible},
        "notes": notes_p.read_text().strip() if notes_p.exists() else "",
    }


if __name__ == "__main__":
    mcp.run()
