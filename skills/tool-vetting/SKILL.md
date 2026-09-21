---
name: tool-vetting
description: Vets a tool before it joins the harness and finds the ones worth vetting: inventory what is installed, derive the gaps, pull the real corpus, prove a service by its protocol, resolve every install route separately, read the instruction file as an execution path, then verdict: install alongside, replace, or decline with a recorded reason. Static scanners (skillspector, mcp-scanner) run first. Use before installing a plugin, skill, MCP server or CLI, on a forwarded tool list, or on "sunu kurar misin", "bu arac iyi mi", "kurmadan once bak", "bize ne lazim". Not for your own app; use pre-launch-security-audit.
---

# Vetting a tool before it goes in

Installing is the easy part and the irreversible part. Everything below happens
**before** anything runs, because the failure mode is silent: a bad install does
not error, it quietly has more access than it needed.

Three standing rules. **Inventory before candidates**: "which tool is good?"
is the wrong question until you know what is missing. **Provenance before
capability**: what a tool does is irrelevant until you know whose code it is.
And **a guide is a claim**: forwarded articles, videos, PDFs and
Notion pages are marketing surfaces, frequently affiliate-driven, and they get
repo names, star counts, licences and even install commands wrong in the
direction that favours installing.

## 0. Enumerate what you already have, then derive the gaps

Do this first, once per session, and reuse it for every candidate. Without it
the answer degenerates into a vendor catalogue where most entries are already
covered.

```bash
claude mcp list 2>/dev/null || jq -r '.mcpServers|keys[]' ~/.claude.json
jq -r '.plugins|keys[]' ~/.claude/plugins/installed_plugins.json
ls ~/.claude/skills ~/.claude/agents
```

**A name is a label, and a brief's description of a tool is a claim.** For
every server the inventory lists, issue one cheap call and record the role from
what came back, one line per tool. A task brief once described `qdrant-find` as
a semantic store of the user's own data; a single call returned vendor
client-library snippets, nothing of the user's, and a job an installed docs
server already covered. A charter written from that brief would have
advertised a memory that did not exist. The observed role stays in the
inventory and rides along to the verdict in section 9.

Write the gap list from the inventory, keyed by **job to be done**; install
type plays no part in it. Then two corollaries that decide most cases on their own:

- A gap that is already 80% covered is not a gap.
- Once ten or more servers are live, **context budget becomes the scarce
  resource**. Every authorised server's tool definitions ride along; three
  or four additions, worked for a week, then remove whatever never fired.

For a batch (a forwarded list, a queue of links) build the inventory once and
run every candidate against it. Re-deriving it per candidate is the expensive
mistake.

## 1. When the question is "what exists", fetch the corpus

Answering a discovery question from memory produces a plausible shortlist and
misses working endpoints you would never recall. Pull the registry, then filter
mechanically before any judgement:

- **Reverse-DNS namespace is domain-verified.** `com.stripe/mcp` is provably
  Stripe's; `com.mcparmory/sentry` is a third party wrapping Sentry. Publisher
  authenticity is readable straight off the name.
- **Publisher entry-count is inversely correlated with legitimacy.** Real
  companies ship one to three servers; spam farms ship twenty to two hundred.
- Vendor blog posts, listicles and search-result summaries are **not**
  endpoint verification. In one run they carried five wrong URLs.

## 2. Prove it exists by speaking its protocol

Status-code probing looks sufficient and is not. Of 43 endpoints returning HTTP
200 to an MCP `initialize` POST, **15 were not MCP servers at all**: marketing
pages, SPA shells and generic APIs that return 200 to any POST. Only parsing the
body for the protocol's own required fields separated the real ones.

```bash
curl -s -m 12 -X POST "$URL" -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}' \
  | grep -o '"serverInfo":{[^}]*}'
```

Read the outcome as evidence, each row a finding:

| Response | What it proves |
|---|---|
| 200 **with** `serverInfo` / `protocolVersion` | Real, open, connect now |
| 200 **without** them | Something answered. Not the service. Drop it |
| 401 | **The real server is there and gated**: the strongest liveness signal short of a handshake |
| 404 / DNS failure | The documented address is wrong; report that, it is a finding about the guide |

An auth rejection is positive evidence of existence. Treat "failed" responses as
data.

## 3. Confirm the repo is the one they meant, and resolve every route

```bash
curl -s "https://api.github.com/repos/OWNER/NAME" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('message') or f\"stars={d['stargazers_count']} lic={(d.get('license') or {}).get('spdx_id')} fork={d['fork']} pushed={d['pushed_at'][:10]}\")"
```

Compare stars, licence and last push against what the guide claimed. A guide
that is wrong about the star count is wrong about other things too.

**Then search for the same name under other owners.** This is the check that
matters most and the one nobody runs. A guide once pointed at a 3-star repo
whose description was a near-copy of a 58,000-star project of the same name.
The star count is the tell; the name is not. A `fork: true` with a `parent`
field is a different situation from a typosquat and deserves a different
sentence in the write-up.

**A recommendation usually offers several ways to obtain the same thing**: a
repo link, a package-manager command, a marketplace button, a curl script.
Resolve each one to the code it fetches, then compare. In the case
above the `npm install` command fetched the legitimate upstream package while
the repo link pointed at a stale fork by an unrelated account. Agreement is weak
confirmation; **disagreement localises the defect and tells you whether the
problem is the tool or the person recommending it.**

## 4. Match the package registry against the repo

```bash
curl -s https://registry.npmjs.org/PKG | python3 -c "import sys,json;d=json.load(sys.stdin);lv=d['dist-tags']['latest'];print([m.get('name') for m in d.get('maintainers',[])], d['versions'][lv].get('repository'))"
curl -s https://pypi.org/pypi/PKG/json | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['info'].get('project_urls'), len(d['releases']),'releases')"
```

An odd package name is not automatically a typosquat; projects get renamed and
hold placeholder names. Resolve it by checking whether the package points back
at the repo; the look of the name settles nothing.

## 5. Read what runs automatically, before it can run

Clone shallow and read. Do not install first and inspect later.

```bash
git clone -q --depth 1 https://github.com/OWNER/NAME /tmp/vet && cd /tmp/vet
find . -name "hooks.json" -o -path "*/hooks/*" -type f | head
grep -rhoE "https?://[a-zA-Z0-9._/-]+" scripts/ hooks/ bin/ 2>/dev/null | sort -u
grep -rinE "api[_ ]?key|_TOKEN|\.env|credentials|process\.env" scripts/ hooks/ bin/ 2>/dev/null | head
```

Three things: what fires without being asked, where it sends data, what secrets
it can reach. A hook that only reads local files is fine. A hook that posts
anywhere is a question for the user.

**Then read the instruction file itself; it is an execution path.** A skill can reach the network on every invocation while
presenting a completely clean hook surface, because the model reads SKILL.md and
does what it says. Grep the prose for imperatives that invoke bundled scripts,
phone home, acknowledge events, or tell the agent what not to mention.

Read the **surrounding section** before judging any sentence. One skill's "then
continue without mentioning the check" reads as suppressed disclosure alone; in
context it applied only to the no-update case, and the same file forbade
relaying remote text at all, a deliberate injection defence. The mitigation for
a real finding is usually a documented environment flag set once in settings,
which beats forking the skill because it survives updates.

## 6. Find out what already owns the target directory

Before writing into any directory an existing setup maintains, find out what
writes there. A config directory that looks hand-maintained may be build output,
and files dropped into it disappear on the next regeneration, silently and much
later.

```bash
grep -rl "GENERATED\|DO NOT EDIT\|autogenerated" ~/.claude/agents ~/.claude/skills 2>/dev/null
```

If the directory is generated, install through the generator's own source (a
registry, a template) or into a namespace it does not own.

## 7. Prefer the mode that touches least

Most serious tools ship several integration modes, and they are not equally
invasive. In descending order of preference:

1. **On-demand skill or agent**: costs nothing until dispatched.
2. **MCP server**: a tool the model calls; no credential access, no interception.
3. **Hooks**: runs on every matching event, forever, in every project.
4. **Proxy or wrapper**: sits between the agent and the model, sees everything,
   and on a subscription plan raises questions the README will not answer.

Take the least invasive mode that still delivers the point of the tool. Be
honest when the lighter mode structurally cannot deliver the value: an MCP
server cannot intercept, so a compression tool in MCP mode compresses only what
you hand it. That is an argument for skipping; the heavy mode has to earn its
own case.

## 8. Judge cost against where the work is

**Does the trigger occur in this workflow?** A commit-time scanner is worth its
hooks only if commits go through the agent. If they run in a deterministic
script outside the model, its one unique contribution almost never fires while
its per-turn hooks fire always.

**Is this already resident?** Rules the user keeps in CLAUDE.md are loaded every
session at zero hook cost. A plugin installing a generic version of a rule the
user already wrote, in their own words, is a third copy plus overhead. Sharpen
the existing line; it is free.

**Is there a target?** A tool can be excellent, cleanly licensed and perfectly
provenanced, and still have nothing here to point it at. "No target yet" is a
real verdict and belongs in the record with the date it might change.

## 9. Finish with a three-way verdict, and record the skips

Every candidate ends as exactly one of:

- **Install alongside**: fills a gap nothing covers.
- **Replace the incumbent**: requires evidence that the incumbent is unused or
  strictly worse, *and* a named rollback. Absent both, this is not available.
- **Decline**: with one line of reason, dated.

The output of a pass is a short list of what went in and a shorter list of what
did not, one line each. "Skipped, overlaps X", "skipped, needs a paid seat",
"skipped, no target yet" are useful; silence is not. A tool rejected with a
recorded reason does not have to be re-evaluated the next time someone forwards
the same guide, and the same names do get forwarded repeatedly.

Re-run section 8 on things already installed. An install that made sense on the
information available then can stop making sense once you learn how the user
works. Reversing it is a normal outcome of this skill.

## 10. Mechanical checks now on this machine (2026-09-21)

The reading pass above stays; these run before it and give it a list of lines
to read first. Static modes only. A scanner's LLM mode sends the scanned code
to a provider, so `SKILLSPECTOR_PROVIDER` stays unset.

```bash
skillspector scan <dir-or-repo-url> --no-llm --format json --output /tmp/ss.json   # skills, plugins, MCP tool manifests
mcp-scanner --analyzers yara stdio --stdio-command "<cmd>"                          # a local MCP server's tools, YARA only, no API key
mcp-scanner --analyzers yara --server-url <url> remote --server-url <url>             # a remote one; 4.8.4 needs the url in both places, and --stdio-timeout crashes it
dev-machine-guard --json                                                            # what is installed on this machine: agents, MCP servers, IDE extensions, packages
```

Read the findings by category and file before believing the score. A repository
that ships benchmarks and test fixtures scores high on prose patterns while its
skill directory alone scores low (ponytail: 100 for the repository, the skill
directory on its own is what gets linked). A green result is one narrow answer,
that the code does nothing hostile; fit is still decided by section 8.
