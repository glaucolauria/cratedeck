"""Split a Bash command line into the simple commands it runs.

Used by the push guard (block_protected_push.py), which needs to know
whether a command line runs `git push` anywhere in it: after a `;` or a
`)` with or without a space, on a later line or after a comment, behind
`FOO=1` or `sudo`, inside `( )`, `$( )` or backticks, quoted or not, or as
the command of `sh -c "..."`, `eval` or `xargs`.

Approximate on purpose. It does not expand variables, aliases or scripts,
and a heredoc body is read as commands. A line with an unbalanced quote is
read again with quotes as plain characters, so a stray `'` in a heredoc
never hides the lines after it. A false "this runs X" costs one refused
command; a false "it does not" is what the boundary behind the hook
(branch protection) exists for.
"""

from __future__ import annotations

import re
import shlex

# shlex returns a run of these characters as one token (`);`, `)&&`), which
# is then split into the operators below, longest first.
PUNCTUATION = frozenset("();<>|&")
OPERATORS = (
    "&&",
    "||",
    ";;",
    ";&",
    "|&",
    ">>",
    "<<",
    ">&",
    "<&",
    "&>",
    ">|",
    "<>",
    ";",
    "|",
    "&",
    "(",
    ")",
    "<",
    ">",
)
# Operators that end one simple command and start the next; `{`, `}` and
# `!` count when they are words of their own.
SEPARATORS = frozenset(
    {"&&", "||", ";", ";;", ";&", "|", "|&", "&", "(", ")", "{", "}", "!"}
)
# Outside quotes, a `#` after one of these, or at the start, opens a
# comment; anywhere else it is part of a word (`a#b`, `$#`).
WORD_BREAKS = frozenset(" \t\n;&|()<>")
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
# Shells: any argument that is not an option may be the command line they
# run (`sh -c "..."`); each is read as one.
SHELLS = frozenset({"sh", "bash", "zsh", "dash"})
# xargs options whose value is the next word.
XARGS_OPTIONS_WITH_VALUE = frozenset(
    {
        "-a",
        "-d",
        "-E",
        "-I",
        "-L",
        "-n",
        "-P",
        "-s",
        "--arg-file",
        "--delimiter",
        "--max-args",
        "--max-chars",
        "--max-lines",
        "--max-procs",
        "--process-slot-var",
    }
)
# What xargs adds from its input, which nobody can read in advance. The
# `$` makes it, to the guard, a word it cannot read.
XARGS_INPUT = "$XARGS_INPUT"
# A command substitution inside a word: it runs even in double quotes.
SUBSTITUTION = re.compile(r"\$\(|`")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
MAX_DEPTH = 3


def basename(word: str) -> str:
    return word.rsplit("/", 1)[-1]


def normalized(command: str, quoting: bool = True) -> str | None:
    """The line as shlex should read it; None when a quote is unbalanced.

    Outside quotes, a comment is dropped and a newline or a backtick ends
    a command the way `;` does. Inside quotes everything stays, newlines
    included. A line continuation (`\\` and a newline) joins two lines,
    even in the middle of a word. With `quoting` off, quote characters are
    plain characters.
    """
    out: list[str] = []
    quote = ""
    word_start = True
    index = 0
    while index < len(command):
        char = command[index]
        if char == "\\" and quote != "'":
            pair = command[index : index + 2]
            if pair != "\\\n":
                out.append(pair)
                word_start = False
            index += 2
            continue
        if quote:
            if char == quote:
                quote = ""
            out.append(char)
        elif quoting and char in "'\"":
            quote = char
            out.append(char)
            word_start = False
        elif char == "#" and word_start:
            end = command.find("\n", index)
            index = len(command) if end < 0 else end
            continue
        elif char in "\n`":
            out.append(" ; ")
            word_start = True
        else:
            out.append(char)
            word_start = char in WORD_BREAKS
        index += 1
    return None if quote else "".join(out)


def lexed(text: str, quoting: bool) -> list[str] | None:
    """shlex's tokens, or None when it cannot read the text."""
    lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    # normalized() has removed the comments; a `#` left is part of a word.
    lexer.commenters = ""
    if not quoting:
        lexer.quotes = ""
        lexer.escape = ""
    try:
        return list(lexer)
    except ValueError:
        return None


def operators_of(token: str) -> list[str]:
    """A run of punctuation as the operators it is made of."""
    if not token or not set(token) <= PUNCTUATION:
        return [token]
    parts: list[str] = []
    while token:
        operator = next(op for op in OPERATORS if token.startswith(op))
        parts.append(operator)
        token = token[len(operator) :]
    return parts


def tokens_of(command: str) -> list[str]:
    """Words and operators, quotes removed."""
    text = normalized(command)
    tokens = None if text is None else lexed(text, quoting=True)
    if tokens is None:
        tokens = lexed(normalized(command, quoting=False) or "", False) or []
    return [part for token in tokens for part in operators_of(token)]


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


def xargs_command(arguments: list[str]) -> list[str]:
    """The command `xargs <arguments>` runs, input included.

    The input goes where `-I` puts it, or after the last argument.
    """
    replace = ""
    index = 0
    while index < len(arguments) and arguments[index].startswith("-"):
        option = arguments[index]
        index += 1
        if option == "--":
            break
        if option == "-I" and index < len(arguments):
            replace = arguments[index]
        elif option.startswith(("-I", "-i")) and len(option) > 2:
            replace = option[2:]
        elif option in ("-i", "--replace"):
            replace = "{}"
        elif option.startswith("--replace="):
            replace = option.partition("=")[2]
        if option in XARGS_OPTIONS_WITH_VALUE:
            index += 1
    command = arguments[index:] or ["echo"]
    if replace:
        return [word.replace(replace, XARGS_INPUT) for word in command]
    return [*command, XARGS_INPUT]


def simple_commands(segment: list[str], depth: int) -> list[list[str]]:
    """The command a segment runs, and every command it runs in turn."""
    if depth > MAX_DEPTH:
        return []
    found: list[list[str]] = []
    for word in segment:
        if match := SUBSTITUTION.search(word):
            found.extend(commands_of(word[match.end() :], depth + 1))
    words = strip_prefixes(segment)
    if not words:
        return found
    found.append(words)
    name = basename(words[0])
    if name in SHELLS:
        for word in words[1:]:
            if not word.startswith(("-", "+")):
                found.extend(commands_of(word, depth + 1))
    elif name == "eval":
        # eval joins its arguments into one line before running it.
        found.extend(commands_of(" ".join(words[1:]), depth + 1))
    elif name == "xargs":
        found.extend(simple_commands(xargs_command(words[1:]), depth + 1))
    return found


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
        found.extend(simple_commands(segment, depth))
    return found
