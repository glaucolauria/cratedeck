# Security Policy

**English** · [Português](SECURITY.pt-BR.md)

cratedeck is an admin UI for CrateDB: whoever runs it gives it access to a
database cluster, usually with administrative privileges. A defect here can
reach that cluster's data and its users, and, through the repository's
automation, the machines of the people who maintain it. This policy says
how to report a vulnerability, what the project treats as
security-relevant, and which protections are and are not in place.

## Supported versions

cratedeck is pre-alpha and has no release yet. Once it has, fixes land on
`dev` and ship in the next release, when `dev` is promoted to `main`; the
supported version is the latest release. There is no backport to older
releases.

## Reporting a vulnerability

**Report privately. Do not open an issue, a pull request or a discussion**
describing an exploitable defect: everything there is public.

Use GitHub's private vulnerability reporting:
[Security → Report a vulnerability](https://github.com/glaucolauria/cratedeck/security/advisories/new).
Only the maintainers see the report. Write in English or Portuguese, and
include what is affected, the cratedeck and CrateDB versions, the steps to
reproduce, and the access an attacker needs. Never test against a cluster
you do not own.

What happens next:

- An acknowledgement within 7 days.
- An assessment, and a plan or a fix, as soon as the severity calls for it.
  The fix goes through a normal pull request that names what it closes
  without the steps to exploit it.
- A published advisory, with credit to the reporter unless they prefer
  otherwise. There is no bug bounty.

## What makes a change security-relevant

Any of these needs a written security note in the pull request (the risk,
what was verified, what was not), a negative-path test where one is
possible, and a review by the `cybersec` agent and a maintainer before
merge:

- Anything under `.github/`: workflows, `dependabot.yml`, `CODEOWNERS`,
  the rulesets. Workflow changes are security changes.
- The agent harness: `.claude/` (settings and hooks), `.agents/`, the
  `Makefile` and `tests/harness/`. They execute on a maintainer's machine
  when a branch is checked out and worked on.
- A dependency added, removed or updated.
- In the app, once it exists: how CrateDB credentials are entered, held,
  sent and forgotten; SQL the app builds itself; how data from the
  database is rendered; any network request; how the app is served and
  configured (headers, CORS guidance, the container image).

## Design rules for the app

They hold from the first line of app code, and a change that breaks one is
a vulnerability, not a feature:

1. **Only the configured cluster.** The browser talks to the CrateDB
   cluster the user configured and to nothing else: no telemetry, no CDN,
   no web font, no update check. Everything the app needs is in its build.
2. **Data is text.** Every value from the database (rows, names,
   messages, error text) is rendered as text, never as HTML.
3. **Identifiers are quoted, values are bound.** The user's own SQL is
   sent as written, by design. SQL the app builds from names it read
   (schemas, tables, columns, users) quotes every identifier and passes
   every value as a parameter.
4. **Credentials stay put.** Never logged, never in a URL, never written
   to storage the user did not choose, never sent anywhere but the
   configured cluster.
5. **Least privilege in the docs.** Setup guidance never recommends a
   wildcard CORS origin together with credentials, nor a superuser where a
   narrower user would do.

## Controls in place

- **Branch rulesets on `dev` and `main`.** A pull request is required and
  the gate (`check`, `pr-title`) must pass, for everyone, the maintainer
  included; force pushes and deletion are blocked. `main` takes only the
  promotion of `dev` (the required `promotion` check, re-run when a pull
  request's base changes), as a merge commit. A code owner's approval is
  required, and only a repository admin may bypass that approval, for a
  pull request only (`docs/repository-settings.md`).
- **Releases are immutable.** `v*` tags cannot be moved or deleted, by
  anyone, and a published release's assets cannot be replaced.
- **Static analysis in the gate.** semgrep with `--error`
  (`p/python`, `p/secrets`, `p/security-audit`, `p/cwe-top-25`,
  `p/owasp-top-ten`, `p/ci`), zizmor over the workflows, and CodeQL
  (default setup) on `dev`, the default branch, and the pull requests into
  it.
- **Workflow supply chain.** Actions pinned by full commit SHA, enforced by
  the repository setting; only GitHub's own actions and an explicit
  allowlist may run; `GITHUB_TOKEN` read-only by default and widened per
  job, with a comment; no workflow uses `pull_request_target`; workflow
  runs from first-time and external contributors wait for a maintainer's
  approval.
- **Secrets.** Secret scanning and push protection are on. No workflow
  holds a secret of the repository's own.
- **Dependencies.** Dependabot alerts and security updates are on; version
  updates come weekly, grouped, with a 7-day cooldown. The dependency
  review in the gate refuses a new dependency, in any scope, with a known
  moderate or worse advisory, or under a license outside its allowlist of
  permissive licenses. The gate's own tools are pinned, with their
  dependencies resolved as of a fixed date at least 7 days old.
- **Every release carries an SBOM** (CycloneDX), attached by
  `create_release.yml`; without a lockfile to build it from, there is no
  release.
- **OpenSSF Scorecard** scores the repository weekly; results are in the
  Security tab.
- **The push guard** (`.claude/hooks/block_protected_push.py`) refuses an
  agent's push to `dev` or `main` before it leaves the machine. A
  convenience: the rulesets are the boundary.

## Accepted vulnerabilities

Known vulnerabilities the project has decided to live with, each until its
review date. Empty is the normal state.

| IDs | Package and version | Why accepted | Review by |
| --- | --- | --- | --- |
| | | | |

## Security exceptions

One row per place a security check is told not to look (a `nosemgrep`, a
zizmor ignore, a control turned off). The reason stays next to the
suppression; this table adds where it was approved and when it is looked at
again.

| Where | Rule | Why | Approved in | Review by |
| --- | --- | --- | --- | --- |
| | | | | |

## Known limits

Stated so nobody assumes a protection that is not there.

- **Secret scanning knows provider tokens only.** Generic patterns
  (passwords, private keys without a known format) and validity checks are
  not available on this plan; semgrep's `p/secrets` and review cover them.
- **One maintainer.** The code-owner review is bypassable by the
  repository admin, for pull requests, so the maintainer can merge their
  own work: for those, the gate and the written security note are the
  review.
- **The push guard is not a boundary.** It does not see git aliases,
  scripts or refs moved through the API (`docs/agent-harness.md`).
- **No signed commits requirement.** Commits are not verified as a rule.
- **Some pins are invisible to automation.** The gate's tools and their
  resolution date (`Makefile`) and uv's version (`check.yml`) move by
  hand; Dependabot does not see them. semgrep's rule packs are fetched
  from its registry on every run, unpinned.
- **The private-name check runs only where the list is.** The list of
  names that must never be published stays off the repository, so CI
  cannot check it: the maintainer's `make ci` before a push is the
  control.

## Out of scope

- The security of CrateDB itself: report it to its project.
- A cluster exposed without authentication, or a cratedeck deployment
  reachable by people who should not administer the cluster: that is the
  operator's configuration, though the docs must not encourage it.
- Compromised GitHub accounts or an already-privileged operator.
