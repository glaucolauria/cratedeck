[English](README.md) · **Português**

<h1 align="center">cratedeck</h1>

<p align="center">
  <em>Uma UI de administração moderna e self-hosted para o CrateDB</em>
</p>

<p align="center">
  <a href="https://github.com/glaucolauria/cratedeck/actions/workflows/check.yml"><img src="https://github.com/glaucolauria/cratedeck/actions/workflows/check.yml/badge.svg" alt="check"></a>
  <a href="https://scorecard.dev/viewer/?uri=github.com/glaucolauria/cratedeck"><img src="https://api.scorecard.dev/projects/github.com/glaucolauria/cratedeck/badge" alt="OpenSSF Scorecard"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/glaucolauria/cratedeck" alt="License: Apache-2.0"></a>
  <img src="https://img.shields.io/badge/status-pre--alpha-orange" alt="Status: pre-alpha">
</p>

O cratedeck é uma UI de administração para clusters [CrateDB](https://cratedb.com)
que você mesmo opera: uma aplicação de navegador que se conecta ao seu
cluster para inspecioná-lo, consultá-lo e administrá-lo, sem nada no meio e
sem enviar nada para nenhum outro lugar.

> **Status: pré-alfa.** O repositório está sendo montado; ainda não há app
> para rodar. Acompanhe o repositório, ou entre nas
> [Discussions](https://github.com/glaucolauria/cratedeck/discussions) para
> dizer o que você precisa dele.

## Por quê

O CrateDB vem com uma UI de administração embutida que funciona para
consultas, mas o desenvolvimento dela desacelerou, e faltam recursos que
operadores usam todo dia. O cratedeck é um recomeço, construído do zero,
mantido em dia e com as correções aplicadas, e aberto a contribuições.

## O que ele vai fazer

O primeiro escopo ainda está sendo definido em público. Os candidatos:

- **Console:** SQL com destaque de sintaxe e autocompletar, várias abas,
  histórico, cancelamento de uma query em execução.
- **Cluster:** nós, carga, heap e disco, health checks, jobs em execução.
- **Tabelas:** schemas, tamanhos, partições e shards, incluindo onde os
  shards estão e por que alguns não foram alocados.
- **Usuários e privilégios:** criar, alterar, conceder e revogar sem
  escrever o SQL à mão.
- **Snapshots:** repositórios, snapshots e restores.

## Princípios

- **Só o seu cluster.** O navegador fala com o cluster que você configura e
  com nada mais: sem telemetria, sem CDN, sem fontes externas.
- **Seguro por padrão.** Os dados do banco são exibidos como texto, e
  credenciais nunca são guardadas onde você não escolheu. Veja o
  [SECURITY.pt-BR.md](SECURITY.pt-BR.md).
- **Mantido.** As dependências são atualizadas automaticamente e toda
  mudança passa pelo mesmo gate, em amd64 e arm64.

## Contribuindo

Contribuições são bem-vindas, em inglês ou português: issues, ideias nas
Discussions, documentação e código. Comece pelo
[CONTRIBUTING.pt-BR.md](CONTRIBUTING.pt-BR.md). Todos que participam seguem
o [Código de Conduta](CODE_OF_CONDUCT.pt-BR.md). Dúvidas vão para o
[SUPPORT.pt-BR.md](SUPPORT.pt-BR.md).

Se você trabalha com um agente de código (Claude Code, Codex, Cursor,
Copilot ou outro), ele lê o [AGENTS.md](AGENTS.pt-BR.md) e as skills em
`.agents/skills/`: as regras e os procedimentos do repositório também são
escritos para ele ([docs/agent-harness.pt-BR.md](docs/agent-harness.pt-BR.md)).

## Segurança

Reporte vulnerabilidades em privado, nunca em uma issue:
[SECURITY.pt-BR.md](SECURITY.pt-BR.md).

## Licença

[Apache License 2.0](LICENSE).

CrateDB é uma marca comercial da Crate.io. O cratedeck é um projeto
comunitário independente, não afiliado à Crate.io, nem patrocinado ou
endossado por ela.
