This file deliberately has no frontmatter block; it opens with plain prose.

The purpose is to prove that the scanner marks the frontmatter_var field false
and that dogrula.py produces R01 (frontmatter-present) at error level. Unlike the
other four files in the fake root, this one has no frontmatter field at all, so
its name and description fields stay empty and it also triggers R02
(required-field) — an expected and acceptable side effect, since a file with no
frontmatter cannot have a name or a description either.

This paragraph exists only to bring the body up to a reasonable length, so that
R07 (body-empty) produces neither an unnecessary error nor a warning for this
file and the test output stays cleanly readable on R01. Every file in the fake
root targets exactly one rule in the P3 test pack; this one targets the complete
absence of frontmatter.
