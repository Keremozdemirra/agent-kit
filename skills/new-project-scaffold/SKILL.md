---
name: new-project-scaffold
description: Creates a new numbered project inside the projects/NNN-name/ monorepo layout used by esg-toolkit, cbam-calc, analyst-toolkit, open-climate-data and unitguard — package directory, unittest suite, executable example, pyproject with requires-python >=3.9 and zero dependencies, and a README whose "what this is not" section is mandatory. Also updates BACKLOG.md and the root README project table, which are the two places a new project is referenced from and the two places people forget. Use this skill whenever the user wants to start a new project or tool in one of these repos, picks up the next unchecked item from BACKLOG.md, or says "yeni proje", "yeni araç ekle", "004'ü yapalım", "add a new tool", "scaffold a project", "start the next backlog item". Also use it when reviewing whether an existing project follows the layout, since it encodes the conventions those repos already hold themselves to.
---

# New project scaffold

These repos share one shape: `projects/NNN-project-name/`, self-contained, its
own README and tests, no shared framework to learn. The shape is the point —
a tool you can read in a sitting is worth more than a tool that participates in
an architecture.

This skill creates a new project in that shape and wires it into the two places
it has to be referenced from. It is deliberately opinionated, because the
conventions here are already written down in `BACKLOG.md` and the point is that
they survive a session where nobody re-reads them.

## Before creating anything

**Read `BACKLOG.md` first.** The next unchecked item is the one being built, and
an item that is half-built outranks starting a new one — check for a `status:`
note before assuming the queue's top item is free.

**Confirm the job is one job.** The rule is one tool, one job, done properly,
rather than a suite of half-features. If the described project has an "and" in
it, that is usually two projects, and splitting now is much cheaper than
splitting after the tests exist.

**Confirm the number.** Project numbers are referenced from `BACKLOG.md` and
from the root `README.md` table. Take the next free one, and check the backlog
for a number already reserved for this item — the queue sometimes assigns them
ahead of time, and it has collided before.

## Create it

```bash
python3 "$SKILL_DIR/scripts/scaffold.py" <repo-root> <NNN> <project-name> \
    --package <python_package_name> \
    --description "one sentence, what it does" \
    --cli <command-name>          # omit if there is no CLI
```

It writes the directory, a README skeleton with the required sections, a
`pyproject.toml` matching the sibling projects, an empty test module and an
`examples/` placeholder, then prints what you still have to fill in. It refuses
to overwrite an existing project directory, and it refuses a number already in
use.

## Then fill in the parts that matter

The scaffold is structure, not content. Four things carry the actual weight:

### The README's "What this is not" section

This is the section that stops someone using an LMDI decomposition as a
forecast, or a top-down market size as a revenue projection. It is not a
disclaimer — it is the most useful paragraph in the file, because it tells a
reader in one pass whether to keep reading.

Write it from the misuse you can actually imagine someone committing. "Not a
substitute for professional advice" is filler; "this attributes an emissions
change to four effects, it does not tell you which of them you caused" is the
real thing.

### Tests that assert a property

The repo rule is that tests assert a real property, not that the code ran. The
test to reach for first:

- **Conservation / identity.** The decomposition's effects sum to the total
  change. The exact solver never costs more than the greedy one. Round-tripping
  a serialisation returns the input. These catch real regressions and they read
  as documentation.
- **Known-answer.** A hand-computed case with the arithmetic shown in a comment.
  One of these is worth ten smoke tests.
- **The raising cases.** What the tool refuses to do is part of its contract —
  ambiguous conversions, missing vintages, inconsistent units. If the README
  claims it rejects something, there is a test proving it rejects it.

A useful check: would this test still pass if the function body were replaced by
`return input`? If yes, it is not a test.

### An example that runs

`examples/` holds executable inputs, not illustrations. Someone should be able
to run the CLI against the example file and see output on their first try. If
the input format later changes, the example changes in the same commit — a stale
example is worse than none, because it fails for a reader who assumes it works.

### Citations with vintages

Any published factor, threshold or rate carries a citation **and** the vintage of
the data. Figures go stale; the citation is how the reader finds out. If the
project touches emission factors, regulatory values, GWPs or market benchmarks,
use the `source-check` skill for them rather than taking a number from memory —
in `cbam-calc` especially, where a wrong factor ends up in a declaration someone
signs.

## Wire it in

Two files reference every project, and both are easy to forget:

1. **`BACKLOG.md`** — move the item from Queue to Done, with the one-line summary
   and the test count. The existing entries set the tone: what it does, what was
   notable about it, how many tests, dependency count.
2. **Root `README.md`** — add the row to the project table. The "What it does"
   cell is one sentence and it is often the only thing anyone reads about the
   project, so write it last, when you know what the tool turned out to be.

## Verify before committing

```bash
cd projects/NNN-project-name && python3 -m unittest discover -s tests -t .
```

That is the command in the README and the one CI runs. Then check:

- Tests pass on **Python 3.9** as well as current — no `match`, no runtime
  `X | Y` annotations, no `tomllib`. CI tests both, but finding it locally is
  faster than finding it in a red check.
- `dependencies = []` still holds. If this project genuinely needs the repo's
  first dependency, say why in the commit message; that is a decision, not a
  detail.
- The example actually runs.
- `BACKLOG.md` and the root README table both updated.

Use `zero-hallucination-coder` for the implementation itself if the project
involves non-trivial arithmetic — in these repos it usually does, and a formula
that is quietly wrong produces a number that goes into a client deck rather than
an error.
