# agent-kit

The conventions every other agent repository here follows.

Skills and agents are easy to write and hard to write well. The
common failure is not a bad instruction — it is a skill that never fires because
its description does not match how the work gets asked for, or a skill that
fires constantly because the description is vague, or six skills that should
have been one.

This repository holds the conventions the rest of them follow: what belongs in a
skill and what belongs in a prompt, how to write a description that triggers on
the real request rather than the idealised one, when a job deserves its own
agent, and how to tell whether a skill is actually earning its place.

It is the smallest repository here and the one the others depend on. Changes to
it are changes to every repository that follows it, which is a reason to move
slowly.

## What this is not

It is not a framework and has no runtime. Nothing imports it. It is
a written standard, and the only thing enforcing it is review.

It is not a general guide to prompting. It covers the narrow question of how to
package instructions so they fire at the right moment and hold up when the
person asking is in a hurry.

## How to use this

These are skills for Claude, not a command-line tool. There is nothing to
install and nothing to import — you describe the work and the matching skill
fires on its own.

**In Claude Code or Cowork**, once the skills are on your machine:

```bash
bash ~/Desktop/agent/_setup/sync-skills.sh
```

That clones every agent repository and links its `skills/` into `~/.claude/skills`,
so they are available in every session and every folder. Re-run it whenever the
daily loop ships something new — it pulls rather than re-clones.

Then simply ask. Each skill's `description` frontmatter is written to match how
the request actually gets phrased, in English or Turkish, so you do not name the
skill and generally should not have to think about which one applies.

**If nothing fires**, that is a defect in the skill rather than in how you
asked. The description was written for the wrong phrasing. Say what you asked
and what you expected, and it gets fixed — that feedback is more valuable than
working around it.

**What is actually built** is the Done section of [BACKLOG.md](BACKLOG.md).
Everything under Queue is planned and does not exist yet. The daily loop builds
one item a day; the table above is the intended shape, not the current state.

## Layout

```
agents/
  <name>.md           one specialist, its brief and its boundaries
skills/
  <name>/
    SKILL.md          the instruction, with triggering description frontmatter
    scripts/          only where deterministic code beats instruction
examples/
  <name>/             worked example on real input, with the output committed
```

## Roadmap

See [BACKLOG.md](BACKLOG.md). The first unchecked item is the one being built.

## Planned contents

Nothing here is built yet. This table is the intended shape, and the daily loop
fills it in one item at a time.

| # | Skill | What it does |
| --- | --- | --- |
| 001 | [anatomy-of-a-skill](skills/anatomy-of-a-skill) | What a skill file contains, what belongs in frontmatter versus body, and the difference between an instruction and a description. |
| 002 | [description-that-triggers](skills/description-that-triggers) | How to write the `description` field so the skill fires on the real request. |
| 003 | [skill-or-prompt](skills/skill-or-prompt) | The test for whether something deserves to be a skill at all. |
| 004 | [agent-boundaries](skills/agent-boundaries) | When a job needs its own agent rather than a skill: different judgement, different standard of proof, or a genuinely separate context. |
| 005 | [testing-a-skill](skills/testing-a-skill) | How to check a skill actually works: the trigger test, the cold-start test, and the adversarial test where the request is phrased the way a real person would phrase it at the end of a long day. |
| 006 | [skill-review-checklist](skills/skill-review-checklist) | The review pass to run over any skill before it ships, and the specific things a reviewer misses when the skill reads well. |
| 007 | [house-voice](skills/house-voice) | The written register these repositories hold to, with before-and-after examples. |
| 008 | [versioning-and-deprecation](skills/versioning-and-deprecation) | What happens to a skill that is superseded. |

## Licence

MIT. See [LICENSE](LICENSE).
