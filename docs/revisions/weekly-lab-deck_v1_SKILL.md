---
name: weekly-lab-deck
description: Builds Anabella's weekly Bruno Lab meeting deck (Mondays 1 PM) and a progress log from the week's git commits, captioned figures, and her notes, using the progress-ledger week_evidence tool and her lab-meeting template. Use when asked for this week's lab meeting slides or a weekly progress update, or when the scheduled weekly run fires.
---

# Weekly lab deck

You report what Anabella did this week. You do not do science, interpret data,
or make annotation calls. Every biological statement must already exist in her
words: a commit message, a figure caption, or her notes.

## Where you may write

Only inside the output folder given in the prompt (`<decks_dir>/<week>/`).
Nothing else: not the research repo, not the toolkit folder, not your working
directory. Every file you create, including scratch files, goes in the output
folder. A separate checker compares the file system before and after your run.

## Steps

1. Call `week_evidence` once (with `since`/`until` if the prompt gives them).
2. Write `<out>/progress_log.md` (format below).
3. Write `<out>/spec.json` and build the deck:
   `python3 .claude/skills/weekly-lab-deck/scripts/build_deck.py <out>/spec.json <out>/lab_meeting_<meeting_date>.pptx`
4. Lint it: `python3 .claude/skills/weekly-lab-deck/scripts/lint_deck.py <deck>`.
   Fix every violation by cutting text or moving it to speaker notes, rebuild,
   lint again. Stop after 3 attempts and list what still fails.
5. Print the deck path, log path, and any remaining lint violations.

## Deck structure

1. Title slide: "PDAC atlas: weekly update", subtitle "Anabella Phelps | <meeting_date>".
2. One figure slide per eligible figure, newest first, max 4. Title = the
   caption's first clause. Bullets = at most 3 short lines from the caption or
   the commit that added the figure. Full caption and params go in speaker notes.
3. "What changed this week": at most 4 bullets, one per commit or group of
   related commits, in plain words.
4. "Blockers / questions for the lab": only from `notes`. Omit if she wrote none.
5. "Missing figures": only if any figures are ineligible; list file and reason.

## Rules

- Every slide in spec.json carries `cites`: the commit hashes and figure paths
  it draws on. No citable source, no slide.
- Use only eligible figures, and never describe a figure beyond its caption.
- Never name a cell type, cluster identity, resolution, or result that is not
  written in a commit message, caption, or her notes.
- Quiet week (no commits, no figures): a 2-slide deck, title plus
  "No new results this week" and her notes if any. Do not pad.
- Fewer words, more figures. On-slide text obeys the lint limits; the rest
  goes in speaker notes.

## Progress log format

```
# <week> (<start> to <end>)

## Done
- <plain-words summary> (<hash>)

## Figures
- <figure path>: <caption> (<hash>)

## Notes
<her notes verbatim, or "none">

## Not in deck
- <ineligible figure>: <reason>
```
