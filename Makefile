# The quality gate. `check` is for a developer's terminal and may rewrite
# files; `ci` only verifies, and .github/workflows/check.yml runs its
# targets one per step, in this order, so the pipeline and a terminal
# cannot drift into checking different things.
#
# Every tool runs at an exact version through `uvx`, so nothing here needs
# a virtualenv or a global install, only `uv` (one binary). A pin moves in
# a `dependencies` pull request, like any other dependency. The app's own
# targets (install, fmt, lint, types, build) arrive with the app's stack.
.PHONY: test security workflows check ci clean

# Tool versions, spelled once. UV_EXCLUDE_NEWER resolves everything uvx
# installs, the tools' own dependencies included, as of that date, so a
# run is reproducible and nothing younger than the cooldown gets in. It
# moves with the pins, by hand, in a `dependencies` pull request: at least
# 7 days before the day it is set, and after every pinned release.
# Dependabot cannot see these pins.
PYTEST_VERSION = 9.2.0
SEMGREP_VERSION = 1.185.0
ZIZMOR_VERSION = 1.32.0
export UV_EXCLUDE_NEWER = 2026-11-17T00:00:00Z

# The repository's own tests: the agent harness hooks and the repository's
# structure (tests/harness). Caches go under .cache/, like every tool's.
PYTEST = uvx --from pytest==$(PYTEST_VERSION) pytest \
	-o pythonpath=.claude/hooks \
	-o cache_dir=.cache/pytest \
	-p no:legacypath \
	tests

# Static analysis, blocking (`--error`). The rule packs come from the
# registry at run time, unpinned (SECURITY.md, "Known limits"). Add the
# app's directories and packs (p/javascript, p/typescript) when it lands.
SEMGREP = XDG_CONFIG_HOME=$(CURDIR)/.cache \
	uvx --from semgrep==$(SEMGREP_VERSION) semgrep scan \
	--config=p/python \
	--config=p/secrets \
	--config=p/security-audit \
	--config=p/cwe-top-25 \
	--config=p/owasp-top-ten \
	--config=p/ci \
	--metrics=off \
	--error \
	.github .claude .agents tests

# GitHub Actions workflows and dependabot.yml, audited for the supply-chain
# mistakes semgrep does not model (template injection, excessive
# permissions, unpinned actions, credential persistence). Online audits run
# when GH_TOKEN is set (CI sets it); without it, offline ones only.
ZIZMOR = uvx --from zizmor==$(ZIZMOR_VERSION) zizmor --persona regular .

test:
	$(PYTEST)

security:
	$(SEMGREP)

workflows:
	$(ZIZMOR)

check: test security workflows

ci: test security workflows

clean:
	rm -rf .cache
