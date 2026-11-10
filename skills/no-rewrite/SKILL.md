---
name: no-rewrite
description: Checks which files an agent created, modified, or deleted against the list of paths it was allowed to touch, and reports every violation without fixing anything. Use after any agent task that came with scope limits ("only write to X", "don't modify Y"), when given a snapshot file and an allowed-paths list, or when asked what files an agent touched.
---

# No-rewrite check

You are reviewing another agent's work. You did not do it. Your only question
is: did it touch anything it wasn't allowed to?

## Inputs

1. A snapshot file taken before the task ran (`before.json`).
2. An allowed-paths file (`ALLOWED.txt`): one glob per line, absolute paths.
   Lines starting with `#` are comments. Anything not matched is off limits.

If either is missing, stop and output `VERDICT: CANNOT CHECK` with what's missing.

## Steps

1. Run the diff command given in the prompt **exactly as written, as one
   command**. Do not chain commands (`&&`, `;`, `|`), do not add `ls`/`cat`
   checks first, and do not rewrite the paths. Anything else is blocked by the
   permission rules. If that one command is refused, output
   `VERDICT: CANNOT CHECK` with the refusal and stop.
2. For every path in `created`, `modified`, and `deleted`, decide whether it
   matches a glob in ALLOWED.txt. Match the full absolute path.
3. Every entry under `git` is a violation unless ALLOWED.txt contains the line
   `git:<repo path>`. A moved HEAD means the agent committed or reset.
4. Write the report.

## Output format

First line, exactly one of: `VERDICT: PASS`, `VERDICT: FAIL`, `VERDICT: CANNOT CHECK`.

Then:

```
Touched: <n created> created, <n modified> modified, <n deleted> deleted
Violations:
1. <created|modified|deleted|git> <absolute path> — not covered by ALLOWED.txt
Allowed changes:
- <path> (matched <glob>)
```

Write `Violations: none` if there are none.

## Rules

- Do not fix, revert, move, or delete anything. Report only.
- Judge only from the snapshot diff. Never trust the other agent's own summary
  of what it changed.
- PASS only with zero violations. One stray file is a FAIL.
- A file the agent was allowed to create but also deleted is still reported
  under deleted. List it; don't excuse it.
- Do not judge the quality of the work. That is not this check.
