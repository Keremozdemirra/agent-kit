---
name: baska-isim
description: Sample agent definition built to exercise the name-file mismatch in the fake root; the name field in the frontmatter is deliberately different from the filename and is expected to trigger only R03.
tools: Read, Grep
model: sonnet
---

The sole purpose of this file is to prove that R03 (name-file-match) fires at
error level.

## Why this defect

The name field in the frontmatter is written "baska-isim", while the filename is
"ad-uyumsuz". The scanner must compare the two values and report the mismatch as
an error finding.

## The other fields are healthy

Description length, body length and heading count are deliberately kept in the
healthy range, so this file triggers R03 alone and adds no other noise to the
test output. The model and tool fields carry valid values, and there is no
unknown field.
