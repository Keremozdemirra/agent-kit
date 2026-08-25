---
name: kirik-ref
description: Sample agent definition built to exercise broken-reference detection in the fake root; the body cites a non-existent agent name inside backticks and is expected to trigger only R08.
tools: Read, Grep
model: opus
---

The sole purpose of this file is to prove that R08 (broken-reference) fires at
warning level.

## The deliberate broken reference

This job should first call an agent that does not exist: `olmayan-agent`. No such
agent is defined in the fake root or in the real one. Because the word agent
appears on this line, the scanner must capture the backticked token as a
candidate reference, and finding no such name among the records, produce a
finding at warning level.

## The other fields are healthy

Description length, body length and heading count are deliberately kept in the
healthy range, so this file triggers R08 alone.
