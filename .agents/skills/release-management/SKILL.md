---
name: release-management
description: Use when deciding whether a change in cratedeck bumps the version and by how much, when preparing a release, or when explaining what a merge into dev or main does and does not do.
---

# Release management

## What a merge does

A merge into `dev` releases nothing. A merge into `main` is only ever the
promotion of `dev` (`git-workflow`), and `create_release.yml` runs on the
push it produces. It reads the version (`version` in `package.json`, or
`project.version` in `pyproject.toml`):

- **No version file** (before the app exists): nothing; a notice says so.
- **`v<version>` already exists**: nothing. The merge did not bump the
  version, so it is not a release.
- **A new version**: `gh release create v<version> --generate-notes`, with
  the CycloneDX SBOM of the production dependencies attached; with no
  lockfile to build it from, the run fails rather than release without
  one. A version with a pre-release suffix (`0.3.0-rc.1`) is marked as a
  pre-release.

The notes are generated from the merged pull requests' titles, grouped by
their labels (`.github/release.yml`). Nobody writes them by hand, which is
why the title and the label of every pull request matter.

## Versioning

SemVer, read from the point of view of the person who runs cratedeck
against their cluster. Bump **in the branch**, before the pull request into
`dev`; the promotion carries the version to `main` unchanged.

| Change | Bump |
| --- | --- |
| A removed screen or flow users must relearn; a dropped CrateDB version; a setting or deployment option that changes meaning | **major** (and the `breaking-change` label). Before 1.0, a minor. |
| A new screen, feature, setting, or newly supported CrateDB version | **minor** |
| A fix; a dependency update that ships to users | **patch** |
| Documentation, the agent harness (`.claude/`, `.agents/`), workflows, tests only | **none** |

A breaking change also carries the `breaking-change` label, whatever the
number says. The release notes put it in its own section.

## Pre-merge checklist

1. The gate green on the pull request (`check`, `pr-title`).
2. The pull request labelled.
3. The version decided and, when release-relevant, committed.
4. The CHANGELOG is the release notes: nothing else to update.
5. For a promotion: `dev` holds what should ship, and its version is the
   one to release.

## After a merge into `main`

Confirm the result: `gh release list --limit 3` when the version moved, or
the notice in `gh run list --workflow create_release.yml --limit 1`
otherwise. A failed run leaves `main` ahead of its last release with no
error anyone sees unless someone looks.

## Things that bite

- `fetch-depth: 0` in `create_release.yml` is load-bearing: a shallow
  checkout has no tags, so every merge would look like a new version.
- Tags `v*` cannot be moved or deleted (the `release-tags` ruleset), and
  releases are immutable once published. A bad release is fixed by a new
  version, not by editing the old one.
- The release runs on `push`, not on `pull_request: closed`: a merged pull
  request from a fork still runs with a read-only token and could not
  create the tag.
- Every merge is a merge commit, never squashed or rebased (the rulesets
  allow nothing else): `main` keeps `dev`'s history, so the next promotion
  carries only what is new.
