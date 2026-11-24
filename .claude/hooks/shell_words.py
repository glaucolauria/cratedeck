"""Split a Bash command line into the simple commands it runs.

Shared by the hooks, which both need to know whether a command line runs
`git push` or `gh pr create` somewhere in it -- after a `;`, on a later
line, behind `FOO=1` or `sudo`, inside `( )` or `$( )`, or inside
`sh -c "..."`.

Approximate on purpose. It does not expand variables, aliases or scripts,
and a heredoc body is read as commands. A false "this runs X" costs one
refused command; a false "it does not" is what the boundary behind the
hook (branch protection) exists for.
"""

from __future__ import annotations

import re
import shlex

# Tokens that end one simple command and start the next. With
# `punctuation_chars`, shlex returns these as tokens of their own even
# when they touch a word (`main;`, `a&&b`).
SEPARATORS = frozenset(
    {"&&", "||", ";", ";;", "|", "|&", "&", "(", ")", "{", "}", "!"}
)
# Shell keywords that can start a segment before the command proper.
KEYWORDS = frozenset({"if", "then", "else", "elif", "do", "while", "until"})
# Commands that run the rest of the line as another command.
PREFIX_COMMANDS = frozenset(
    {
        "env",
        "sudo",
        "time",
        "timeout",
        "command",
        "builtin",
        "exec",
        "nice",
        "nohup",
    }
)
# A prefix's own arguments: flags, and numbers or durations
# (`nice -n 10`, `timeout 30s`).
PREFIX_ARGUMENT = re.compile(r"^(-.*|\d+(\.\d+)?[smhd]?)$")
# Commands whose arguments are themselves a command line.
WRAPPERS = frozenset({"sh", "bash", "zsh", "dash", "eval", "xargs"})
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
MAX_DEPTH = 3


def basename(word: str) -> str:
    return word.rsplit("/", 1)[-1]


def tokens_of(command: str) -> list[str]:
    """Words and operators, quotes removed; empty when unparseable."""
    # A line continuation joins two lines into one command. Any other
    # newline, and a backtick, ends a command the way `;` does; inside
    # quotes the replacement stays part of the same quoted word.
    text = command.replace("\\\n", " ")
    text = text.replace("\n", " ; ").replace("`", " ; ")
    lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:
        return []


def strip_prefixes(words: list[str]) -> list[str]:
    """The command proper: without `then`, `FOO=1`, `env`, `sudo`, ...

    A prefix's flags and numeric arguments are skipped; a flag that takes
    a word (`sudo -u bob`) is not understood, and the word is read as the
    command.
    """
    index = 0
    while index < len(words):
        word = words[index]
        if ASSIGNMENT.match(word) or word in KEYWORDS:
            index += 1
        elif basename(word) in PREFIX_COMMANDS:
            index += 1
            while index < len(words) and PREFIX_ARGUMENT.match(words[index]):
                index += 1
        else:
            break
    return words[index:]


def commands_of(command: str, depth: int = 0) -> list[list[str]]:
    """Every simple command in the line, descending into wrappers."""
    if depth > MAX_DEPTH:
        return []
    segments: list[list[str]] = [[]]
    for token in tokens_of(command):
        if token in SEPARATORS:
            segments.append([])
        else:
            segments[-1].append(token)

    found: list[list[str]] = []
    for segment in segments:
        words = strip_prefixes(segment)
        if not words:
            continue
        found.append(words)
        if basename(words[0]) in WRAPPERS:
            for word in words[1:]:
                if not word.startswith("-"):
                    found.extend(commands_of(word, depth + 1))
    return found
