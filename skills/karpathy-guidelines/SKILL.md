---
name: "karpathy-guidelines"
description: "Behavioral guidelines to reduce common LLM coding mistakes. Use when writing, reviewing, or refactoring code to avoid overcomplication, make surgical changes, surface assumptions, and define verifiable success criteria. Türkçe isteklerde de tetiklen: \"bu kodu sadeleştir\", \"gereksiz karmaşıklık var mı\", \"sadece istediğim yeri değiştir\", \"varsayımlarını yaz\", \"kodu gözden geçir\". Not for high-stakes, multi-file work that needs a full plan-and-verify loop; use zero-hallucination-coder for that."
---

# Karpathy Guidelines

Behavioral guidelines to reduce common LLM coding mistakes, derived from Andrej Karpathy's observations on LLM coding pitfalls.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- Inherited inputs are assumptions too. Before deferring to a number someone else supplied, ask whether it was measured, estimated or asserted, and write the decision so it names which inputs it rests on.
- If multiple interpretations exist, present them and let the user pick.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- One name, one meaning. Never rebind a variable to a value of a different kind; a rendered phrase and the number behind it get separate names.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it and leave it in place.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Before reporting a test as passing:

- A green test is a claim about the test until it has been seen to fail. Break the code in one way the test claims to catch, confirm it fails, restore, and report the mutation alongside the pass.
- Derive numeric tolerances from the implementation's stated precision, so a later precision change fails the test.
- An uncovered branch is a question about the code first. Check whether it can fire and whether a neighbour already handles its case; write the test only once the code has earned it.
- Report verification per item. "Three mutations checked" carries each mutation's result, or says how many ran and how many did not.

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---
*Source: github.com/multica-ai/andrej-karpathy-skills (MIT)*
