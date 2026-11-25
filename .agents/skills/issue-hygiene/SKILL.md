---
name: issue-hygiene
description: Use at the start of a task or request that will become code in cratedeck, to propose the issue through a short form and open it only on the user's answer; and when creating, refining, labelling or triaging issues and pull requests. Holds the intake form, the approach levels that bound how much the agent designs, the body format, the labels and the commands.
---

# Issue hygiene

Issues are public: what `AGENTS.md`, "Public repository", says about names,
data and vulnerabilities applies to every word of them.

## The intake: propose, then open

At the start of a task or a request that will become code, **propose the
issue; open it only on the user's answer**. Skip this for a question, a
review, or a request that already names its issue.

First, look for one that exists:

```bash
gh issue list --state open --search "<keywords>" --limit 10
```

Then ask, with the tool's multiple-choice form when it has one (otherwise a
numbered list), the recommended answer first in every question:

**Form 1. Create the issue?**
- Create "<conventional title, English>" (recommended).
- Use #n "<title>", when the search found one.
- Don't create: the work goes on without an issue.
- Other: a title of their own.

**Form 2. Properties**
- **Labels:** the type (`enhancement`, `bug`, `chore`, `documentation`),
  plus `security`, `breaking-change`, `good first issue` or `help wanted`
  when they apply.
- **Assignee:** the user (`@me`), or nobody when it is meant for a
  contributor.
- **Milestone:** an open one, or none (`gh api repos/:owner/:repo/milestones`).

**Form 3. Approach**
- "Follow the repository's pattern" (first and recommended when the code
  already does something similar), then Low, Medium, High (below).
- **Your suggestion:** none, or the approach the user proposes, in free
  text. It goes into the body, and the agent follows it.

Then write the body and open it:

```bash
gh issue create --title "<title>" --body-file <file> \
  --label <type> [--label …] [--assignee @me] [--milestone "<name>"]
```

## The approach: how much to design before coding

The level decides how much the agent invests in thinking the solution
through. **Tests are not part of it: every level is fully tested.**

| Approach | Fallbacks | Code complexity | Patterns from outside |
| --- | --- | --- | --- |
| **Follow the repository's pattern** | those the code already has | that of the code around it | none |
| **Low** | none beyond the acceptance criteria | the least that meets them | none |
| **Medium** | the likely failures (network, an unreachable node, a timeout, an empty result) | a local module or abstraction is fine | only those the repository already uses |
| **High** | the likely and the rare, naming any left out | what the design needs | research what comparable tools do, compare two or three options, propose the design in the issue before coding |

- **When the work outgrows the level**, stop and ask ("this needs a retry
  for X, which Low leaves out: move to Medium, or leave X out?"). Never
  grow the solution on your own.
- **The pull request states the issue's approach**, and why the work went
  past it when it did.

## The body: short

The pull request carries the detail; the issue says what and how to tell
it is done.

1. The outcome, in one or two sentences, and who it is for.
2. The acceptance criteria as a checklist.
3. One line: `Approach: <level>`, plus `Suggested: <text>` when the user
   wrote one.
4. For a bug: the CrateDB and cratedeck versions, the steps, what happened,
   what was expected. Reduced to synthetic data.
5. `## Português (pt-BR)` with all of the above, when a maintainer or an
   agent working for one opens it (`AGENTS.md`, "Language").

A comment is rare: one line, when something the issue cannot show changes
(a blocker, a change of scope). A maintainer's: the English, a blank line,
`**pt-BR:**` and the same in Portuguese.

## Labels

| Label | For |
| --- | --- |
| `bug`, `enhancement`, `chore`, `documentation` | the type: every issue and pull request has one |
| `security` | a fix or a hardening; never the details of an open vulnerability |
| `breaking-change` | breaks a user flow, a setting, or drops a CrateDB version |
| `dependencies`, `github_actions` | dependency and workflow updates (Dependabot applies them) |
| `triage` | set by the issue forms; removed once a maintainer has looked |
| `good first issue`, `help wanted` | open to contributors: small, well-defined, with acceptance criteria |
| `question`, `duplicate`, `invalid`, `wontfix` | closing reasons, or a pointer to Discussions |

**Label the pull request too**: `.github/release.yml` builds the release
notes from pull request labels, and an unlabelled one lands in "Other
Changes".

## Triage (maintainers)

For each issue with `triage`:

1. Reproducible, in scope, and not a vulnerability? A vulnerability
   reported in public: thank the reporter, ask them to use the private
   report (`SECURITY.md`), and hide the details (edit, or delete the
   comment).
2. Set the type label, remove `triage`; add `good first issue` or
   `help wanted` when a contributor could take it.
3. A question or an open-ended idea: point it to Discussions and close it
   as `question`.

## Sizing

One issue, one verifiable increment. Split what does not fit a focused
cycle. An umbrella issue only points at its sub-issues.

## Commands

```bash
gh issue view <n> --json title,labels,assignees,milestone,state
gh issue edit <n> --add-label <label> --remove-label triage
gh issue edit <n> --add-assignee @me
gh pr view <n> --json closingIssuesReferences --jq '[.closingIssuesReferences[].number]'
```

Verify the end state, not exit codes.
