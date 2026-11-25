**English** · [Português](README.pt-BR.md)

<h1 align="center">cratedeck</h1>

<p align="center">
  <em>A modern, self-hosted admin UI for CrateDB</em>
</p>

<p align="center">
  <a href="https://github.com/glaucolauria/cratedeck/actions/workflows/check.yml"><img src="https://github.com/glaucolauria/cratedeck/actions/workflows/check.yml/badge.svg" alt="check"></a>
  <a href="https://scorecard.dev/viewer/?uri=github.com/glaucolauria/cratedeck"><img src="https://api.scorecard.dev/projects/github.com/glaucolauria/cratedeck/badge" alt="OpenSSF Scorecard"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/glaucolauria/cratedeck" alt="License: Apache-2.0"></a>
  <img src="https://img.shields.io/badge/status-pre--alpha-orange" alt="Status: pre-alpha">
</p>

cratedeck is an admin UI for [CrateDB](https://cratedb.com) clusters you run
yourself: a browser application that connects to your cluster to inspect
it, query it and administer it, with nothing in between and nothing sent
anywhere else.

> **Status: pre-alpha.** The repository is being set up; there is no app to
> run yet. Watch the repository, or join
> [Discussions](https://github.com/glaucolauria/cratedeck/discussions) to
> say what you need from it.

## Why

CrateDB ships with a built-in admin UI that works for querying, but its
development has slowed, and features operators reach for every day are
missing. cratedeck is a fresh start, built from scratch, kept up to date and
patched, and open to contributions.

## What it will do

The first scope is still being defined in the open. The candidates:

- **Console:** SQL with highlighting and completion, several tabs, history,
  cancelling a running query.
- **Cluster:** nodes, load, heap and disk, health checks, running jobs.
- **Tables:** schemas, sizes, partitions and shards, including where shards
  are and why some are not allocated.
- **Users and privileges:** create, alter, grant and revoke without
  writing the SQL by hand.
- **Snapshots:** repositories, snapshots and restores.

## Principles

- **Your cluster only.** The browser talks to the cluster you configure and
  to nothing else: no telemetry, no CDN, no external fonts.
- **Secure by default.** Data from the database is shown as text, and
  credentials are never stored where you did not choose. See
  [SECURITY.md](SECURITY.md).
- **Maintained.** Dependencies are updated automatically and every change
  passes the same gate, on amd64 and arm64.

## Contributing

Contributions are welcome, in English or Portuguese: issues, ideas in
Discussions, documentation and code. Start with
[CONTRIBUTING.md](CONTRIBUTING.md). Everyone taking part follows the
[Code of Conduct](CODE_OF_CONDUCT.md). Questions go to
[SUPPORT.md](SUPPORT.md).

If you work with a coding agent (Claude Code, Codex, Cursor, Copilot or
another), it reads [AGENTS.md](AGENTS.md) and the skills in `.agents/skills/`:
the repository's rules and procedures are written for it too
([docs/agent-harness.md](docs/agent-harness.md)).

## Security

Report vulnerabilities privately, never in an issue:
[SECURITY.md](SECURITY.md).

## License

[Apache License 2.0](LICENSE).

CrateDB is a trademark of Crate.io. cratedeck is an independent community
project, not affiliated with, sponsored or endorsed by Crate.io.
