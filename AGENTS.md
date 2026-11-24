# cratedeck

cratedeck is a modern, self-hosted admin UI for [CrateDB](https://cratedb.com):
a browser application that talks to the CrateDB cluster the user points it
at, to inspect it, query it and administer it (nodes, tables and shards,
users and privileges, snapshots, running jobs). It is an independent
community project, built from scratch, and not affiliated with Crate.io.

The repository is public and open to contributions. Everything in it, and
everything said in its issues and pull requests, is read by strangers:
"Public repository", below, is a hard constraint.

**Shape:** web application. **Stack:** not chosen yet (below).
**Stage model:** two stages, `dev` → `main`. **Status:** pre-alpha, no app code yet.

## Before every task

- Read "Decisions taken", below, before proposing a change of direction.
- Skills load on demand: `.agents/skills/` (Claude Code reads the same
  folder through the `.claude/skills` link). Agents are in
  `.claude/agents/`. `docs/agent-harness.md` says what each tool loads.
- A task that will change the repository starts from an issue
  (`issue-hygiene`) and a branch (`git-workflow`).

## Language

Answer the user in the language they write in, English or Portuguese.
Titles, code, comments, commits, branches and labels are English.

- **Documentation for people** (`README`, `CONTRIBUTING`, `SECURITY`,
  `SUPPORT`, `CODE_OF_CONDUCT`, `docs/`): English and Portuguese, the
  Portuguese in a `.pt-BR.md` twin that links back, changed in the same
  pull request. The English is the reference.
- **Agent instructions** (this file, skills, agents): the English is what
  tools load; each has a Portuguese twin that no tool loads
  (`AGENTS.pt-BR.md`, `<skill>/README.pt-BR.md`,
  `.claude/agents.pt-BR/<name>.md`), changed in the same pull request.
- **Issue and pull request bodies:** a maintainer, or an agent working for
  one, writes the English, then a last section `## Português (pt-BR)` with
  the same content. A contributor may write in either language. A review
  comment from a maintainer: the English, a blank line, `**pt-BR:**` and the
  same in Portuguese.

`tests/harness/test_repository.py` fails when a twin is missing or its
headings differ from the English.

## Public repository (hard constraint)

Files, commits (messages and author e-mails), branches, issues, pull
requests and comments are all public, and stay public once pushed.

1. Never name the maintainers' employers, clients or private projects, nor
   copy anything from them. The list of those names lives on each
   maintainer's machine, never here (`~/.config/cratedeck/private-names`,
   or the file `CRATEDECK_PRIVATE_NAMES` points at); the
   `test_no_private_names_*` tests check the files and the unpushed commits
   against it, and skip without it. Run `make ci` before every push: once
   pushed, it is public. Never read that file into a session.
2. Commit with a GitHub `noreply` address, never a work e-mail:
   `git config user.email <id>+<login>@users.noreply.github.com` in the
   clone. Check it before the first commit.
3. No real data anywhere: no hostname, credential, table or row from a real
   CrateDB cluster in code, tests, fixtures, issues, pull requests or
   screenshots. Synthetic data only.
4. A vulnerability is reported privately (`SECURITY.md`), never in an
   issue, a pull request, a commit message or a discussion.

## Stage flow (hard constraint)

Two stages. `dev`, the default branch, is where every change lands;
`main` receives only the promotion of `dev`. A merge into `dev` releases
nothing; a promotion that bumps the version releases it
(`create_release.yml`).

1. Never push to `dev` or `main`. Pull requests only: the hook in
   `.claude/settings.json` denies the push, and the rulesets refuse it for
   everyone (`docs/repository-settings.md`).
2. Every pull request goes into `dev`. `main` takes one, from `dev`, merged
   as a merge commit; the required `promotion` check fails a pull request
   into `main` from any other head, also after a change of base.
3. Approval before merging, at both stages. Merging is a maintainer's
   action: an agent never merges (`gh pr merge` is denied in
   `.claude/settings.json`).
4. Bump the version in the pull request into `dev` when the change is
   release-relevant; the promotion carries it (`release-management`).
5. Maintainers: task branches from `dev` merge locally into
   `sprint/<topic>`, the gate runs once there, one pull request goes into
   `dev`. Contributors: a branch in their fork, a pull request into `dev`
   (`git-workflow`).

## Stack

Not chosen. The first pull request with app code records it here, with
the reason for each choice, and adds its targets to the `Makefile` and its
ecosystem to `.github/dependabot.yml`. Whatever it is, these already hold
(`SECURITY.md`, "Design rules for the app"):

- The browser talks only to the CrateDB cluster the user configured: no
  telemetry, no CDN, no web font or script from anywhere else.
- Every value from the database is rendered as text, never as HTML.
- Credentials are never written to storage the user did not choose, never
  logged, never put in a URL.

## Layout

```
AGENTS.md              this file; AGENTS.pt-BR.md is the same for people
.agents/skills/        git-workflow, issue-hygiene, release-management, quality-gate
.claude/agents/        pm, qa, cybersec (agents.pt-BR/: the same for people)
.claude/hooks/         block_protected_push.py and its tokenizer, shell_words.py
.claude/settings.json  permissions (allow/deny) and the push guard
.claude/skills         a link to ../.agents/skills
.github/               workflows/, rulesets/ (as applied), issue forms, PR template,
                       CODEOWNERS, dependabot.yml, release.yml
docs/                  repository-settings, agent-harness (each with .pt-BR.md)
tests/harness/         the hook's tests and the repository's structure checks
```

## Rules

1. **A rule lives in one file.** This file holds rules; skills hold
   procedures; `docs/` holds the how and the why. When the code and a
   document disagree, the code wins and the document is fixed in the same
   pull request.
2. **A rule names the test that holds it**, when one does.
3. **Hooks never fail the command they observe**, and need only the system
   `python3` (3.9+) and its standard library. They read the payload's
   `cwd`, not their own working directory.
   `tests/harness/test_block_protected_push.py` covers the guard.
4. **Workflows:** actions pinned by full commit SHA, looked up with
   `gh api` and never typed from memory, the version in a trailing comment;
   least-privilege `permissions:`, documented inline; no
   `pull_request_target`; no `${{ }}` of pull-request data inside `run:`.
   zizmor and semgrep's `p/ci` hold this in the gate, and the repository
   refuses unpinned actions and actions outside its allowlist
   (`docs/repository-settings.md`, "Actions").
5. **Exact tool versions, cooled-down dependencies.** Tools run at the
   versions pinned in the `Makefile`, their own dependencies resolved as of
   its `UV_EXCLUDE_NEWER` date; a dependency release younger than 7 days is
   not adopted (that date, Dependabot's `cooldown`, the app's package
   manager once chosen).
6. **Scope is the issue's.** Work stays inside the acceptance criteria and
   the approach level of its issue (`issue-hygiene`); anything more is
   proposed, not done.
7. **Stage by path.** Never `git add -A`, `git add .` or `git commit -a`;
   name the files, and read `git diff --cached` before committing.
8. **Built from scratch.** No code is copied from other CrateDB admin UIs.
   Reading CrateDB's documentation and system tables is how features are
   designed.

## Decisions taken: do not reopen

Recorded so that no agent spends a session re-arguing them. Changing one is
an issue of its own, opened by a maintainer.

- **From scratch** (2026-11-24): no fork, no code from existing CrateDB
  admin UIs.
- **Apache-2.0**, for the code and for contributions to it
  (`CONTRIBUTING.md`).
- **Two stages, `dev` → `main`** (2026-11-24). Every pull request merges
  as a merge commit, a contributor's included; no squash, no rebase.
- **Dependency updates are automatic**: Dependabot security updates as
  soon as an advisory exists, version updates weekly and grouped, with a
  7-day cooldown. Keeping the project patched is a goal of its own.
- **Bilingual documentation**, English as the reference ("Language").
- **Independent of Crate.io.** "CrateDB" names what cratedeck works with;
  the trademark notice in the README stays.

## Known gaps

What the gate and the settings do not do yet, so nobody assumes they do.

- No app code, so no formatting, linting, type checking or app tests: they
  arrive with the stack.
- CodeQL (default setup) analyses the default branch, `dev`: the workflows
  and the Python hooks. It picks up the app's language once that lands on
  `dev`; confirm it in the Security tab after the first app merge.
- Secret scanning's generic patterns and validity checks are not
  available on this plan: push protection knows provider tokens only, and
  semgrep's `p/secrets` plus review cover the rest.

## Working here

- Branches, commits, pull requests: `git-workflow`. Issues and labels:
  `issue-hygiene`. Versions and releases: `release-management`. The gate:
  `quality-gate`.
- Agents: `pm` orchestrates; `qa` judges whether the tests would catch the
  change being wrong; `cybersec` reviews against `SECURITY.md`.
- A change to `.github/`, `.claude/`, `.agents/`, the `Makefile`,
  `tests/harness/` or a dependency needs a security note in the pull
  request and a `cybersec` review.

## The quality gate

```bash
make check    # a developer's terminal
make ci       # verifying only; what .github/workflows/check.yml runs
```

## CI/CD

- `check.yml`: the gate on pull requests to `dev` and `main`. `gate` runs
  `make ci` on amd64 and arm64 (and the app's build, once it exists);
  `check` adds the dependency review and passes only when every leg did.
  Required.
- `pr-title.yml`: the title is a Conventional Commits title. Required.
- `promotion.yml`: a pull request into `main` comes from this repository's
  `dev`; re-run on every edit, a change of base included. Required on
  `main`.
- `create_release.yml`: on a push to `main`, releases `v<version>` when the
  version is new, with generated notes and an SBOM.
- `scorecard.yml`: OpenSSF Scorecard, weekly and on `dev`; results in the
  Security tab and the README badge.
- CodeQL default setup and Dependabot run from the repository settings
  and `.github/dependabot.yml`.
