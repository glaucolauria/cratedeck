# Repository settings

**English** · [Português](repository-settings.pt-BR.md)

What is configured on GitHub for this repository, why, and the commands that
apply and audit it. GitHub settings do not live in git, so this file is
their record: a change to a setting is a pull request that changes this
file, and the commands below reproduce the state. Applied on 2026-11-24.

`R` below is `repos/glaucolauria/cratedeck`.

## General

| Setting | Value | Why |
| --- | --- | --- |
| Description, topics | set | discoverability |
| Default branch | `dev` | every pull request lands there; Dependabot and closing keywords (`Closes #12`) act on the default branch |
| Issues, Discussions | on | issues for work, Discussions for questions and ideas |
| Wiki, Projects | off | documentation lives in the repository, work in issues |
| Merge commits | on | the only method: a pull request keeps its commits, and `main` keeps `dev`'s history |
| Squash merging, rebase merging | off | |
| Merge commit title | the pull request title | `dev` and `main` read like the release notes |
| Delete head branches | on | a branch dies with its pull request |
| Auto-merge | off | a maintainer merges, by hand |
| Suggest updating branches | on | |

```bash
# The stage branches: dev starts as a copy of main, then becomes the default.
gh api -X POST $R/git/refs -f ref=refs/heads/dev \
  -f sha="$(gh api $R/git/ref/heads/main --jq .object.sha)"
gh api -X PATCH $R -f default_branch=dev \
  -F has_wiki=false -F has_projects=false -F has_discussions=true -F has_issues=true \
  -F allow_merge_commit=true -F allow_squash_merge=false -F allow_rebase_merge=false \
  -f merge_commit_title=PR_TITLE -f merge_commit_message=PR_BODY \
  -F delete_branch_on_merge=true -F allow_auto_merge=false -F allow_update_branch=true
gh api -X PUT $R/topics -f 'names[]=cratedb' -f 'names[]=admin-ui' \
  -f 'names[]=database-admin' -f 'names[]=sql' -f 'names[]=sql-console' \
  -f 'names[]=self-hosted' -f 'names[]=database-tools'
```

## Rulesets

The rulesets as applied are in `.github/rulesets/`. Rulesets, rather than
classic branch protection, because two of them can be combined: one that
nobody bypasses, and one that only the admin may bypass, for a pull request.

| Ruleset | Target | Rules | Bypass |
| --- | --- | --- | --- |
| `dev` | `refs/heads/dev` | no deletion, no force push; a pull request is required (merge commit only); `check` and `pr-title` must pass, from GitHub Actions | **nobody** |
| `main` | `refs/heads/main` | the same, and `promotion` must pass too | **nobody** |
| `code-owner-review` | `dev` and `main` | one approval, from a code owner; stale approvals dismissed; the last push approved by someone other than its author; conversations resolved | repository admin, **for pull requests only** |
| `release-tags` | tags `v*` | no deletion, no update, no force push (creation is allowed) | **nobody**; in an emergency the ruleset is disabled, which the audit log records |

- The rulesets name their branches instead of `~DEFAULT_BRANCH`: the
  default branch is `dev`, and `main` must stay protected whatever the
  default is (`tests/harness/test_repository.py`).
- A contributor's pull request needs the maintainer's approval, the green
  gate and a pull request; nothing else reaches `dev`.
- `main` receives only the promotion of `dev`. `promotion` (`promotion.yml`)
  fails a pull request into `main` from any other head, and runs again
  when a pull request's base is changed, so a green result from a run
  against `dev` cannot carry over.
- The maintainer cannot approve their own pull request, so they merge it
  through the `code-owner-review` bypass, which the merge button offers
  explicitly and the ruleset's insights record. The `main` ruleset still
  holds: the pull request and the gate are never skipped.
- `check` is the aggregate job of `check.yml`, so legs of the gate matrix
  can change without touching the ruleset. Renaming `check` or `pr-title`
  blocks every pull request until the ruleset follows.

```bash
for f in dev main code-owner-review release-tags; do
  gh api -X POST $R/rulesets --input .github/rulesets/$f.json
done
# To change one: gh api -X PUT $R/rulesets/<id> --input .github/rulesets/<name>.json
```

**After CodeQL has analysed `dev` once**, add a code-scanning rule to the
`dev` and `main` rulesets, so that a pull request introducing a
high-severity alert cannot merge:

```json
{ "type": "code_scanning", "parameters": { "code_scanning_tools": [
  { "tool": "CodeQL", "security_alerts_threshold": "high_or_higher", "alerts_threshold": "errors" } ] } }
```

## Security and analysis

| Feature | State |
| --- | --- |
| Private vulnerability reporting | on: reports arrive as draft advisories |
| Dependency graph, Dependabot alerts | on |
| Dependabot security updates | on: a pull request as soon as an advisory has a fix |
| Dependabot version updates | `.github/dependabot.yml`: weekly, grouped, 7-day cooldown |
| Secret scanning, push protection | on |
| Secret scanning: generic patterns, validity checks | not available on this plan (`SECURITY.md`, "Known limits") |
| CodeQL | default setup, extended query suite; it analyses the languages the default branch, `dev`, has |
| OpenSSF Scorecard | `.github/workflows/scorecard.yml` |
| Immutable releases | on: once published, a release's assets and tag cannot change |

```bash
gh api -X PUT $R/vulnerability-alerts
gh api -X PUT $R/automated-security-fixes
gh api -X PUT $R/private-vulnerability-reporting
echo '{"security_and_analysis":{"secret_scanning":{"status":"enabled"},
  "secret_scanning_push_protection":{"status":"enabled"}}}' | gh api -X PATCH $R --input -
gh api -X PATCH $R/code-scanning/default-setup -f state=configured -f query_suite=extended
gh api -X PUT $R/immutable-releases
```

## Actions

| Setting | Value | Why |
| --- | --- | --- |
| Allowed actions | GitHub's own (`actions/*`, `github/*`) plus `astral-sh/setup-uv@*` and `ossf/scorecard-action@*` | a third-party action is code with access to the run; adding one is a reviewed change to this list |
| Require actions pinned to a full SHA | on | a tag can be moved by whoever controls the action's repository |
| Default `GITHUB_TOKEN` | read-only; Actions cannot approve pull requests | each job asks for what it needs, documented inline |
| Fork pull request workflows | approval required for every external contributor | a first run from a stranger does not execute until a maintainer has read it |

```bash
echo '{"enabled":true,"allowed_actions":"selected","sha_pinning_required":true}' \
  | gh api -X PUT $R/actions/permissions --input -
echo '{"github_owned_allowed":true,"verified_allowed":false,
  "patterns_allowed":["astral-sh/setup-uv@*","ossf/scorecard-action@*"]}' \
  | gh api -X PUT $R/actions/permissions/selected-actions --input -
gh api -X PUT $R/actions/permissions/workflow \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=false
gh api -X PUT $R/actions/permissions/fork-pr-contributor-approval \
  -f approval_policy=all_external_contributors
```

A workflow that needs a new third-party action: add it to
`patterns_allowed` in the same pull request, in this file, and say why.

## Labels

The set `issue-hygiene` describes: GitHub's defaults plus `chore`,
`security`, `dependencies`, `github_actions`, `breaking-change` and
`triage`.

```bash
gh label create chore --color c5def5 --description "Tooling, process or maintenance" --force
# … one line per label; `gh label list` shows them all.
```

## Set by hand (no API)

- **Social preview image:** Settings → General → Social preview.
- **Reported content:** Settings → Moderation options → Reported content →
  accept reports from all users, so the Code of Conduct's reporting channel
  reaches the maintainers.
- **Security alert e-mails:** Watch → Custom → Security alerts, on the
  maintainer's account.

## Auditing

Read-only; compare the output with the tables above.

```bash
gh api $R --jq '{default_branch, has_wiki, has_projects, has_discussions, allow_merge_commit,
  allow_squash_merge, allow_rebase_merge, delete_branch_on_merge, allow_auto_merge,
  security: .security_and_analysis}'
gh api $R/rulesets --jq '.[] | {id, name, enforcement}'
for id in $(gh api $R/rulesets --jq '.[].id'); do
  gh api $R/rulesets/$id --jq '{name, bypass: .bypass_actors, rules: [.rules[].type]}'
done
gh api $R/actions/permissions
gh api $R/actions/permissions/selected-actions
gh api $R/actions/permissions/workflow
gh api $R/actions/permissions/fork-pr-contributor-approval
gh api $R/code-scanning/default-setup --jq '{state, languages, query_suite}'
gh api $R/private-vulnerability-reporting
gh api $R/immutable-releases
gh api $R/vulnerability-alerts -i 2>&1 | head -1        # 204 = on
gh api $R/automated-security-fixes --jq .enabled          # true
```
