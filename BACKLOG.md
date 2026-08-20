# Backlog

Working queue. The next unchecked item is the one being built. An item stays
unchecked and picks up a `status:` note if it spans more than one working
session — finishing something half-built takes priority over starting the next
one.

Rules of thumb applied to every item:

- one job per skill, done properly, rather than a bundle of half-features
- a skill earns its place only if it beats writing the instruction out by hand;
  if a good prompt does the same job, the skill is overhead
- the `description` frontmatter is the whole trigger mechanism — write it so the
  skill fires on how the work is actually asked for, including in Turkish
- every skill carries a worked example on real input, not a toy
- no claim about a framework, standard, regulation or method without a citation
  and a vintage
- an agent gets its own file only when it needs a different judgement, not a
  different topic

---

## Done

- [x] **hafiza-guncelle** · shipped 2026-08-20. Written before this repository existed and published here as-is; no queue item.
- [x] **karpathy-guidelines** · shipped 2026-08-20. Written before this repository existed and published here as-is; no queue item.
- [x] **new-project-scaffold** · shipped 2026-08-20. Written before this repository existed and published here as-is; no queue item.
- [x] **proje** · shipped 2026-08-20. Written before this repository existed and published here as-is; no queue item.
- [x] **zero-hallucination-coder** · shipped 2026-08-20. Written before this repository existed and published here as-is; no queue item.

## Queue

- [ ] **001 — anatomy-of-a-skill** · What a skill file contains, what belongs in frontmatter versus body, and the difference between an instruction and a description. The reference every other item here points back to.
- [ ] **002 — description-that-triggers** · How to write the `description` field so the skill fires on the real request. Includes the failure catalogue: too narrow, too broad, describes the output rather than the trigger, only matches English when the request comes in Turkish.
- [ ] **003 — skill-or-prompt** · The test for whether something deserves to be a skill at all. A decision procedure, not a list of opinions — most candidates should fail it.
- [ ] **004 — agent-boundaries** · When a job needs its own agent rather than a skill: different judgement, different standard of proof, or a genuinely separate context. Topic alone is never the reason.
- [ ] **005 — testing-a-skill** · How to check a skill actually works: the trigger test, the cold-start test, and the adversarial test where the request is phrased the way a real person would phrase it at the end of a long day.
- [ ] **006 — skill-review-checklist** · The review pass to run over any skill before it ships, and the specific things a reviewer misses when the skill reads well.
- [ ] **007 — house-voice** · The written register these repositories hold to, with before-and-after examples. Plain declarative sentences, British spelling, no marketing adjectives, what a docstring is for.
- [ ] **008 — versioning-and-deprecation** · What happens to a skill that is superseded. Deleting it breaks whoever depended on it; leaving it means two skills compete for the same trigger.
