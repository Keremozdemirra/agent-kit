#!/usr/bin/env python3
"""Create a new projects/NNN-name/ project in the standard layout.

Writes structure only — the README's "what this is not" section, the tests that
assert a real property, and the example that actually runs are yours to fill in.
Refuses to overwrite anything, and refuses a project number already in use.

Usage:
    python3 scaffold.py <repo-root> <NNN> <project-name> \
        --package <python_package> \
        --description "one sentence" \
        [--cli <command>] [--keywords a,b,c]

Example:
    python3 scaffold.py ~/esg-toolkit 004 scope2-dual \
        --package scope2_dual \
        --description "Location-based and market-based Scope 2 side by side." \
        --cli scope2
"""

import argparse
import os
import re
import sys

PYPROJECT = '''[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = "{description}"
readme = "README.md"
requires-python = ">=3.9"
license = {{ text = "MIT" }}
keywords = [{keywords}]
dependencies = []
{scripts}
[tool.setuptools.packages.find]
include = ["{package}*"]
'''

SCRIPTS_BLOCK = '''
[project.scripts]
{cli} = "{package}.cli:main"
'''

README = '''# {title}

{description}

TODO: two or three sentences on the problem this exists for. Say what goes wrong
without it — the concrete failure, not the abstract benefit.

## What this is not

TODO: **the most useful section in this file.** Write it from the misuse you can
actually imagine someone committing, not from a liability worry. What will
someone reach for this tool to do that it does not do?

## Install

```bash
cd projects/{number}-{slug}
pip install -e .
```

## Use

{usage}

## Input format

TODO: describe the input, and point at `examples/` for a working one.

## Method

TODO: the arithmetic or algorithm, stated plainly enough that a reader can check
it. Where it follows a published method, cite the source with a vintage.

## Assumptions and limits

TODO: what has to be true for the output to mean anything.

## Tests

```bash
python3 -m unittest discover -s tests -t .
```

TODO: replace with the count once written, e.g. "42 tests, zero dependencies."

## Licence

MIT. See the repository [LICENSE](../../LICENSE).
'''

USAGE_CLI = '''```bash
{cli} examples/TODO-example-input.csv
```
'''

USAGE_LIB = '''```python
from {package} import TODO

TODO
```
'''

INIT = '''"""{description}"""

__all__ = []
'''

CLI = '''"""Command line entry point for {name}."""

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="{cli}",
        description="{description}",
    )
    parser.add_argument("input", help="path to the input file")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    # TODO: load, compute, report. Fail loudly on bad input rather than
    # returning a plausible-looking number.
    raise NotImplementedError(args.input)


if __name__ == "__main__":
    sys.exit(main())
'''

TEST = '''"""Tests for {package}.

The repo rule: a test asserts a real property, not that the code ran. Reach for
a conservation identity, a hand-computed known answer, or a case the tool is
supposed to refuse — and check that the test would fail if the function body
were replaced with `return input`.
"""

import unittest


class TODOProperty(unittest.TestCase):
    def test_TODO_replace_this(self):
        self.skipTest("scaffold placeholder — write a real property test")


if __name__ == "__main__":
    unittest.main()
'''

EXAMPLE_NOTE = """This directory holds executable inputs, not illustrations.

Someone should be able to run the tool against a file in here and see output on
their first try. If the input format changes, the example changes in the same
commit — a stale example fails for a reader who assumed it worked.

Delete this file once a real example exists.
"""


def slugify(s):
    return re.sub(r"[^a-z0-9-]+", "-", s.strip().lower()).strip("-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root")
    ap.add_argument("number", help="project number, e.g. 004")
    ap.add_argument("project_name", help="hyphenated slug, e.g. scope2-dual")
    ap.add_argument("--package", required=True, help="python package name")
    ap.add_argument("--description", required=True)
    ap.add_argument("--cli", default=None, help="console script name, if any")
    ap.add_argument("--keywords", default="")
    args = ap.parse_args()

    root = os.path.abspath(args.repo_root)
    projects = os.path.join(root, "projects")
    if not os.path.isdir(projects):
        print(f"no projects/ directory under {root} — is this the repo root?",
              file=sys.stderr)
        return 2

    number = args.number.zfill(3)
    if not re.fullmatch(r"\d{3}", number):
        print(f"project number must be three digits, got {args.number!r}",
              file=sys.stderr)
        return 2

    existing = sorted(d for d in os.listdir(projects)
                      if os.path.isdir(os.path.join(projects, d)))
    for d in existing:
        if d.startswith(number + "-"):
            print(f"number {number} is already taken by {d}", file=sys.stderr)
            print("existing projects: " + ", ".join(existing), file=sys.stderr)
            return 2

    slug = slugify(args.project_name)
    if not re.fullmatch(r"[a-z][a-z0-9_]*", args.package):
        print(f"package name must be a valid python identifier, got "
              f"{args.package!r}", file=sys.stderr)
        return 2

    proj = os.path.join(projects, f"{number}-{slug}")
    if os.path.exists(proj):
        print(f"{proj} already exists — refusing to overwrite", file=sys.stderr)
        return 2

    kw = ", ".join(f'"{k.strip()}"' for k in args.keywords.split(",") if k.strip())
    scripts = (SCRIPTS_BLOCK.format(cli=args.cli, package=args.package)
               if args.cli else "")
    usage = (USAGE_CLI.format(cli=args.cli) if args.cli
             else USAGE_LIB.format(package=args.package))

    os.makedirs(os.path.join(proj, args.package))
    os.makedirs(os.path.join(proj, "tests"))
    os.makedirs(os.path.join(proj, "examples"))

    written = []

    def write(rel, content):
        path = os.path.join(proj, rel)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        written.append(os.path.relpath(path, root))

    write("pyproject.toml", PYPROJECT.format(
        name=slug, description=args.description, keywords=kw,
        scripts=scripts, package=args.package))
    write("README.md", README.format(
        title=slug, description=args.description, number=number, slug=slug,
        usage=usage))
    write(f"{args.package}/__init__.py", INIT.format(description=args.description))
    if args.cli:
        write(f"{args.package}/cli.py", CLI.format(
            name=slug, cli=args.cli, description=args.description))
    write("tests/__init__.py", "")
    write(f"tests/test_{args.package}.py", TEST.format(package=args.package))
    write("examples/README.md", EXAMPLE_NOTE)

    print(f"Created projects/{number}-{slug}\n")
    for w in written:
        print(f"  {w}")

    print("\nStill to do — the scaffold is structure, not content:\n")
    print("  1. README: the 'What this is not' section, written from a misuse")
    print("     you can actually imagine someone committing.")
    print("  2. tests/: replace the placeholder with a property test — a")
    print("     conservation identity, a hand-computed known answer, or a case")
    print("     the tool is supposed to refuse.")
    print("  3. examples/: a real input file that runs on the first try, and")
    print("     delete examples/README.md.")
    print(f"  4. BACKLOG.md: move item {number} from Queue to Done, with the")
    print("     one-line summary and the test count.")
    print("  5. Root README.md: add the row to the project table.")
    print("\nThen verify:")
    print(f"  cd projects/{number}-{slug} && "
          "python3 -m unittest discover -s tests -t .")
    print("  (must also pass on Python 3.9 — no match, no runtime X | Y "
          "annotations, no tomllib)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
