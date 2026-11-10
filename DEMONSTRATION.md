# Demonstration


## The real task
My real task is to build weekly powerpoint decks from my repo that I'm currently working in for my research. 
The week_evidence MCP tool and weekly-lab-deck skill write a progress log and slide spec so that a .pptx can be built using
a template that I created from past powerpoints I've put together. The no-rewrite checker runs in a seperate session and 
checks that the week_evidence MCP agent only wrote inside the currect directory and didn't make any changes to files. 
The allowed paths are my atlas repo and tollkit folder and this runs on a schedule weekly. 


## Run 1: week of Oct 19-26 (main, 5 commits)
Evidence: 5 commits on main, no figures, no notes
the agent: wrote progress_log.md with one line per commit and its hash. It made a 2-slide 
deck with a title slide and bullet points for what changed this week. I have a rule
about minimizing text on slides so the rest was put in speaker notes. The checker to make 
sure no files were disturbed or changed returned that it passed having not created any mew files
and only modifired the powerpoint file and the spec.json. 

## Run 2: week of Nov 2-9 (protect-lineage-markers, 3 commits)
Evidence: 3 commits.
Tool calls: 1. Skill(weekly-lab-deck)
2. ToolSearch 
3. week_evidence(since="2026-11-02T13:00", until="2026-11-09T13:00"), which returned the window (week W45, meeting 2026-11-09), the 3 commits with their bodies, empty figures and empty notes
4. Read of build_deck.py and lint_deck.py
5. write of progress_log.md and spec.json
6. a Bash ls of the output folder which was blocked by the permissions
7. a rewrite of both files 
8. Bash build, then lint 
This resulted in a 2-slide deck with 3 bullets that passed lint on the first try. 
The check returned a verdict: pass. This was consistent with earlier runs


## What the checker caught, and whether I agree
In the final runs there were no violations. 
In the earlier runs it returned CANNOT CHECK. The run where the checker flagged a stray spec.json and an edit to a .R was a simulated doer in my sandbox.
I agree with the checkers assesment however I need to check to further tune to make sure "modified" files inside the week folder
aren't flagged. I also need to account that the slide smmaries are accurate since the checker can't judge content at all. 
