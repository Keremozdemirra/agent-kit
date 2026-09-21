---
name: new-project-scaffold
description: Creates a new numbered project in the projects/NNN-name/ layout of the toolkit repos: package dir, unittest suite, executable example, zero-dependency pyproject (python >=3.9), README with a mandatory "what this is not" section, plus the BACKLOG and root README table updates. Use to start a project or tool in those repos, pick the next BACKLOG item ("yeni proje", "yeni arac ekle", "scaffold a project"), or check an existing layout. Not for a multi-part build; use proje.
---

# New project scaffold

These repos share one shape: `projects/NNN-project-name/`, self-contained, its
own README and tests, no shared framework to learn. The shape is the point: a
tool you can read in a sitting is worth more than a tool that participates in
an architecture.

This skill creates a new project in that shape and wires it into the two places
it has to be referenced from. It is deliberately opinionated, because the
conventions here are already written down in `BACKLOG.md` and the point is that
they survive a session where nobody re-reads them.

## Before creating anything

**Read `BACKLOG.md` first.** The next unchecked item is the one being built, and
an item that is half-built outranks starting a new one. Check for a `status:`
note before assuming the queue's top item is free.

**Confirm the job is one job.** The rule is one tool, one job, done properly. If
the described project has an "and" in it, that is usually two projects, and
splitting now is much cheaper than splitting after the tests exist.

**Confirm the number.** Project numbers are referenced from `BACKLOG.md` and
from the root `README.md` table. Take the next free one, and check the backlog
for a number already reserved for this item; the queue sometimes assigns them
ahead of time, and it has collided before.

## Create it

```bash
# $SKILL_DIR is not set in every runtime; locate the script directly.
SCAFFOLD="$(find "$HOME/.claude/skills" "$HOME/agents" -name scaffold.py -path '*new-project-scaffold*' -print -quit 2>/dev/null)"
python3 "$SCAFFOLD" <repo-root> <NNN> <project-name> \
    --package <python_package_name> \
    --description "one sentence, what it does" \
    --cli <command-name>          # omit if there is no CLI
```

If `$SCAFFOLD` comes back empty the skill lives somewhere these roots do not
cover. Ask the user where it is installed.

It writes the directory, a README skeleton with the required sections, a
`pyproject.toml` matching the sibling projects, an empty test module and an
`examples/` placeholder, then prints what you still have to fill in. It refuses
to overwrite an existing project directory, and it refuses a number already in
use.

## Then fill in the parts that matter

The scaffold is structure. The content is yours, and four things carry the
weight:

### The README's "What this is not" section

This is the section that stops someone using an LMDI decomposition as a
forecast, or a top-down market size as a revenue projection. It is the most
useful paragraph in the file, because it tells a reader in one pass whether to
keep reading.

Write it from a misuse you can picture someone committing. "Not a substitute
for professional advice" is filler; "this attributes an emissions change to
four effects, it does not tell you which of them you caused" is the real thing.

### Tests that assert a property

The repo rule is that every test asserts a real property of the output. The
test to reach for first:

- **Conservation / identity.** The decomposition's effects sum to the total
  change. The exact solver never costs more than the greedy one. Round-tripping
  a serialisation returns the input. These catch real regressions and they read
  as documentation.
- **Known-answer.** A hand-computed case with the arithmetic shown in a comment.
  One of these is worth ten smoke tests.
- **The raising cases.** What the tool refuses to do is part of its contract:
  ambiguous conversions, missing vintages, inconsistent units. If the README
  claims it rejects something, there is a test proving it rejects it.

A useful check: would this test still pass if the function body were replaced by
`return input`? If yes, rewrite it until the answer is no.

### An example that runs

`examples/` holds executable inputs. Someone should be able to run the CLI
against the example file and see output on their first try. If the input format
later changes, the example changes in the same commit; a stale example is worse
than none, because it fails for a reader who assumes it works.

Any output the README shows for the example, and any table that says which
input produces which result, comes from a run: paste it from the terminal, and
run it again whenever the code changes. A table written from the design reads
as evidence, and the first reader who tries it finds the row that never fired.
Where a claim cannot be checked by running, say what was checked and what was
not.

### Citations with vintages

Any published factor, threshold or rate carries a citation **and** the vintage of
the data. Figures go stale; the citation is how the reader finds out. If the
project touches emission factors, regulatory values, GWPs or market benchmarks,
run the `source-check` skill on every one of them. In `cbam-calc` especially, a
wrong factor ends up in a declaration someone signs.

When a figure's primary source cannot be reached, write that beside the figure
in the README: what was checked, what was not, and whether the result depends
on it. The note closes the finding while keeping the record and the rule, and
writing it honestly sometimes ends with the figure coming out.

## Wire it in

Two files reference every project, and both are easy to forget:

1. **`BACKLOG.md`**: move the item from Queue to Done, with the one-line summary
   and the test count. The existing entries set the tone: what it does, what was
   notable about it, how many tests, dependency count.
2. **Root `README.md`**: add the row to the project table. The "What it does"
   cell is one sentence and it is often the only thing anyone reads about the
   project, so write it last, when you know what the tool turned out to be.

## Verify before committing

```bash
cd projects/NNN-project-name && python3 -m unittest discover -s tests -t .
```

That is the command in the README and the one CI runs. Then check:

- Tests pass on **Python 3.9** as well as current: no `match`, no runtime
  `X | Y` annotations, no `tomllib`. CI tests both, but finding it locally is
  faster than finding it in a red check.
- `dependencies = []` still holds. If this project needs the repo's first
  dependency, say why in the commit message; that sentence is the decision
  record.
- `grep -rn TODO .` inside the project returns nothing, and the unittest
  summary reports no skipped test. The scaffold marks every unfilled section,
  the example input and the placeholder test with `TODO`, so the layout check
  passes on an untouched skeleton; this grep is what tells the two apart.
- The example runs, and the output the README shows for it is what it printed.
- `BACKLOG.md` and the root README table both updated.

Use `zero-hallucination-coder` for the implementation itself if the project
involves non-trivial arithmetic. In these repos it usually does, and a formula
that is quietly wrong produces a plausible number that goes into a client deck.
