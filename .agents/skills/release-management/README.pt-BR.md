# Gestão de releases

[English](SKILL.md) · **Português**

> Tradução para leitura. O agente carrega a versão em inglês, que é a referência: se as duas divergirem, vale o inglês.

**Quando usar:** ao decidir se uma mudança no cratedeck incrementa a versão e em quanto, ao preparar uma release, ou ao explicar o que um merge na main faz e o que não faz.

## O que um merge na `main` faz

O `create_release.yml` roda no push que o merge produz. Ele lê a versão
(`version` em `package.json`, ou `project.version` em `pyproject.toml`):

- **Sem arquivo de versão** (antes de o app existir): nada; um aviso diz
  isso.
- **`v<version>` já existe**: nada. O merge não incrementou a versão, então
  não é uma release.
- **Uma versão nova**: `gh release create v<version> --generate-notes`, com
  o SBOM CycloneDX das dependências de produção anexado; sem um lockfile
  para gerá-lo, a execução falha em vez de publicar sem ele. Uma versão com
  sufixo de pré-release (`0.3.0-rc.1`) é marcada como pré-release.

As notas são geradas a partir dos títulos dos pull requests que entraram,
agrupados pelos seus labels (`.github/release.yml`). Ninguém as escreve à
mão, e é por isso que o título e o label de cada pull request importam.

## Versionamento

SemVer, lido do ponto de vista de quem roda o cratedeck contra o próprio
cluster. Incremente **na branch**, antes do pull request.

| Mudança | Incremento |
| --- | --- |
| Uma tela ou um fluxo removido que os usuários precisam reaprender; uma versão do CrateDB que deixa de ser suportada; uma configuração ou opção de deploy que muda de significado | **major** (e o label `breaking-change`). Antes da 1.0, um minor. |
| Uma tela, funcionalidade ou configuração nova, ou uma versão do CrateDB recém-suportada | **minor** |
| Uma correção; uma atualização de dependência que chega aos usuários | **patch** |
| Só documentação, o harness de agentes (`.claude/`, `.agents/`), workflows, testes | **nenhum** |

Uma breaking change também leva o label `breaking-change`, seja qual for o
número. As release notes a colocam em uma seção própria.

## Checklist antes do merge

1. O gate verde no pull request (`check`, `pr-title`).
2. O pull request com label.
3. A versão decidida e, quando relevante para a release, commitada.
4. O CHANGELOG são as release notes: não há mais nada a atualizar.

## Depois de um merge na `main`

Confirme o resultado: `gh release list --limit 3` quando a versão mudou, ou
o aviso em `gh run list --workflow create_release.yml --limit 1` caso
contrário. Uma execução que falhou deixa a `main` à frente da sua última
release sem nenhum erro visível, a menos que alguém vá olhar.

## Pegadinhas

- O `fetch-depth: 0` no `create_release.yml` é essencial: um checkout raso
  não tem tags, então todo merge pareceria uma versão nova.
- Tags `v*` não podem ser movidas nem excluídas (o ruleset `release-tags`),
  e as releases são imutáveis depois de publicadas. Uma release ruim se
  corrige com uma versão nova, não editando a antiga.
- A release roda em `push`, não em `pull_request: closed`: um pull request
  de fork que entrou ainda roda com um token somente leitura e não
  conseguiria criar a tag.
