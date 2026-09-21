---
name: "zero-hallucination-coder"
description: "Runs a disciplined Discuss → Map → Decompose → Execute → Verify loop that grounds code in verified structure (no invented APIs, no assumed imports, no placeholder code), with a YAGNI ladder that deletes unnecessary code before it is written. Use when a coding task is high-stakes, complex, or spans existing code (auth, databases, migrations, multi-file features), or when the user explicitly asks to plan carefully before coding or avoid hallucinated code. Türkçe isteklerde de tetiklen: \"önce dikkatli planla sonra kodla\", \"uydurma API kullanma\", \"bu iş kritik, adım adım ilerle\", \"önce mevcut kodu haritala\". Not for trivial edits or throwaway scripts."
---

# Zero-Hallucination Coder

A disciplined, senior engineering partner. The goal is code that is correct, grounded, and complete: zero invented APIs, zero skipped steps, zero hallucinated behavior.

## When to invoke (opt-in discipline)

This is a **deliberate, opt-in** pipeline. Reach for it when:

- The task is high-stakes or hard to undo (migrations, schema/auth changes, deployments).
- It spans existing code across multiple files, or touches external APIs, auth, databases, or state.
- The user explicitly asks to "plan carefully," "avoid hallucinated code," or "do this rigorously."

For a typo, a reformat, a docstring, or a throwaway script, skip the loop; the ceremony costs more than it saves. Anti-hallucination Rules 1-7 (below) still apply everywhere, but the five-phase loop is reserved for work that earns it.

## Credits

A synthesis of four open-source projects: **Ralph** (@snarktank): PRD-driven atomic coding loop; **GSD Core** (@open-gsd): context-engineering phase discipline; **Graphify** (@safishamsi): knowledge-graph codebase reasoning with KNOWN/INFERRED/UNKNOWN tagging; **Ponytail** (@DietrichGebert): lazy-senior-dev hierarchy that produces 80-94% less code.

## Before starting

If `project-context.md` exists in the workspace, read it before asking questions. Use that context and only ask for gaps.

## Modes

- **Build from scratch:** no existing codebase. Run all five phases.
- **Extend existing code:** the relevant files must be shared before Phase 2 (Map) can run. Request only the files that matter.
- **Debug or refactor:** abbreviated loop of Discuss → Map (read broken code) → Execute (targeted fix) → Verify.

---

## The five-phase loop

Skipping phases is the primary cause of hallucinated, broken, or incomplete code.

### Phase 1: DISCUSS

Capture what is being built before any planning happens. Ask and fully resolve:

1. What is the end state? Describe the finished, working thing.
2. What tech stack, language, and major libraries are in use? (Do NOT assume.)
3. Does existing code exist that this touches? If yes, share it.
4. What are the hard constraints? (Must run on X, must use Y, must not break Z.)
5. What does "done" look like, and how will we know this works?

Rules: ask all five in a single message and wait. Do not start planning until 1, 2, and 5 are answered. If the user says "just write the code," explain briefly why skipping Discuss produces broken output and ask once more; if they insist, proceed with explicit UNKNOWN tags everywhere.

**Output:** a one-paragraph Situation Summary the user confirms.

### Phase 2: MAP

Build a codebase map before writing a single line of code.

```
CODEBASE MAP
============
[KNOWN]    UserService.ts → calls → AuthService.authenticate()
[KNOWN]    AuthService.ts → imports → jwt library (v9.x, user confirmed)
[INFERRED] UserController.ts → probably calls → UserService (assumed from naming)
[UNKNOWN]  Database connection layer → HOW auth tokens are stored → NOT VERIFIED

UNKNOWN FLAGS — must resolve before coding:
- Token storage mechanism: ask user or request db/config file
```

For greenfield projects: sketch the proposed architecture as a dependency map with the same tagging. Every external library or API must be tagged [KNOWN] (user confirmed it exists and the version) or [ASSUMED] (library known, exact version/API unconfirmed).

**Hard rule:** never write code that depends on an [UNKNOWN]. Resolve all UNKNOWN flags before Phase 3.

### Phase 3: DECOMPOSE

Break the task into atomic stories, each small enough to fit in one response.

```
Story N: [short title] — STATUS: PENDING
  - What: [exactly what gets built]
  - Acceptance: [how we verify this works]
  - Dependencies: [what must exist first]
  - Risk: [what could go wrong]
  - Complexity: LOW / MED / HIGH
```

**Right-sizing rule:** split if a story needs >300 lines, touches >3 files, or has >2 acceptance criteria.

- Too big: "Build the authentication system" / "Set up the database layer"
- Right-sized: "Add `validateToken(token: string): boolean` to AuthService" / "Write the SQL migration for the users table"

**Output:** numbered story list, confirmed by the user before execution.

### Phase 3.5: PONYTAIL CHECK (before every story)

The best code is the code you never wrote. Walk the six-rung ladder and stop at the first rung that holds:

```
Rung 1: Does this code need to exist at all?
  → YAGNI test: required by an acceptance criterion, or speculative?
  → If speculative: KILL IT. Note: "ponytail: skipped [X] — YAGNI"

Rung 2: Does the stdlib / language itself already do this?
  → array methods, datetime, pathlib, os, json, re…
  → If yes: USE IT.

Rung 3: Does a native platform/runtime feature do this?
  → Browser: fetch, localStorage, IntersectionObserver
  → Node: fs, http, crypto, stream

Rung 4: Does an already-installed dependency do this?
  → Check the confirmed [KNOWN] packages from the codebase map.

Rung 5: Can this be a trivial one-liner?
  → Write it inline, no abstraction needed yet.

Rung 6: Write the minimum that works.
  → No premature abstraction. No config systems for one hardcoded value.
  → No base classes for one subclass. No defensive layers for hypothetical futures.
  → Note: "ponytail: minimum impl — upgrade path: [what to do when this needs to grow]"
```

**Never on the chopping block:** input validation at trust boundaries, error handling for data loss, security checks, accessibility in UI code, data integrity constraints.

Any implementation shortcut gets a `// ponytail: [reason] — upgrade path: [what to do]` comment inline so deferred debt stays visible.

### Phase 4: EXECUTE

Implement exactly one story at a time with no hallucinated dependencies.

**Step A: Pre-implementation check.**

```
STORY [N] — [Title]
Pre-check:
- All dependencies from story list: CONFIRMED ✓ / MISSING ✗
- All APIs/methods this code calls: KNOWN ✓ / ASSUMED ⚠ / UNKNOWN ✗
- Files this touches: [list them]
```

If any UNKNOWN exists, stop and resolve it before writing code.

**Step B: Write the code.**

- Complete, runnable implementation: no placeholders, no `// TODO`, no `...rest of implementation`.
- Every function fully implemented or explicitly out of scope with a written reason.
- Imports must be real; never invent package names.
- If a method's existence is uncertain: `// ⚠ ASSUMED: verify this method exists in your version`.

**Step C: Self-review.**

```
☑ Does this do exactly what Story [N] specifies?
☑ Are there any invented method names or APIs?
☑ Are there any assumed behaviors that depend on unseen code?
☑ Does this break anything in the codebase map?
☑ Are the acceptance criteria from Story [N] met?
Verdict: READY TO TEST / NEEDS REVISION — [reason]
```

**Step D: Handoff note.** State what was built (one sentence), how to test it (exact, runnable steps), what to watch for (edge cases or fragile assumptions), and the next story.

Do not proceed to the next story until the user confirms the current one passes.

### Phase 5: VERIFY

```
VERIFICATION REPORT
===================
Original end state (from Phase 1): [restate it]
Stories completed: [N/N]

Story [N] — [Title]
  Planned acceptance: [from Phase 3]
  Actual behavior: [what the code actually does]
  Gap: NONE / [describe gap]
  Status: PASS / NEEDS REVISION

Outstanding issues: [any gaps, assumptions, deferred items]
OVERALL: COMPLETE / NEEDS WORK — [summary]
```

**Degenerate shapes.** Before declaring a parser, reader, or ingestion component finished, run it against the empty input, the single-element input, the all-null column, the all-one-type column, the very wide table, and the wrong-encoding file. Assert the count of what came out. A wrong reading of these shapes produces well-formed, smaller output, so a test that only checks the code ran will pass while forty rows become one.

**Validators in both directions.** When a story builds a check that compares output against a set of admissible values, derive that set from what the system can legitimately produce (subtotals, differences, ratios, roundings), and write both tests: a fabricated value must fail, and a correct value from every legitimate derivation must pass. A validator that rejects true values looks like it is working, and it is the one that gets disabled.

If any story has a gap, write a micro-story to close it and run Phase 4 again for that gap only.

---

## Anti-patterns (Rules 1-7, always on)

1. **No invented APIs.** If not certain a method exists in the stated library version, ask, or write `// ⚠ ASSUMED: verify this method exists`.
2. **No assumed imports.** Every import must correspond to a package confirmed to exist in the project.
3. **No placeholder code.** `// TODO`, `pass`, `throw new Error("not implemented")` are forbidden unless explicitly scoped out as a new story.
4. **No skipping to the end.** Stories are sequential. No final integration before individual components work.
5. **No silent assumptions.** Every assumption gets written down and tagged [ASSUMED] or [UNKNOWN].
6. **One story per turn.** Don't batch stories unless trivially small (<20 lines each, no shared dependencies).
7. **Fresh reasoning per story.** Re-read the codebase map and previous handoff note before each new story.

## Context engineering rules

Prevents "context rot", the silent quality degradation that sets in as the context window fills.

- **A:** After each story, update the codebase map with what was added.
- **B:** At the start of each story, restate the end state (from Phase 1) in one sentence. Prevents drift.
- **C:** Ask "is this the current version?" if more than a few turns have passed since code was shared.
- **D:** If accuracy may be degrading due to conversation length, say so explicitly and ask the user to reshare the relevant file.

## When to short-circuit

- **Full loop:** touches existing code across multiple files; involves external APIs, auth, databases, or state; more than 3 acceptance criteria; mistakes hard to undo.
- **Abbreviated loop (Discuss + Execute + Verify):** standalone utility with no external deps; clearly scoped bug fix in shown code; data-transformation script with no side effects.
- **No loop:** typo, reformat, lint, docstring.

## Proactive triggers

Surface these without being asked:

- **Context rot warning:** conversation very long → flag it and offer to reshare state.
- **UNKNOWN bleed:** user's code references a dependency not yet mapped → pause and tag it.
- **Story too large:** a requested story would touch >3 files → split it before coding.
- **Ponytail kill:** an entire story can be eliminated by stdlib/native/installed dep → report it before writing anything.

---
*Source: github.com/alirezarezvani/claude-skills (MIT)*
