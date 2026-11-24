## What and why

<!--
One paragraph. The diff says what changed; say why. Link the issue it
closes, one closing word per issue: "Closes #12, closes #15".
-->

Closes #

## Verification

<!--
`make ci`, and which tests were added or changed. A visible change: how it
was looked at (a screenshot, the CrateDB version it ran against). Anything
manual: the steps.
-->

## Security impact

<!--
One line. "None of these" is a valid answer, but it has to be given:
workflows, the agent harness (.claude/, .agents/, Makefile), dependencies,
how CrateDB credentials are handled, SQL the app builds, rendering data
from the database, calls to anything other than the user's CrateDB.
See SECURITY.md, "What makes a change security-relevant".
-->

## AI assistance

<!--
"None", or: the tool and model; what it generated and what you changed by
hand; where the reviewer should look closest. Generated code is reviewed
against the issue, against APIs and packages that exist in our versions,
for security and error handling, and for tests that fail without the
change. A Co-Authored-By trailer on the commits says which ones.
-->

## Checklist

- [ ] `make ci` passes locally
- [ ] Title in Conventional Commits form (`feat(console): ...`): it becomes the release-notes line
- [ ] Version bumped, if release-relevant (the `release-management` skill)
- [ ] Docs updated, if behaviour changed (English and Portuguese)

<!--
Maintainers: add the Portuguese section below (AGENTS.md, "Language").
Contributors: optional; write in English or Portuguese, either is welcome.
-->

## Português (pt-BR)

### O que e por quê

### Verificação

### Impacto de segurança

### Assistência de IA
