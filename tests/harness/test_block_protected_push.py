"""The push guard: which commands it denies, and which it lets through.

Every form a review has found passing is a deny case here, so a regression
in the tokenizer shows up as a named command.
"""

import io
import json
import subprocess
from pathlib import Path

import block_protected_push as hook
import pytest
import shell_words


def decide(monkeypatch, payload: object, branch: str = "feat/1-x") -> str:
    """Run the hook on a payload; return what it printed."""
    monkeypatch.setattr(hook, "current_branch", lambda _cwd: branch)
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    out = io.StringIO()
    monkeypatch.setattr("sys.stdout", out)
    assert hook.main() == 0
    return out.getvalue()


def bash(command: str, cwd: str | None = None) -> dict[str, object]:
    payload: dict[str, object] = {
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }
    if cwd:
        payload["cwd"] = cwd
    return payload


def denial(output: str) -> str:
    """The deny reason; fails the test if the output is not a deny."""
    decision = json.loads(output)["hookSpecificOutput"]
    assert decision["hookEventName"] == "PreToolUse"
    assert decision["permissionDecision"] == "deny"
    reason = decision["permissionDecisionReason"]
    assert isinstance(reason, str)
    return reason


@pytest.mark.parametrize(
    ("command", "names"),
    [
        ("git push origin main", "main"),
        ("git push origin HEAD:main", "main"),
        ("git push origin feat/x:refs/heads/master", "master"),
        ("git push origin +refs/heads/x:refs/heads/master", "master"),
        ("git push origin x:heads/main", "main"),
        ("git push -u origin master", "master"),
        ("git push --force origin +main", "main"),
        ("git push origin main master", "main, master"),
        # Deleting a stage branch writes to it too.
        ("git push origin :main", "main"),
        ("git push --delete origin main", "main"),
        # Options before and between operands.
        ("git -C /repo push origin main", "main"),
        ("git push -o ci.skip origin main", "main"),
        ("git push --push-option=x origin main", "main"),
        ("git push origin --force main", "main"),
        ("git push --repo=origin main", "main"),
        ("git push --repo origin main", "main"),
        ("git push 'origin' \"main\"", "main"),
        ("/usr/bin/git push origin main", "main"),
        # Every branch.
        ("git push --all origin", "every branch (--all)"),
        ("git push --mirror", "every branch (--mirror)"),
        # A destination the hook cannot read is refused, not guessed.
        ("git push origin $BRANCH", "an unexpanded destination ($BRANCH)"),
        # Separators, touching or not, and new lines.
        ("git status && git push origin main", "main"),
        ("git push origin main;", "main"),
        ("git push origin main; echo hi", "main"),
        ("git push origin main&&true", "main"),
        ("cd x&&git push origin main", "main"),
        ("git status\ngit push origin main", "main"),
        ("git push \\\n  origin main", "main"),
        # Prefixes.
        ("FOO=1 git push origin main", "main"),
        ("GIT_SSH_COMMAND=x git push origin main", "main"),
        ("env X=1 git push origin main", "main"),
        ("sudo git push origin main", "main"),
        ("time git push origin main", "main"),
        ("timeout 30 git push origin main", "main"),
        ("nice -n 10 git push origin main", "main"),
        ("command git push origin main", "main"),
        # Grouping, substitution, control flow.
        ("(git push origin main)", "main"),
        ("{ git push origin main; }", "main"),
        ("echo $(git push origin main)", "main"),
        ("echo `git push origin main`", "main"),
        ("if true; then git push origin main; fi", "main"),
        ("for b in x; do git push origin main; done", "main"),
        # Wrappers.
        ('sh -c "git push origin main"', "main"),
        ("bash -lc 'cd x && git push origin master'", "master"),
        ("sh -c 'cd x && git push origin main'", "main"),
        ('eval "git push origin main"', "main"),
    ],
)
def test_a_push_to_a_stage_branch_is_denied(monkeypatch, command, names):
    reason = denial(decide(monkeypatch, bash(command)))
    assert f"it would write to {names}," in reason


@pytest.mark.parametrize(
    "command",
    ["git push origin HEAD", "git push -u origin HEAD", "git push origin @"],
)
def test_head_is_the_current_branch(monkeypatch, command):
    assert decide(monkeypatch, bash(command), branch="feat/x") == ""
    reason = denial(decide(monkeypatch, bash(command), branch="main"))
    assert "write to main," in reason


@pytest.mark.parametrize(
    "command", ["git push", "git push origin", "git push -u", "git push -f"]
)
def test_a_push_without_refspec_is_judged_by_the_current_branch(
    monkeypatch, command
):
    assert decide(monkeypatch, bash(command), branch="feature/x") == ""
    assert "write to main," in denial(
        decide(monkeypatch, bash(command), branch="main")
    )


def test_a_detached_head_or_unknown_branch_is_not_protected(monkeypatch):
    assert decide(monkeypatch, bash("git push"), branch="HEAD") == ""
    assert decide(monkeypatch, bash("git push"), branch="") == ""


@pytest.mark.parametrize(
    "command",
    [
        "git push origin sprint/topic",
        "git push -u origin feat/12-thing",
        "git push origin feature/main",
        "git push origin hotfix-dev",
        "git push origin main-fix",
        # From a protected branch to another name: only destinations count.
        "git push origin main:feature",
        "git push origin origin/main:refs/heads/sprint/x",
        # Tags are not branches.
        "git push origin refs/tags/main",
        "git push origin v1.2.3",
        "git push --tags",
        "git push origin --tags",
        # Not a push.
        "git log --oneline main",
        "echo push main",
        "echo 'git push origin main'",
        'git commit -m "then git push origin main"',
        "gh pr create --base main",
        "legit push origin main",
    ],
)
def test_a_push_elsewhere_passes(monkeypatch, command):
    assert decide(monkeypatch, bash(command), branch="main") == ""


@pytest.mark.parametrize(
    "command",
    [
        # A git alias is not expanded.
        "git -c alias.p=push p origin main",
        # A script's contents are not read.
        "./scripts/release.sh",
        # A prefix flag that takes a word is read as the command.
        "sudo -u bob git push origin main",
    ],
)
def test_known_limits_pass_and_are_documented(monkeypatch, command):
    # Pinned so that fixing one is a conscious change to this list and to
    # the limits in docs/agent-harness.md and the hook's docstring.
    assert decide(monkeypatch, bash(command), branch="feat/x") == ""


@pytest.mark.parametrize(
    "payload",
    ["not a dict", {"tool_input": "x"}, {"tool_input": {"command": 3}}, {}],
)
def test_a_malformed_payload_is_ignored(monkeypatch, payload):
    assert decide(monkeypatch, payload) == ""


def test_unparseable_stdin_is_ignored(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("{not json"))
    assert hook.main() == 0


def test_an_unbalanced_quote_does_not_crash(monkeypatch):
    assert shell_words.tokens_of('git push "origin main') == []
    assert decide(monkeypatch, bash('git push "origin main')) == ""


def wrapped(times: int) -> str:
    command = "git push origin main"
    for _ in range(times):
        command = f"sh -c {json.dumps(command)}"
    return command


def test_wrappers_are_followed_to_the_limit_and_no_further(monkeypatch):
    limit = shell_words.MAX_DEPTH
    assert denial(decide(monkeypatch, bash(wrapped(limit))))
    assert decide(monkeypatch, bash(wrapped(limit + 1))) == ""


def test_git_dash_c_moves_where_the_branch_is_read(monkeypatch, tmp_path):
    asked: list[str | None] = []

    def branch_in(cwd: str | None) -> str:
        asked.append(cwd)
        return "main"

    monkeypatch.setattr(hook, "current_branch", branch_in)
    assert hook.blocked("git -C sub push", str(tmp_path)) == ["main"]
    assert asked == [str(tmp_path / "sub")]


def test_the_payload_cwd_is_where_git_is_asked(tmp_path):
    assert hook.cwd_of({"cwd": str(tmp_path)}) == str(tmp_path)
    assert hook.cwd_of({"cwd": str(tmp_path / "missing")}) is None
    assert hook.cwd_of({"cwd": 3}) is None


# ------------------------------------------------- against a real repository


def git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q")
    git(
        tmp_path,
        "-c",
        "user.email=t@t",
        "-c",
        "user.name=t",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "init",
    )
    return tmp_path


def test_current_branch_reads_the_repository(repo, tmp_path_factory):
    assert hook.current_branch(str(repo)) == "main"
    outside = tmp_path_factory.mktemp("not-a-repo")
    assert hook.current_branch(str(outside)) == ""


def run_hook(payload: object, script: str = "block_protected_push.py") -> str:
    """The hook as Claude Code runs it: a python3 process, JSON on stdin."""
    path = Path(hook.__file__).with_name(script)
    result = subprocess.run(
        ["python3", str(path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        cwd="/",
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    return result.stdout


def test_a_bare_push_is_judged_in_the_payloads_repository(repo):
    # The hook process runs in `/`; only the payload says where the
    # command runs.
    assert "write to main," in denial(run_hook(bash("git push", str(repo))))
    git(repo, "checkout", "-q", "-b", "feat/1-x")
    assert run_hook(bash("git push", str(repo))) == ""


@pytest.mark.parametrize(
    "command",
    [
        "git --no-pager push origin main",
        "git --git-dir .git push origin main",
        "git --namespace x --no-pager push origin main",
    ],
)
def test_git_options_before_push_are_stepped_over(monkeypatch, command):
    assert "main" in denial(decide(monkeypatch, bash(command)))


def test_git_with_only_options_is_not_a_push(monkeypatch):
    # `push` here is the value of -C, a folder: no subcommand runs.
    assert decide(monkeypatch, bash("git -C push")) == ""


def test_current_branch_without_git_is_unknown(monkeypatch):
    def missing(*_args, **_kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr("subprocess.run", missing)
    assert hook.current_branch(None) == ""
