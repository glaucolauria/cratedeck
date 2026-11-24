---
name: git-workflow
description: Use whenever starting the development of a task in cratedeck, creating branches, commits or pull requests, or handing finished work back. Branch names, commit format, the sprint branch, the hand-back report and the next-step question before a pull request, the promotion of dev to main, and what a merge into each stage does.
---

# Git workflow

The rules are in `AGENTS.md` ("Public repository", "Stage flow"); this is
the procedure. Do not infer process from branch names already in history.

## The stage model

Two stages. `dev`, the default branch, receives every pull request;
`main` receives only the promotion of `dev`, and a promotion that bumps the
version releases it (`release-management`).

**Never push to `dev` or `main`.** The hook in `.claude/settings.json`
denies a push whose destination is `dev`, `main` or `master`; the rulesets
refuse it for everyone, the maintainer included.

## Before the first commit in a clone

```bash
git config user.email    # must be <id>+<login>@users.noreply.github.com
```

If it prints a work or personal address, stop and ask the user to set the
`noreply` one in this clone (`AGENTS.md`, "Public repository"). A commit's
e-mail is public the moment it is pushed.

Before every push, `make ci` with the maintainer's private-names list in
place: it checks the unpushed commits and the files for names that must
never be published. If the two `test_no_private_names_*` tests were
skipped, say so and ask before pushing.

## Branches

```
feat/<issue>-<slug>      fix/<issue>-<slug>      chore/<issue>-<slug>
refactor/<issue>-<slug>  docs/<issue>-<slug>     ci/<issue>-<slug>
sprint/<topic>           a maintainer's integration branch for several task branches
```

- **A maintainer** branches from `dev`. Task branches are merged into
  `sprint/<topic>` **locally** (a local merge runs no CI); `make ci` runs
  once there; `qa` and `cybersec` review the consolidated diff; one pull
  request goes into `dev`. A single task may go straight from its task
  branch to a pull request.
- **A contributor** works on a branch of their fork, from `dev`, and opens
  the pull request from it into `dev`.

Per task branch, run only what is fast and relevant; the full gate runs
once, on the branch that becomes the pull request. A branch dies with its
pull request (`delete_branch_on_merge`).

## Commits

Conventional Commits, English, imperative:

```
feat(console): add query history
fix(tables): quote schema names with dots
ci(actions): pin dependency-review-action by sha
```

Types: `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `ci`, `build`,
`perf`, `revert`. The body says *why*; the diff already says what. A change
and the test that proves it are one commit.

- **Stage by path** (`AGENTS.md`, rule 7): `git add <files>`, then read
  `git diff --cached`. `git commit -m` commits everything staged, including
  what an earlier step left there.
- **The agent commits on task and sprint branches**; it pushes and opens a
  pull request only when the user asks (step 4 below).
- **AI attribution.** A commit an agent wrote, or helped write, ends with
  the `Co-Authored-By:` trailer of its tool and model. If the tool did not
  add it (`git log -1 --format=%B`) and the commit is not pushed, amend
  with `--trailer "Co-Authored-By: <tool> <model> <vendor noreply>"`. Once
  pushed, never rewrite history for it.

## From task to pull request

### 1. Before coding

Read the issue's acceptance criteria and approach (`issue-hygiene`). Say in
one line what will be run to see the change working (the app against a
local CrateDB container, once there is an app), or that there is nothing
to run (documentation, tooling).

### 2. Develop

Small commits on the task branch. The full gate (`quality-gate`) once on
the branch that becomes the pull request, then `qa` and `cybersec` on the
consolidated diff.

### 3. The hand-back

When the work is done and the gate is green, and before any pull request,
report in the chat, in the user's language, in this order:

1. **See it running.** A link or the command for each screen or behaviour
   the change touches. When there is nothing to open, say so.
2. **What was done.** Three to six bullets.
3. **Tests.** What ran and the result; the tests added or changed; the
   changed lines left uncovered, and why.
4. **Security.** Each `cybersec` finding and what happened to it: fixed,
   accepted with the reason, or filed. Without findings, say so; without a
   security-relevant path touched (`SECURITY.md`), say that instead.
5. **Your part.** A checklist of what only the user can do: look at a
   screen, change a setting, approve, merge.

### 4. The next step: ask

With the tool's multiple-choice form when it has one, otherwise a
numbered list, the recommended answer first:

- Push and open the pull request (recommended when the gate is green and
  nothing in "Your part" blocks it).
- Push and open it as a draft, when something in "Your part" comes first.
- Review locally first. The agent waits.
- Other: what to change.

### 5. After the pull request

Send the links: the pull request and the issue. Then check the end state,
not exit codes: `gh pr view <n> --json closingIssuesReferences,labels,assignees`.

## Pull requests

- **Title** in Conventional Commits form, English: it is the line in the
  release notes and, on a squash merge, the commit on `dev`. The
  `pr-title` check enforces it.
- **Closing issues:** one closing word per issue, `Closes #12, closes #15`;
  confirm with `closingIssuesReferences` after opening.
- **Body:** the template's sections; a maintainer's (or their agent's)
  body ends with the complete `## Português (pt-BR)` section
  (`AGENTS.md`, "Language"). Short: ~15–25 lines per language for a task,
  ~30–40 for a sprint (naming every issue it closes). Never empty, never
  the title restated.
- **Security impact:** one line, even "none". A change to a path
  `SECURITY.md` lists carries a written note and a `cybersec` review.
- **Version:** decided and, when release-relevant, bumped in the branch
  (`release-management`).
- **Label** the pull request (`bug`, `enhancement`, `chore`, `security`,
  `documentation`, `dependencies`, `github_actions`, plus
  `breaking-change`): the release notes are built from it.
- `gh pr create --base dev --assignee "@me" --label <type> --title … --body-file …`.

## Promoting dev to main

Only when the maintainer asks for it: one pull request from `dev` into
`main`, with the same hand-back and next-step question as any other.

- `gh pr create --base main --head dev --assignee "@me" --label <type> --title … --body-file …`.
  The title says what ships: `chore(release): v<version>` when the version
  moved, `chore: promote dev to main` when it did not.
- The body names every pull request and issue it promotes. The version was
  bumped in the pull request into `dev` that needed it, never here.
- The required `promotion` check (`promotion.yml`) fails a pull request
  into `main` whose head is anything but this repository's `dev`, and runs
  again when the base is changed.

## Merging

The maintainer merges; an agent never does. Into `dev`, a maintainer's
sprint pull request merges as a merge commit; a contributor's may be
squashed, with the title as the commit subject. Into `main`, the promotion
merges as a merge commit, the only method its ruleset allows: it keeps
`dev`'s history in `main`, so the next promotion shows only what is new,
where a squash would leave `main` with a history `dev` does not share. Merging their own pull
request, the maintainer uses the ruleset's bypass for the code-owner
review: the gate and the pull request itself are never bypassed
(`docs/repository-settings.md`).
