"""Record or compare the state of a set of folders, to find what an agent touched.

  python3 snapshot.py take  <out.json> <root> [<root> ...]
  python3 snapshot.py diff  <before.json>

`take` records size + sha256 (size+mtime for files over 50 MB) for every file under each root (skipping .git
internals, .venv, __pycache__, .DS_Store) and, for any root that is a git repo,
HEAD and `git status --porcelain`. `diff` re-scans the same roots and prints
JSON: created, modified, deleted files, and git changes (HEAD moved, status
changed). It reports facts only; judging them is the checker's job.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules"}
SKIP_FILES = {".DS_Store"}
BIG = 50 * 1024 * 1024


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _git(root: Path, *args):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def scan(roots):
    files, git = {}, {}
    for r in roots:
        root = Path(r).expanduser().resolve()
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
                continue
            if p.is_file() and p.name not in SKIP_FILES:
                st = p.stat()
                # big data files (.rds/.h5ad): size+mtime instead of hashing GBs every run
                fp = _sha(p) if st.st_size < BIG else f"size={st.st_size};mtime={st.st_mtime_ns}"
                files[str(p)] = {"size": st.st_size, "sha256": fp}
        if (root / ".git").exists():
            git[str(root)] = {"head": _git(root, "rev-parse", "HEAD"),
                              "status": _git(root, "status", "--porcelain")}
    return {"roots": [str(Path(r).expanduser().resolve()) for r in roots],
            "files": files, "git": git}


def diff(before):
    after = scan(before["roots"])
    b, a = before["files"], after["files"]
    git_changes = []
    for root, g in before["git"].items():
        g2 = after["git"].get(root, {})
        if g.get("head") != g2.get("head"):
            git_changes.append({"repo": root, "change": "HEAD moved",
                                "before": g.get("head"), "after": g2.get("head")})
        if g.get("status") != g2.get("status"):
            git_changes.append({"repo": root, "change": "working tree status changed",
                                "before": g.get("status"), "after": g2.get("status")})
    return {"roots": before["roots"],
            "created": sorted(set(a) - set(b)),
            "modified": sorted(k for k in set(a) & set(b) if a[k]["sha256"] != b[k]["sha256"]),
            "deleted": sorted(set(b) - set(a)),
            "git": git_changes}


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "take":
        Path(sys.argv[2]).write_text(json.dumps(scan(sys.argv[3:])))
        print(sys.argv[2])
    elif cmd == "diff":
        print(json.dumps(diff(json.loads(Path(sys.argv[2]).read_text())), indent=1))
    else:
        sys.exit(__doc__)
