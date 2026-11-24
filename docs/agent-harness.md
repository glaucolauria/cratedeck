# The agent harness

**English** · [Português](agent-harness.pt-BR.md)

cratedeck is developed with coding agents, by its maintainer and, welcome,
by contributors. The rules and procedures they follow are written down in
the repository, in files every tool reads, so that the result is the same
whichever agent a person uses. This page says what those files are, which
tool reads what, and what the one hook does.

## The pieces

| Where | What | Loaded |
| --- | --- | --- |
| `AGENTS.md` | the repository's rules, stated once | every session, every tool |
| `.agents/skills/<name>/SKILL.md` | procedures: `git-workflow`, `issue-hygiene`, `release-management`, `quality-gate` | on demand, when the task matches the skill's description |
| `.claude/agents/<name>.md` | sub-agents with a narrow job: `pm`, `qa`, `cybersec` | on demand, in tools that read this format |
| `.claude/hooks/` | the push guard | before every shell command, in Claude Code |
| `.claude/settings.json` | Claude Code's permissions (allow and deny) and the hook | every Claude Code session |

There is no `CLAUDE.md`: Claude Code reads `AGENTS.md` when there is none,
and a `CLAUDE.md` or `CLAUDE.local.md` would hide it. Personal notes go in
`~/.claude/CLAUDE.md`.

Every instruction file has a Portuguese twin for people
(`AGENTS.pt-BR.md`, `<skill>/README.pt-BR.md`,
`.claude/agents.pt-BR/<name>.md`). No tool loads them, so they cost no
tokens; they change in the same pull request as the English.

## Which tool reads what

| Tool | `AGENTS.md` | Skills | Agents | Hook and permissions |
| --- | --- | --- | --- | --- |
| Claude Code (CLI, IDE extensions) | yes | `.claude/skills`, a link to `.agents/skills` | `.claude/agents/` | yes |
| Codex | yes | `.agents/skills/` | no | no |
| Cursor, Gemini CLI, Copilot and others | yes | `.agents/skills/`, where the tool supports skills | no | no |

A tool without the hook loses a convenience, not a control: the rulesets
refuse a push to `main` from anyone. A tool without sub-agents runs the
same reviews in the main session, following the agent's file as a
checklist.

On Windows, git may check `.claude/skills` out as a plain file instead of a
link: enable `core.symlinks` (and Developer Mode), or point the tool at
`.agents/skills/` directly.

## The push guard

`.claude/hooks/block_protected_push.py`, a `PreToolUse` hook on Bash:
it denies a `git push` whose destination is `main` or `master`, wherever
the push sits on the command line (after `;` or `&&`, on a later line,
behind `FOO=1` or `sudo`, inside `sh -c`), with `HEAD` and a bare push
resolved to the current branch, and `--all` and `--mirror` refused. A
destination it cannot read (`$BRANCH`) is refused rather than guessed.

- It needs only the system `python3` (3.9+), standard library only, and
  never fails the command it observes.
- It is a guardrail, not a boundary: it does not expand git aliases
  (`git -c alias.p=push p`), read scripts, or see a ref moved through the
  API. The rulesets are the boundary.
- `tests/harness/test_block_protected_push.py` names every command form it
  must deny and every one it must let through, including these limits.

## Permissions

`.claude/settings.json` allows, without a prompt, a few exact read-only
commands (`git status`, `git diff`, `gh pr view`, the `make` gate targets),
never a prefix that also takes an option able to write a file or run a
program (`git diff --output`, `git fetch --upload-pack`). It denies reading
secret files (`.env*`, keys, `~/.ssh`, `~/.aws`, `gh`'s token, the local
private-names list), force pushes, `gh pr merge`, `gh repo delete` and
package runners (`npx`, `npm exec`, `pnpm dlx`, `bunx`). It saves mistakes;
it is not a sandbox: a `make` target runs whatever the checked-out branch
holds.

## Trust

When you open a clone in Claude Code, you are asked to trust the folder;
the hook and the settings then apply. **Read `.claude/`, `.agents/`, the
`Makefile` and `tests/` in a pull request before you check it out and work
in it with an agent or run `make`**: they are instructions and code that
will run with your credentials. `CODEOWNERS`
puts them under the maintainer's review for the same reason.

## Changing the harness

A change to any of these files is a pull request like any other, with a
security note (`SECURITY.md`), its Portuguese twin, and `make ci` green:
`tests/harness/test_repository.py` checks that each skill and agent has its
frontmatter and its twin with the same headings.
