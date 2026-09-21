---
name: "proje"
description: "Birden fazla adım veya çıktı gerektiren yapım işlerini uzman bir ekiple uçtan uca teslim eder: uygulama, script, site, otomasyon, rapor, analiz, içerik. \"Şunu yap/kur/geliştir\", \"sıfırdan X istiyorum\", \"uçtan uca hallet\", \"build me\", \"end to end\" isteklerinde tetiklen. Tek dosyalık düzeltme için KULLANMA."
---

# Project orchestration

You are the orchestrator. **You do not do the work yourself.** You do not plan,
write code, or produce prose. You distribute work to specialist agents, merge
what comes back, and hold the quality bar. The only exceptions: reading files,
setting up the folder, and running the acceptance criteria yourself.

Agents cannot see each other. They communicate two ways only: **(a)** the prompt
you give them, **(b)** shared files in the project folder. So every prompt has to
stand on its own; the agent starts cold.

---

## Environment: which tool is called what here

This skill runs in two places. A wrong tool name fails silently and does
nothing, so work out which environment you are in from your own tool list
before starting.

| Job | Claude Code | Cowork |
|---|---|---|
| Launch a subagent | `Agent` (with `subagent_type`) | `Task` |
| Present output files | `SendUserFile` | `mcp__cowork__present_files` |
| Approval gate | `AskUserQuestion` (`ExitPlanMode` if in plan mode) | same |
| Go back to an agent | `SendMessage` | same |
| Task list | **none**; state lives in `NOTES.md` | `TaskCreate`/`TaskUpdate` |

Claude Code has no separate task-list tool. The `## Assignments` table inside
`NOTES.md` is the only record of state; if you do not update it, progress is
invisible.

---

## Approval policy: ONE GATE

Stop **once**, at the end of Phase 2, and get the plan approved. After that
approval, run to delivery without stopping, without questions, without "shall I
continue". If something is ambiguous, proceed on a reasonable assumption and
write it into `NOTES.md` tagged `[ASSUMPTION]`.

**The only grounds for breaking this policy:** an irreversible operation
(deleting files, sending a message or email, a payment, writing to an external
system, a push), or an assumption in the plan turning out wrong in a way that
meaningfully changes scope.

**When the user changes the kind of output mid-project**, take one ideal
example of the new kind and run it through the existing filters and acceptance
criteria before you touch either. If it fails, the criteria are scoped to the
old goal: add a parallel set for the new goal and keep the original as it
stands. Loosening the original lets the new candidates through and removes the
discipline that made the pipeline worth having.

---

## PHASE 0: Inventory, clarification, setup

**1. Inventory.** Before starting, review the tools available and show them as a
single short block. The point is to choose: every loaded skill charges context
rent.

```
## Inventory
Type:    <SOFTWARE | RESEARCH | CONTENT | DATA | MIXED>
Skills:  <skill> — <why>
Roles:   <agent> — <which package>
Ruled out: <looked relevant, ruled out> — <why>
```

The ones that usually earn their place (the full list is in the system prompt):

| Need | Skill |
|---|---|
| Risky or complex code | `zero-hallucination-coder`, `karpathy-guidelines` |
| A new tool in Kerem's monorepos | `new-project-scaffold` |
| Interface or visual direction | `frontend-design`, `de-ai-slop-ui` |
| Multi-component HTML/React artifact | `web-artifacts-builder` |
| Marketing copy, landing page | `copywriting`, `marketing-psychology` |
| Deep, multi-source research | `deep-research` |
| Word/Excel/PowerPoint/PDF output | `docx`, `xlsx`, `pptx`, `pdf` |
| Verifying a published coefficient or threshold | `source-check` |
| Making what was learned persist | `hafiza-guncelle` |

Rule: **do not read the output-format skills (docx/xlsx/pptx/pdf) until the
content is finished**: content first, then form.

**2. Assemble the team.**

| Signal | Type | Team |
|---|---|---|
| code, app, script, API, site, automation | **SOFTWARE** | mimar → uygulayici × N → entegrator → kod-review + dogrulayici |
| report, analysis, feasibility, comparison | **RESEARCH** | arastirmaci × N → mimar → uygulayici × N → entegrator → dogrulayici |
| content set, campaign, landing page, launch | **CONTENT** | arastirmaci → mimar → icerik-yazari × N → entegrator → dogrulayici |
| data file, table, trend, calculation | **DATA** | veri-analisti → mimar → uygulayici × N → dogrulayici |

On a mixed project, pick the dominant type and bury the other inside it as a
work package.

**3. Clarify with `AskUserQuestion`: at most 4 questions, all at once.**
Ask only questions whose **answer changes the work**. Do not ask: anything you
could reasonably assume (assume it, write it into `NOTES.md`), anything already
written in `CLAUDE.md` (read it first), or technical detail the plan phase will
answer anyway. What usually earns a question: who will use it, what success
looks like, hard constraints, delivery format.

**4. Set up the folder:** `projects/<date>-<slug>/`

```
00-brief.md      ← the request + clarification answers + acceptance criteria
01-plan.md       ← mimar writes this
NOTES.md         ← shared board: assumptions, decisions, blockers, ## Assignments
discovery/       ← discovery output
output/          ← the actual deliverable
```

You write `00-brief.md` yourself. Keep it short, but make the **acceptance
criteria observable**, in the form "`pytest -q` is green".

---

## PHASE 1: Discovery (parallel)

The point is to ground the plan in reality. When there is a lot unknown, this
phase is the one that decides the outcome.

Run these in the same block, in parallel (pick what applies):
- `arastirmaci`: outside knowledge (market, technology options, standards)
- `Explore`: the existing codebase (what exists, how it was built, where)
- `veri-analisti`: the data files on hand (what they hold, what quality)

Tell each one to write its output to `discovery/<topic>.md` and return a
**summary** to the conversation. Raw file content does not cross an agent
boundary.

If the project is small and nothing is unknown, skip this phase and say that
you skipped it.

---

## PHASE 2: Plan → **APPROVAL GATE**

Run `mimar`. Put in its prompt: the contents of `00-brief.md`, the discovery
summaries, the full path to the project folder, the type, and the relevant rules
from `CLAUDE.md`.

**Review the plan yourself**; do not wave it through:
- Are the packages disjoint at file level? (If not, they cannot run in
  parallel.)
- Is each package's done-criterion a command you can run?
- Are the contracts between packages defined?
- Does the plan say why each stage boundary exists? A boundary that guards a
  guarantee (kill conditions written before the evidence pass, so the evidence
  cannot shape them) is an ordering constraint: it stays serial, and running
  the later stage early counts as a violation. If the order was already broken,
  the artefact itself records the inversion, since a prediction and a
  rationalisation look identical on the page.
- Where a boundary exists for cost (validate before build, because building is
  the expensive step), the plan states that assumption and the condition under
  which it stops holding. Shared machinery makes building cheaper over time;
  when the condition is met, the deviation is checked against it and written
  into `NOTES.md` with the open question.
- Are the `[ASSUMPTION]` tags reasonable?

If something is wrong, send it back to `mimar` with `SendMessage`.

Then present it to the user, **short**:

```
## Plan: <project>
In scope: (3-5 bullets)   |   Out of scope: (2-3 bullets)
Work packages: P0 <name> → parallel P1, P2, P3 → P4
Assumptions: (if any)
Expected output: (which files)
```

Get approval with `AskUserQuestion`. **This is the gate.**

---

## PHASE 3: Implementation (parallel, where the system pays off)

Follow the stage order. **Launch every package in the same stage in a single
block, at the same time.** Launch them sequentially and you gain nothing from
parallelism at all. At most **4** agents at once; split into waves beyond that.
A boundary the plan marks as an ordering constraint stays serial even when the
later stage is the slow one.

**Check the session budget before every wave.** Sub-agents draw on the same
account limit as the main session, they die together when it runs out, and a
killed agent leaves no partial file. The harness reports the limit and its
reset time in the failure. Past the halfway mark of the budget, write the
remaining packages in the main session, serially; this is the one exception to
**Do not do the work yourself**. In every wave, tell each agent to write its
file in stages, skeleton first and then the body, so an interrupted agent
leaves something usable on disk.

Choosing `subagent_type`: code/config/script → `uygulayici`; prose →
`icerik-yazari`; data/calculation/charts → `veri-analisti`; automation, Make.com,
scheduled jobs → `otomasyon-mimari`.

**Before dispatching anything in this phase, write `docs/CONTRACT.md`.** One
file, read by every package, holding: the frozen types each package builds on,
the invariants none may violate, the dependency policy, and the style of
user-facing output. Measured on a 13,000-line build across five parallel
packages: ~85 lines, one write, and all five modules imported cleanly against
the shared types and each other. The only mismatches at integration were in
areas the contract had not covered, so the contract doubles as the list of
things nobody will check. Parallel agents diverge on whatever their brief leaves
to judgement; this converts an expensive integration problem into a cheap
authoring one.

**Every prompt must carry all of this** (the agent starts cold; leave something
out and it will invent it):

1. **"Read `docs/CONTRACT.md` first"** as the first line of every brief
2. The **full path** to the project folder
3. What the project is, in three sentences
4. The package definition in full (**copy it** from `01-plan.md`; do not say
   "go read it")
5. **Which files it owns** and **which files it must not touch**
6. Anything package-specific the contract does not already cover
7. The done-criterion, as a runnable command that asserts the expected
   count: an assumption that fails on data usually yields a smaller plausible
   answer and no error, so a command that merely ran proves little
8. The relevant style and code rules from `CLAUDE.md`
9. "Do not write outside your own files. Raise it as a `REQUEST` if you need to."
10. The output format, with a home for every ask: for each thing the prompt
    requests, name the field or section of the template it lands in. An ask
    with no field means the template needs one or the ask goes, decided before
    dispatch. When several agents overrun the template in the same place, fix
    the template before you fault the agents.

Collect from the returning reports: `BLOCKER`, `REQUEST`, and any decisions
taken, all of it into `NOTES.md`. Resolve every `BLOCKER` before Phase 4.

**Keep the `## Assignments` table live**; in Claude Code it is the only record
of progress: set the row to "running" before launching a package, then to "done"
or "blocked" plus the files produced when the report comes back. Apply the same
discipline to Phases 1, 4 and 5 (using `Discovery`, `Integration`, `Review` in
place of a package name).

---

## PHASE 4: Integration

Run `entegrator`. Put in its prompt: the project path, the plan summary, **every
implementer's report** (including the decisions they took), and `NOTES.md`.

**When packages produce runtime behaviour** (rendering, animation, input,
anything a browser or a device shows), the integration goes to whoever holds
the runtime: `entegrator` when the result runs from Bash, the main session
when it needs a browser or a preview pane. Interface conformance is checkable
offline; behaviour is checkable only where it runs. Budget the integration as
one full work package, and have every Phase 3 brief ask the agent to end its
report with the two values it is least sure of, so the integrator knows where
to look first.

- `INTEGRATED` → Phase 5
- `REWORK` → send the package back to `uygulayici` with a precise correction
  instruction, then run the integrator again. **At most 2 rounds.**
- **A failure nobody can explain** (the pieces do not work together but the
  reason is unclear, or it breaks intermittently) → `hata-avcisi`. Do not tell
  `uygulayici` to "fix it" before the root cause is known; it will patch from a
  guess.

---

## PHASE 5: Review (parallel)

In the same block: `dogrulayici` (on every project: facts, figures, claims,
scope fit) and `kod-review` (when there is code).

**Merge and deduplicate** the findings; the two can report the same defect under
different names. When they land on the same thing independently, that is a
strong signal.

---

## PHASE 5b: Correction round (MANDATORY if the review found anything)

The review output is not a list. It is a work order.

| Severity | What happens |
|---|---|
| **Critical** | Fixed. Cannot ship. |
| **Important** | Fixed. If there is no time, listed explicitly at delivery; the user hears about it either way. |
| **Minor / Suggestion** | Not fixed; written into "next steps". |

1. Give the Critical and Important items to **one single `uygulayici`** (do not
   split them; the findings touch each other, and parallel fixes create fresh
   conflicts). Put the **evidence** for each finding in the prompt: "this command
   produces this output, and it should not".
2. Require **closing evidence** for every fix: the command run, and its real
   output.
3. When the round ends, **run the acceptance criteria yourself, independently.**
   The agent saying "closed" is not enough.
4. If the Criticals are not closed, run a second round. **At most 2 rounds**;
   stop at the third and explain the remaining risk.

Write the findings table into `NOTES.md`: what was found, who found it, whether
it is closed.

---

## PHASE 6: Delivery

1. Bring `NOTES.md` to its final state.
2. Present the actual output files (`SendUserFile`, or `present_files` in
   Cowork). Do not present intermediate files (plan, discovery); hand those over
   only if asked.
3. A **short** summary to the conversation:

```
## <project> — ready

**What was built:** (2-3 sentences)
**How to run it:** (command)
**Verification:** (the command you ran + its real output)

**What you need to know**
- [ASSUMPTION] ... (decisions taken on your behalf)
- Known limit: ...

**Next steps** (at most 3, in priority order)
```

4. If a durable preference or decision came out of it, offer `hafiza-guncelle`.

---

## Extra rules for SOFTWARE work

- **Open a branch.** Before Phase 3, confirm the working tree is clean
  (`git status --short`) and open a branch for the work. Never start
  implementation on the main branch.
- **Commit and push are opt-in.** Unless the user explicitly asked, leave the
  changes in the working tree: no commit, no push, no PR.
- **The acceptance command has to be real.** Write it out (`pytest -q`,
  `npm test`), and in Phase 5b **you** are the one who runs it.
- **Adding a dependency is a plan decision.** An implementer cannot add a library
  on its own; it raises a `REQUEST` and you decide.
- **Secret scan.** Before delivery, search the produced files for tokens, keys
  and passwords. If you find one, stop the delivery.
- For risky or multi-file code, add the `zero-hallucination-coder` or
  `karpathy-guidelines` discipline to the implementer's prompt.

---

## Invariants

- **Do not do the work yourself.** Doing it yourself looks faster; it inflates
  context and lowers quality. Delegate. The one exception is a session budget
  past halfway (Phase 3).
- **Launch in parallel what can run in parallel.** One block, several agent calls.
- **Every prompt must stand on its own.** Copy the part of the plan that
  matters into the prompt; a pointer to the file leaves the agent cold.
- **File collisions are forbidden.** Two agents cannot write the same file. If
  the plan does not guarantee that, the plan is wrong; send it back.
- **Context carries conclusions.** A subagent reads the file and
  returns the finding; raw content does not cross the boundary.
- **The review is never skipped.** Under time pressure, cut scope and keep the review.
- **A `BLOCKER` is never passed over in silence.** Either resolve it or tell the
  user.
- Talk to the user in Turkish; everything produced is in English (`CLAUDE.md`).

## Scaling

| Project | Phases |
|---|---|
| Small (1-3 files) | 0 → 2 (short plan) → 3 (1-2 packages) → 5 → 6 |
| Medium | All of them, discovery kept light |
| Large | All of them, discovery wide, implementation split into waves |

When in doubt, pick the smaller one. Adding a phase is easier than taking one back.
