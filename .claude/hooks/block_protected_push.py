#!/usr/bin/env python3
"""Deny a `git push` whose destination is a protected branch.

Every change reaches the stage branches, `dev` and then `main`, through a
pull request (AGENTS.md, "Stage flow"; the `git-workflow` skill). The
repository's rulesets enforce that server-side
(docs/repository-settings.md). This hook refuses the push before it leaves
the machine, so the refusal is immediate and says what to do instead.

It inspects the *destination* of each refspec rather than looking for a
branch name anywhere in the command: `git push origin x:main` is blocked,
`git push origin main:sprint/x` is not. `HEAD`, a bare `git push` and a
remote-only push resolve to the current branch of the repository the
command runs in -- the payload's `cwd`, or `git -C <dir>`. A wildcard
destination (`refs/heads/*`) is matched against the protected branches;
`:`, `--all` and `--mirror` write every branch both sides have, or every
branch, and are refused.

A destination it cannot read (`$BRANCH`, or what `xargs` adds from its
input) is refused rather than guessed: the cost is one retry with the
branch spelled out. `--tags` alone pushes tags, not branches, and passes.

A guardrail, not a security boundary. It does not see git aliases
(`git -c alias.p=push p`), scripts, a `cd` earlier on the line, another
repository named by `--git-dir` or `GIT_DIR`, push configuration
(`remote.<name>.push`, `push.default=matching`), or a ref moved through the
API (`gh api .../git/refs/heads/main`); the boundary is the rulesets.

Reads a PreToolUse payload on stdin. Prints a deny decision on stdout when
it should block, nothing otherwise. Python 3.9+, standard library only.
"""

from __future__ import annotations

import json
import re

# Driving git is the whole point of this hook. Every call is list-form with
# no shell=True, so nothing reaches a shell parser.
import subprocess
import sys
from pathlib import Path
from typing import Any

from shell_words import basename, commands_of

# The stage branches, and the name a fresh clone elsewhere may still use.
# tests/harness/test_repository.py checks that every branch a ruleset
# protects is here.
PROTECTED = frozenset({"dev", "main", "master"})
GIT_OPTIONS_WITH_VALUE = (
    "-C",
    "--git-dir",
    "--work-tree",
    "--namespace",
    "-c",
)
PUSH_OPTIONS_WITH_VALUE = ("-o", "--push-option", "--receive-pack", "--exec")
# Push every branch, so every stage branch the clone has.
EVERY_BRANCH = frozenset({"--all", "--mirror", "--branches"})
CURRENT = frozenset({"HEAD", "@"})


def read_payload() -> dict[str, Any]:
    """The hook payload, or an empty dict when stdin is not one."""
    try:
        payload: Any = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def command_of(payload: dict[str, Any]) -> str:
    """The Bash command the hook is looking at, or an empty string."""
    tool_input = payload.get("tool_input", {})
    if not isinstance(tool_input, dict):
        return ""
    command = tool_input.get("command", "")
    return command if isinstance(command, str) else ""


def cwd_of(payload: dict[str, Any]) -> str | None:
    """The session's working directory, when the payload names one.

    A plugin hook's own working directory is not documented to be the
    project, and `git rev-parse` answers for whatever repository it runs
    in. The payload's `cwd` is where the command will run.
    """
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and Path(cwd).is_dir():
        return cwd
    return None


def parse_git_push(
    words: list[str], cwd: str | None
) -> tuple[int, str | None]:
    """(index after `push`, directory git runs in), or (-1, cwd)."""
    if not words or basename(words[0]) != "git":
        return -1, cwd
    index = 1
    while index < len(words):
        word = words[index]
        if word == "-C" and index + 1 < len(words):
            base = Path(cwd) if cwd else Path.cwd()
            cwd = str(base / words[index + 1])
            index += 2
        elif word in GIT_OPTIONS_WITH_VALUE:
            index += 2
        elif word.startswith("-"):
            index += 1
        else:
            return (index + 1 if word == "push" else -1), cwd
    return -1, cwd


def current_branch(cwd: str | None) -> str:
    """Current branch, or an empty string when git cannot say."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
            cwd=cwd,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def refspec_destination(token: str) -> str:
    """The destination of a refspec, without the leading `+`."""
    spec = token.lstrip("+")
    return spec.rsplit(":", 1)[-1] if ":" in spec else spec


def protected_matches(destination: str) -> list[str]:
    """The protected branches a destination writes to.

    `main`, `heads/main` and `refs/heads/main` are the same ref; a `*`
    matches any run of characters, as it does in a refspec, so
    `refs/heads/*` writes to all of them and `refs/tags/*` to none.
    """
    if destination.startswith("refs/"):
        ref = destination
    elif destination.startswith("heads/"):
        ref = f"refs/{destination}"
    else:
        ref = f"refs/heads/{destination}"
    pattern = re.escape(ref).replace(r"\*", ".*")
    return sorted(
        branch
        for branch in PROTECTED
        if re.fullmatch(pattern, f"refs/heads/{branch}")
    )


def protected_destinations(
    words: list[str], start: int, cwd: str | None
) -> list[str]:
    """What this push would write to that is protected."""
    operands: list[str] = []
    remote_given = False
    tags_only = False
    index = start
    while index < len(words):
        word = words[index]
        if word == "--repo":
            remote_given = True
            index += 2
            continue
        if word.startswith("--repo="):
            remote_given = True
        elif word in EVERY_BRANCH:
            return [f"every branch ({word})"]
        elif word == "--tags":
            tags_only = True
        elif word in PUSH_OPTIONS_WITH_VALUE:
            index += 1
        elif not word.startswith("-"):
            operands.append(word)
        index += 1

    # The first operand is the remote, unless `--repo` named it. With no
    # refspec, git pushes the current branch -- or, with `--tags`, only
    # the tags.
    targets = []
    refspecs = operands if remote_given else operands[1:]
    if not remote_given and operands and "$" in operands[0]:
        # An unread remote may expand to refspecs as well.
        targets.append(f"whatever {operands[0]} expands to")
    if not refspecs:
        refspecs = [] if tags_only else ["HEAD"]
    for spec in refspecs:
        if spec.lstrip("+") == ":":
            targets.append("every branch both sides have (:)")
            continue
        destination = refspec_destination(spec)
        if "$" in destination:
            targets.append(f"an unexpanded destination ({destination})")
            continue
        if destination in CURRENT:
            destination = current_branch(cwd)
        targets.extend(protected_matches(destination))
    return targets


def blocked(command: str, cwd: str | None) -> list[str]:
    """Protected destinations of every `git push` in the command line."""
    targets: list[str] = []
    for words in commands_of(command):
        start, where = parse_git_push(words, cwd)
        if start >= 0:
            targets.extend(protected_destinations(words, start, where))
    return targets


def deny(targets: list[str]) -> None:
    names = ", ".join(sorted(set(targets)))
    reason = (
        f"Push blocked: it would write to {names}, and the stage branches "
        "(`dev`, then `main`) only change through a pull request (the "
        "git-workflow skill). Push a task or sprint branch and open a PR "
        "into `dev`. Pushing *from* a protected branch to another name is "
        "fine; only the destination is blocked."
    )
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )


def main() -> int:
    payload = read_payload()
    # No shortcut on the text: `git pu""sh` is a push too.
    targets = blocked(command_of(payload), cwd_of(payload))
    if targets:
        deny(targets)
    return 0


if __name__ == "__main__":
    sys.exit(main())
