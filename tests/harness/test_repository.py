"""The repository's structure: the rules in AGENTS.md that a test can hold.

Each test names the rule it holds. They read files only, with the standard
library, so they run anywhere `make test` does.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".agents" / "skills"
AGENTS = ROOT / ".claude" / "agents"
AGENTS_PT = ROOT / ".claude" / "agents.pt-BR"
WORKFLOWS = ROOT / ".github" / "workflows"
FENCE = re.compile(r"^(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def heading_levels(path: Path) -> list[int]:
    """The level of every Markdown heading outside fenced code."""
    levels: list[int] = []
    fenced = False
    for line in read(path).splitlines():
        if FENCE.match(line):
            fenced = not fenced
        elif not fenced and (match := HEADING.match(line)):
            levels.append(len(match.group(1)))
    return levels


def frontmatter(path: Path) -> dict[str, str]:
    """The `key: value` lines of a YAML frontmatter block, or {}."""
    text = read(path)
    if not text.startswith("---\n"):
        return {}
    block = text[4:].split("\n---\n", 1)[0]
    fields: dict[str, str] = {}
    for line in block.splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


# ------------------------------------------------ AGENTS.md, "Language"

PEOPLE_DOCS = [
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "SUPPORT.md",
    "CODE_OF_CONDUCT.md",
    *sorted(
        str(p.relative_to(ROOT))
        for p in (ROOT / "docs").glob("*.md")
        if not p.name.endswith(".pt-BR.md")
    ),
]


def twins() -> list[tuple[Path, Path]]:
    pairs = [
        (ROOT / doc, ROOT / doc.replace(".md", ".pt-BR.md"))
        for doc in PEOPLE_DOCS
    ]
    pairs.append((ROOT / "AGENTS.md", ROOT / "AGENTS.pt-BR.md"))
    pairs += [
        (skill, skill.with_name("README.pt-BR.md"))
        for skill in sorted(SKILLS.glob("*/SKILL.md"))
    ]
    pairs += [
        (agent, AGENTS_PT / agent.name) for agent in sorted(AGENTS.glob("*.md"))
    ]
    return pairs


@pytest.mark.parametrize(
    ("english", "portuguese"),
    twins(),
    ids=lambda p: str(p.relative_to(ROOT)),
)
def test_every_english_document_has_its_portuguese_twin(english, portuguese):
    assert portuguese.is_file(), f"missing {portuguese.relative_to(ROOT)}"
    assert heading_levels(portuguese) == heading_levels(english), (
        f"{portuguese.relative_to(ROOT)}: headings differ from the English"
    )


@pytest.mark.parametrize("doc", PEOPLE_DOCS)
def test_each_people_document_links_to_its_twin(doc):
    english = ROOT / doc
    twin = english.with_name(english.name.replace(".md", ".pt-BR.md"))
    assert f"]({twin.name})" in read(english)
    assert f"]({english.name})" in read(twin)


def test_twins_carry_no_frontmatter():
    # A twin with a frontmatter could be loaded as a skill or an agent.
    for path in [*SKILLS.glob("*/README.pt-BR.md"), *AGENTS_PT.glob("*.md")]:
        assert not read(path).startswith("---"), path.relative_to(ROOT)


# ---------------------------------------------- skills and agents load


@pytest.mark.parametrize(
    "skill", sorted(SKILLS.glob("*/SKILL.md")), ids=lambda p: p.parent.name
)
def test_every_skill_has_its_frontmatter(skill):
    fields = frontmatter(skill)
    assert fields.get("name") == skill.parent.name
    description = fields.get("description", "")
    assert description.startswith("Use "), "the description is the trigger"
    assert len(description) <= 1024


@pytest.mark.parametrize(
    "agent", sorted(AGENTS.glob("*.md")), ids=lambda p: p.stem
)
def test_every_agent_has_its_frontmatter(agent):
    fields = frontmatter(agent)
    assert fields.get("name") == agent.stem
    assert fields.get("description")
    assert fields.get("tools")
    assert fields.get("model")


def test_claude_reads_the_shared_skills():
    link = ROOT / ".claude" / "skills"
    assert link.is_symlink(), ".claude/skills must link to ../.agents/skills"
    assert link.resolve() == SKILLS.resolve()


def test_there_is_no_claude_md():
    # Either file hides AGENTS.md from Claude Code (docs/agent-harness.md).
    assert not (ROOT / "CLAUDE.md").exists()
    assert not (ROOT / "CLAUDE.local.md").exists()


# --------------------------------------------- AGENTS.md, rules 4 and 5

USES = re.compile(r"^\s*(?:-\s+)?uses:\s*(\S+)(.*)$", re.MULTILINE)
PINNED = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")


def workflow_files() -> list[Path]:
    return sorted([*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")])


@pytest.mark.parametrize("workflow", workflow_files(), ids=lambda p: p.name)
def test_every_action_is_pinned_by_sha(workflow):
    for reference, rest in USES.findall(read(workflow)):
        assert PINNED.match(reference), f"{workflow.name}: {reference}"
        assert re.match(r"\s*#\s*v\d", rest), (
            f"{workflow.name}: {reference} needs its version in a comment"
        )


@pytest.mark.parametrize("workflow", workflow_files(), ids=lambda p: p.name)
def test_every_workflow_is_least_privilege_and_bounded(workflow):
    text = read(workflow)
    assert re.search(r"^permissions:", text, re.MULTILINE), (
        f"{workflow.name}: top-level permissions"
    )
    assert "pull_request_target" not in text
    jobs = len(re.findall(r"^\s+runs-on:", text, re.MULTILINE))
    timeouts = len(re.findall(r"^\s+timeout-minutes:", text, re.MULTILINE))
    assert jobs == timeouts, f"{workflow.name}: every job has a timeout"


def make_targets(name: str) -> list[str]:
    match = re.search(
        rf"^{name}:([^\n]*)$", read(ROOT / "Makefile"), re.MULTILINE
    )
    assert match, f"no `{name}:` target"
    return match.group(1).split()


def test_the_gate_runs_every_target_of_make_ci():
    # The pipeline and a developer's terminal check the same things.
    check = read(WORKFLOWS / "check.yml")
    steps = re.findall(r"run: make (\S+)", check)
    assert steps == make_targets("ci")


def test_every_required_check_is_a_job():
    # Renaming a required job blocks every pull request.
    ruleset = json.loads(read(ROOT / ".github" / "rulesets" / "main.json"))
    required = [
        check["context"]
        for rule in ruleset["rules"]
        if rule["type"] == "required_status_checks"
        for check in rule["parameters"]["required_status_checks"]
    ]
    names = {
        name
        for workflow in workflow_files()
        for name in re.findall(r"^\s{4}name:\s*(\S+)\s*$", read(workflow), re.M)
    }
    assert required
    assert set(required) <= names, set(required) - names


# ---------------------------------- AGENTS.md, "Public repository", rule 1

# Names that must never appear in this repository (the maintainers'
# employers, clients and private projects) live in a file on each
# maintainer's machine, never in the repository: published, even hashed, a
# short word is one dictionary lookup away. Without the file the checks
# skip; they matter before a push, on the machine that pushes, since
# anything CI sees is already public.
PRIVATE_NAMES_FILE = Path(
    os.environ.get(
        "CRATEDECK_PRIVATE_NAMES",
        Path.home() / ".config" / "cratedeck" / "private-names",
    )
)
# Unicode words: an accented letter is part of the word, so a Portuguese
# word is never split into a fragment that looks like a name.
WORD = re.compile(r"[^\W_]+")


def private_names() -> frozenset[str]:
    """One word per line, `#` comments; empty when the file is absent."""
    try:
        lines = PRIVATE_NAMES_FILE.read_text(encoding="utf-8").splitlines()
    except OSError:
        return frozenset()
    return frozenset(
        line.strip().lower()
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    )


def private_words(text: str, names: frozenset[str]) -> set[str]:
    return set(WORD.findall(text.lower())) & names


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else ""


def repository_files() -> list[Path]:
    """Tracked files, and new ones git does not ignore."""
    listed = git("ls-files", "--cached", "--others", "--exclude-standard")
    return [ROOT / name for name in listed.splitlines() if name]


@pytest.fixture
def names() -> frozenset[str]:
    found = private_names()
    if not found:
        pytest.skip(f"no private-names list at {PRIVATE_NAMES_FILE}")
    return found


def test_the_word_matcher_finds_whole_words_only():
    made_up = frozenset({"acme", "initech"})
    assert private_words("Built at ACME; initech's tool", made_up) == {
        "acme",
        "initech",
    }
    # A name inside a longer word, accented or not, is not that name.
    assert private_words("acmeville acmeção initechs", made_up) == set()


def test_the_names_file_ignores_comments_and_blanks(tmp_path, monkeypatch):
    listed = tmp_path / "names"
    listed.write_text("# comment\n\n  Acme \ninitech\n", encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "PRIVATE_NAMES_FILE", listed)
    assert private_names() == {"acme", "initech"}


def test_no_private_names_in_the_files(names):
    found = []
    for path in repository_files():
        if not path.is_file() or path.is_symlink():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if private_words(f"{path.relative_to(ROOT)}\n{text}", names):
            found.append(str(path.relative_to(ROOT)))
    # The words themselves are never printed.
    assert not found, f"private names in: {found}"


def test_no_private_names_in_the_commits(names):
    # Author and committer names and e-mails, and messages, of every commit
    # on this branch that is not on the remote's main yet.
    log = git(
        "log", "--format=%an%n%ae%n%cn%n%ce%n%B", "HEAD", "--not", "--remotes"
    )
    assert not private_words(log, names), "a commit names a private name"
