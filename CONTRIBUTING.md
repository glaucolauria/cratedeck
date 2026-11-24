# Contributing to cratedeck

**English** · [Português](CONTRIBUTING.pt-BR.md)

Thank you for considering it. cratedeck is young, so the most useful
contributions right now are telling us what you need from a CrateDB admin
UI, and, once the app exists, small, well-tested pull requests.

Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md).
Write in English or Portuguese; both are welcome everywhere.

## Ways to contribute

- **Ideas and questions:** [Discussions](https://github.com/glaucolauria/cratedeck/discussions).
- **Bugs and concrete features:** an issue, through one of the forms.
- **Code and documentation:** a pull request, ideally for an issue labelled
  `good first issue` or `help wanted`. For anything larger, comment on the
  issue first so the approach is agreed before the work.
- **Vulnerabilities:** never in public. See [SECURITY.md](SECURITY.md).

## Before you start

- Everything here is public, forever: issues, pull requests, commits and
  their author e-mail. Use your GitHub `noreply` address for commits
  ([GitHub's guide](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address)).
- Never paste credentials, hostnames or data from a real cluster into an
  issue, a test or a screenshot. Reduce the case to synthetic data.
- You need `git`, [`uv`](https://docs.astral.sh/uv/) (it runs every tool of
  the gate at a pinned version) and `make`. The app's own requirements will
  be listed here when it lands.

## Development flow

1. Fork the repository and create a branch:
   `feat/<issue>-<slug>`, `fix/<issue>-<slug>`, `docs/<issue>-<slug>`…
2. Make the change, with the tests that prove it.
3. Run the gate: `make ci`. Pull requests run the same targets on amd64 and
   arm64.
4. Open a pull request into `main` and fill in the template.

The first workflow run of a new contributor waits for a maintainer to
approve it; that is a security setting, not a judgement of your change.

## Commits and pull requests

- **Commits:** [Conventional Commits](https://www.conventionalcommits.org),
  in English: `feat(console): add query history`,
  `fix(tables): quote schema names with dots`. Types: `feat`, `fix`,
  `chore`, `refactor`, `docs`, `test`, `ci`, `build`, `perf`, `revert`.
- **Pull request title:** the same form. It becomes the line in the release
  notes, and a check fails until it fits.
- **Pull request body:** what and why, how you verified it, the security
  impact (one line, even "none"), and whether an AI tool helped. The
  Portuguese section of the template is for maintainers; skip it if you
  like.
- **AI assistance** is welcome and disclosed: say which tool, what it
  generated and what you checked. A `Co-Authored-By:` trailer on the
  commits names the tool.
- **One concern per pull request.** Unrelated refactors or formatting go in
  a separate one.

## Review and merge

A maintainer reviews every pull request; the code owner's approval and a
green gate are required to merge. A pull request may be merged with a merge
commit or squashed into one commit titled after the pull request.

Changes to `.github/`, `.claude/`, `.agents/`, the `Makefile` or
`tests/harness/` run in CI or on the maintainers' machines, so they get a
closer review and a written security note. Expect questions.

## Documentation

User-facing documentation is written in English and Portuguese (a
`.pt-BR.md` file next to the English). If you write only one of them, say so
in the pull request and a maintainer will add the other.

## License

cratedeck is licensed under the [Apache License 2.0](LICENSE). By
submitting a contribution you agree that it is licensed under the same
terms (section 5 of the license). Only submit work you have the right to
license this way, and do not copy code from other projects, including
other CrateDB admin UIs: cratedeck is written from scratch.
