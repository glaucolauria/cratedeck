---
name: quality-gate
description: Use whenever running, changing or reviewing cratedeck's quality gate, or writing tests for it. The Makefile targets, what check.yml runs on each architecture, when to run what, the tools' pinned versions, suppressions, and the review checklist.
---

# Quality gate

The `Makefile` defines the commands and pins every tool's version;
`.github/workflows/check.yml` runs the same targets. When this file and
they disagree, they win, and this file is fixed.

## The targets

| Target | Runs | Notes |
| --- | --- | --- |
| `test` | pytest over `tests/` | the push guard's tests and the repository's structure checks (`tests/harness`) |
| `security` | semgrep, `--error` | `p/python`, `p/secrets`, `p/security-audit`, `p/cwe-top-25`, `p/owasp-top-ten`, `p/ci` over `.github .claude .agents tests` |
| `workflows` | zizmor | the workflows and `dependabot.yml`; online audits when `GH_TOKEN` is set |
| `check` | all of the above | a developer's terminal; may rewrite files once formatters exist |
| `ci` | the same, verifying only | what `check.yml` runs |
| `clean` | removes `.cache/` | |

Every tool runs through `uvx` at the exact version in the `Makefile`
variables, so the only requirement is `uv`. `UV_EXCLUDE_NEWER`, exported by
the `Makefile`, resolves the tools' own dependencies as of a fixed date:
moving a pin means moving that date too, to at least 7 days before the
day, in a `dependencies` pull request. Caches and reports go under
`.cache/`.

**The app's targets** (`install`, `fmt`, `lint`, `types`, the app's tests,
`build`) arrive with the stack, in the same pull request that adds the
app's code, together with their steps in `check.yml` and their packs in
`SEMGREP`.

## In CI

`check.yml` on every pull request into `dev` or `main`:

- `gate`, a matrix over `ubuntu-24.04` (amd64) and `ubuntu-24.04-arm`
  (arm64): one step per target of `make ci`, each running even after an
  earlier one failed, so one run reports every failure. The app's build
  joins this matrix.
- `check`, after every leg: the dependency review (new dependencies with a
  moderate-or-worse advisory, or a license that does not fit Apache-2.0),
  then it fails unless every leg passed. `check` is the required status on
  both stages.

`promotion.yml`, on every pull request into `main` and on every edit to
one (a change of base included), fails unless the head is this
repository's `dev`. Required on `main` only.

`make -k ci` reports every failure in a terminal, as the gate does. A
failure on one architecture only is the information the matrix exists
for: read that leg's log before re-running anything, and re-run failed
jobs only (`gh run rerun <id> --failed`).

## When to run what

```bash
make test        # while changing the hooks or the repository's structure
make workflows   # after touching .github/workflows or dependabot.yml
make ci          # once, on the branch that becomes the pull request
```

## Tests

- A test asserts behaviour, not that code ran: the hook's decision for a
  given command, a file the structure check requires.
- A bug fix has a regression test that fails before the fix.
- `tests/harness/test_block_protected_push.py` lists every command form
  the guard must deny or let through; a new form found passing becomes a
  case there first.
- `tests/harness/test_repository.py` holds the repository's structure:
  Portuguese twins, skill and agent frontmatter, actions pinned by SHA,
  workflow permissions and timeouts, the stage rulesets and their required
  checks, the script that keeps `main` for `dev`, and no private names in
  the files or unpushed commits (against the maintainer's local list,
  `AGENTS.md`, "Public repository"; skipped where there is none, as in
  CI).

## Suppressions

Fix first. Then the narrowest thing, with the reason beside it:
`# nosemgrep: <rule-id> <why>`, `# noqa: <code>  # <why>`, a zizmor
`# zizmor: ignore[<audit>] <why>`. Never a file-wide disable for one line.
Every suppression also gets a row in `SECURITY.md`, "Security exceptions",
in the same pull request.

## Review checklist

1. `make ci` green, on both architectures in CI.
2. Tests cover the failure paths, not only the happy one.
3. A security-relevant change (`SECURITY.md`) has a negative test where
   one is possible, and a written note.
4. A new tool or version pin moves in the `Makefile` variable, in a pull
   request labelled `dependencies`.
