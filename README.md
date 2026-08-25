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
so they are available in every session and every folder. Re-run it whenever one of
these repositories ships something new — it pulls rather than re-clones.

Then simply ask. Each skill's `description` frontmatter is written to match how
the request actually gets phrased, in English or Turkish, so you do not name the
skill and generally should not have to think about which one applies.

**If nothing fires**, that is a defect in the skill rather than in how you
asked. The description was written for the wrong phrasing. Say what you asked
and what you expected, and it gets fixed — that feedback is more valuable than
working around it.

**What is actually built** is listed under Contents below and in the Done
section of [BACKLOG.md](BACKLOG.md). Everything under Queue is planned and does
not exist yet.

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

`examples/` is empty so far.

## Roadmap

See [BACKLOG.md](BACKLOG.md). The first unchecked item is the one being built.

## Contents

| Skill | What it does |
| --- | --- |
| [hafiza-guncelle](skills/hafiza-guncelle) | Write what a session established into persistent memory, and prune what is no longer true. |
| [karpathy-guidelines](skills/karpathy-guidelines) | Behavioural guidelines that reduce the coding mistakes language models reliably make. |
| [new-project-scaffold](skills/new-project-scaffold) | Create a new numbered project in the projects/NNN-name/ layout these repositories share. |
| [proje](skills/proje) | Deliver a multi-step build end to end with a team of specialist agents, from one prompt. |
| [tool-vetting](skills/tool-vetting) | Check a third-party plugin, skill, MCP server or CLI before it is installed: provenance, lookalike repositories, what runs automatically, and whether its value fires where the work actually is. |
| [zero-hallucination-coder](skills/zero-hallucination-coder) | A Discuss to Map to Decompose to Execute to Verify loop that grounds code in verified structure. |

| Agent | What it does |
| --- | --- |
| [dogrulayici](agents/dogrulayici.md) | Reviews finished work adversarially, before it is handed over. |
| [entegrator](agents/entegrator.md) | Merges work packages that ran in parallel into one coherent whole. |
| [mimar](agents/mimar.md) | Turns a request into an implementable plan with parallel work packages. |
| [uygulayici](agents/uygulayici.md) | Delivers one defined work package end to end. |

| Tool | What it does |
| --- | --- |
| [tools/inventory](tools/inventory) | Scans a `.claude/` directory, validates every agent and skill it finds — frontmatter, name collisions, weak descriptions, broken references — and writes a single-file HTML panel. Python 3 standard library, no dependencies, read-only: it reports and never edits. |

These arrived already written and in daily use, rather than being built against the queue below — which is why most carry no item number. Some have Turkish bodies: they were written in the language they are used in, and translating them is a queue item rather than a blocker.

Everything still under Queue in [BACKLOG.md](BACKLOG.md) does not exist
yet.
## Licence

MIT. See [LICENSE](LICENSE).
