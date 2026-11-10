"""save_fig(): save a figure plus a caption sidecar so the weekly deck can use it.

    from save_fig import save_fig
    save_fig(fig, "caf_umap_res0.6",
             caption="CAF subclusters at res 0.6; iCAF/myCAF split on PDGFRA vs ACTA2",
             params={"resolution": 0.6})
Works with a matplotlib Figure or anything with .savefig (scanpy: pass plt.gcf()).
Then commit both files: figures/<name>.png and figures/<name>.json
"""
import json
import subprocess
import sys
import warnings
from datetime import datetime
from pathlib import Path


def save_fig(fig, name, caption, params=None, dir="figures", dpi=200):
    if not caption.strip():
        raise ValueError("caption is required")
    d = Path(dir)
    d.mkdir(parents=True, exist_ok=True)
    png = d / f"{name}.png"
    fig.savefig(png, dpi=dpi, bbox_inches="tight")
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True).stdout.strip() or None
    except OSError:
        commit = None
    meta = {"caption": caption,
            "created": datetime.now().isoformat(timespec="seconds"),
            "script": sys.argv[0] or None,
            "params": params or {},
            "code_commit": commit}
    (d / f"{name}.json").write_text(json.dumps(meta, indent=2))
    if png.stat().st_size > 1024 * 1024:
        warnings.warn(f"{png} is over 1 MB; keep figures small for git")
    return png
