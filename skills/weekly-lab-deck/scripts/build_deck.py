"""Build the weekly lab-meeting deck from a JSON spec, using Anabella's template.

usage: python3 build_deck.py spec.json out.pptx [--template path] [--list-layouts]

spec.json:
{
  "title": "PDAC atlas: weekly update",
  "subtitle": "Anabella Phelps | 2026-11-16",
  "slides": [
    {"type": "figure", "title": "...", "figure": "/abs/path.png",
     "bullets": ["<=3 short lines"], "notes": "speaker notes", "cites": ["a1b2c3d"]},
    {"type": "text", "title": "...", "bullets": ["..."], "notes": "...", "cites": [...]}
  ]
}
The template's existing slides are removed; its master, layouts, theme and fonts are kept.
"""
import argparse
import json
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu, Pt

CONFIG = Path(__file__).resolve().parents[4] / "config.json"


def find_layout(prs, wanted, fallback_idx):
    for name in wanted:
        for lay in prs.slide_layouts:
            if lay.name.lower() == name.lower():
                return lay
    return prs.slide_layouts[min(fallback_idx, len(prs.slide_layouts) - 1)]


def clear_slides(prs):
    sldIdLst = prs.slides._sldIdLst
    for sldId in list(sldIdLst):
        prs.part.drop_rel(sldId.rId)
        sldIdLst.remove(sldId)


def drop_empty_placeholders(slide, keep):
    for ph in list(slide.placeholders):
        if ph.placeholder_format.idx not in keep:
            ph._element.getparent().remove(ph._element)


def add_bullets(slide, bullets, left, top, width, height, size):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = "• " + b
        p.space_after = Pt(8)
        for r in p.runs:
            r.font.size = Pt(size)
    return tb


def place_picture(slide, path, left, top, max_w, max_h):
    pic = slide.shapes.add_picture(str(path), left, top)
    scale = min(max_w / pic.width, max_h / pic.height)
    pic.width, pic.height = int(pic.width * scale), int(pic.height * scale)
    pic.left = int(left + (max_w - pic.width) / 2)
    pic.top = int(top + (max_h - pic.height) / 2)
    return pic


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--template")
    ap.add_argument("--list-layouts", action="store_true")
    a = ap.parse_args()
    cfg = json.loads(CONFIG.read_text()) if CONFIG.exists() else {}
    template = Path(a.template or cfg.get("template", "")).expanduser()
    prs = Presentation(str(template)) if template.is_file() else Presentation()

    if a.list_layouts:
        for i, lay in enumerate(prs.slide_layouts):
            print(i, lay.name, [p.placeholder_format.type for p in lay.placeholders])
        return

    spec = json.loads(Path(a.spec).read_text())
    body_pt = cfg.get("body_font_pt", 18)
    clear_slides(prs)
    W, H = prs.slide_width, prs.slide_height
    m = int(W * 0.04)

    title_lay = find_layout(prs, cfg.get("title_layouts", ["Title Slide"]), 0)
    s = prs.slides.add_slide(title_lay)
    if s.shapes.title is not None:
        s.shapes.title.text = spec["title"]
    subs = [p for p in s.placeholders if p.placeholder_format.idx != 0]
    if subs and spec.get("subtitle"):
        subs[0].text = spec["subtitle"]
        drop_empty_placeholders(s, {0, subs[0].placeholder_format.idx})
    else:
        drop_empty_placeholders(s, {0})

    content_lay = find_layout(prs, cfg.get("content_layouts", ["Title Only", "Title and Content"]), 5)
    for sd in spec["slides"]:
        s = prs.slides.add_slide(content_lay)
        if s.shapes.title is not None:
            s.shapes.title.text = sd["title"]
            top = s.shapes.title.top + s.shapes.title.height + int(H * 0.02)
        else:
            top = int(H * 0.18)
        drop_empty_placeholders(s, {0})
        avail_h = H - top - m
        bullets = sd.get("bullets", [])
        if sd.get("type") == "figure":
            fig_w = int((W - 2 * m) * (0.66 if bullets else 1.0))
            place_picture(s, sd["figure"], m, top, fig_w, avail_h)
            if bullets:
                add_bullets(s, bullets, m + fig_w + int(m / 2), top,
                            W - fig_w - int(2.5 * m), avail_h, body_pt)
        else:
            add_bullets(s, bullets, m, top, W - 2 * m, avail_h, body_pt)
        notes = sd.get("notes", "")
        if sd.get("cites"):
            notes += "\n\nSources: " + ", ".join(sd["cites"])
        if notes.strip():
            s.notes_slide.notes_text_frame.text = notes.strip()

    prs.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
