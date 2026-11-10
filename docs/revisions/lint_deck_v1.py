"""Measure a .pptx against the style limits in config.json.

usage: python3 lint_deck.py deck.pptx
Prints JSON: per-slide word count (speaker notes excluded), picture count,
smallest explicit font size, likely text overflow (a character-count estimate,
not a render), plus a list of violations. Exit code 1 if any violations.
"""
import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

CONFIG = Path(__file__).resolve().parents[4] / "config.json"


def lint(path):
    cfg = json.loads(CONFIG.read_text()) if CONFIG.exists() else {}
    max_words = cfg.get("max_words_per_slide", 30)
    min_font = cfg.get("min_font_pt", 14)
    slides, violations = [], []
    for i, slide in enumerate(Presentation(path).slides, start=1):
        words, pics, fonts, overflow = 0, 0, [], []
        for shp in slide.shapes:
            if shp.shape_type == 13:  # PICTURE
                pics += 1
            if not shp.has_text_frame:
                continue
            text = shp.text_frame.text
            words += len(text.split())
            sizes = [r.font.size.pt for p in shp.text_frame.paragraphs
                     for r in p.runs if r.font.size]
            fonts += sizes
            if text.strip() and shp.width and shp.height:
                pt = min(sizes) if sizes else 18
                per_line = max(1, int(Emu(shp.width).pt / (pt * 0.5)))
                lines = sum(max(1, -(-len(p.text) // per_line))
                            for p in shp.text_frame.paragraphs)
                if lines * pt * 1.2 > Emu(shp.height).pt * 1.15:
                    overflow.append(shp.name)
        rec = {"slide": i, "words": words, "pictures": pics,
               "min_font_pt": min(fonts) if fonts else None,
               "likely_overflow": overflow}
        slides.append(rec)
        if i > 1 and words > max_words:
            violations.append(f"slide {i}: {words} words (limit {max_words})")
        if rec["min_font_pt"] and rec["min_font_pt"] < min_font:
            violations.append(f"slide {i}: font {rec['min_font_pt']}pt (min {min_font})")
        if overflow:
            violations.append(f"slide {i}: text likely overflows {overflow}")
    if len(slides) > 2 and not any(s["pictures"] for s in slides[1:]):
        violations.append("deck has no figures")
    return {"slides": slides, "violations": violations,
            "limits": {"max_words_per_slide": max_words, "min_font_pt": min_font}}


if __name__ == "__main__":
    r = lint(sys.argv[1])
    print(json.dumps(r, indent=1))
    sys.exit(1 if r["violations"] else 0)
