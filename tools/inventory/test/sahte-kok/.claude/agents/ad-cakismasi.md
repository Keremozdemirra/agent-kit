---
name: kisa-aciklama
description: Sample agent definition built to exercise name collision in the fake root; the name field in the frontmatter deliberately matches the name in kisa-aciklama.md and is expected to trigger R05.
tools: Read, Grep
model: opus
---

The sole purpose of this file is to prove that R05 (name-collision) fires at
error level.

## Why this defect

The fake root already contains an agent named "kisa-aciklama". This file uses
that name a second time; since two records cannot be invoked under one name, the
scanner must flag the later record as a collision.

## Expected side effect

Because the filename is "ad-cakismasi" while the name field is "kisa-aciklama",
this file also triggers R03 (name-file-match). That is unavoidable: two files in
one directory cannot share a filename, so a name collision can only be
constructed by writing the name field differently from the filename. R03 is
already covered by another file in the fake root, so this side effect does not
distort the test output.
