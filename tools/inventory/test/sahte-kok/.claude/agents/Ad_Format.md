---
name: Ad_Format
description: Sample agent definition built to exercise the name-format rule in the fake root; the name field in the frontmatter deliberately contains an uppercase letter and an underscore, matches the filename exactly, and is expected to trigger only R04.
tools: Read, Grep
model: sonnet
---

The sole purpose of this file is to prove that R04 (name-format) fires at error
level.

## Why this defect

The expected format is lowercase letters, digits and hyphens only. The name field
here is written "Ad_Format": it carries both an uppercase letter and an
underscore, so it violates the format rule. The filename is written identically
on purpose, so that R03 (name-file-match) does not also fire and only R04 shows
in the test output.

## The other fields are healthy

Description length, body length and heading count are deliberately kept in the
healthy range, so this file triggers R04 alone and adds no other noise to the
test output. The model and tool fields carry valid values, and there is no
unknown frontmatter field.
