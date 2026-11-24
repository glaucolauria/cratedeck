# cratedeck

[English](AGENTS.md) · **Português**

> Tradução para leitura. O agente carrega a versão em inglês, que é a referência: se as duas divergirem, vale o inglês.

O cratedeck é uma UI de administração moderna e self-hosted para o
[CrateDB](https://cratedb.com): uma aplicação de navegador que fala com o
cluster CrateDB para o qual o usuário a aponta, para inspecioná-lo,
consultá-lo e administrá-lo (nós, tabelas e shards, usuários e privilégios,
snapshots, jobs em execução). É um projeto comunitário independente,
construído do zero, e não afiliado à Crate.io.

O repositório é público e aberto a contribuições. Tudo o que há nele, e
tudo o que se diz nas suas issues e pull requests, é lido por estranhos:
"Repositório público", abaixo, é uma restrição rígida.

**Formato:** aplicação web. **Stack:** ainda não escolhida (abaixo).
**Modelo de estágios:** dois estágios, `dev` → `main`. **Status:** pré-alfa, ainda sem
código do app.

## Antes de toda tarefa

- Leia "Decisões tomadas", abaixo, antes de propor uma mudança de direção.
- As skills carregam sob demanda: `.agents/skills/` (o Claude Code lê a
  mesma pasta pelo link `.claude/skills`). Os agentes estão em
  `.claude/agents/`. O `docs/agent-harness.md` diz o que cada ferramenta
  carrega.
- Uma tarefa que vai mudar o repositório começa por uma issue
  (`issue-hygiene`) e uma branch (`git-workflow`).

## Idioma

Responda ao usuário no idioma em que ele escreve, inglês ou português.
Títulos, código, comentários, commits, branches e labels são em inglês.

- **Documentação para pessoas** (`README`, `CONTRIBUTING`, `SECURITY`,
  `SUPPORT`, `CODE_OF_CONDUCT`, `docs/`): inglês e português, o português
  em uma versão `.pt-BR.md` que aponta de volta para o inglês, alterada no
  mesmo pull request. O inglês é a referência.
- **Instruções para agentes** (este arquivo, skills, agentes): o inglês é o
  que as ferramentas carregam; cada um tem uma versão em português que
  nenhuma ferramenta carrega (`AGENTS.pt-BR.md`, `<skill>/README.pt-BR.md`,
  `.claude/agents.pt-BR/<name>.md`), alterada no mesmo pull request.
- **Corpo de issues e pull requests:** um mantenedor, ou um agente
  trabalhando para um, escreve o inglês e depois uma última seção
  `## Português (pt-BR)` com o mesmo conteúdo. Um contribuidor pode escrever
  em qualquer um dos dois idiomas. Um comentário de revisão de um
  mantenedor: o inglês, uma linha em branco, `**pt-BR:**` e o mesmo em
  português.

O `tests/harness/test_repository.py` falha quando falta uma versão em
português ou quando os títulos dela diferem dos do inglês.

## Repositório público (restrição rígida)

Arquivos, commits (mensagens e e-mails de autor), branches, issues, pull
requests e comentários são todos públicos, e continuam públicos depois do
push.

1. Nunca cite os empregadores, clientes ou projetos privados dos
   mantenedores, nem copie nada deles. A lista desses nomes fica na máquina
   de cada mantenedor, nunca aqui (`~/.config/cratedeck/private-names`, ou
   o arquivo para o qual `CRATEDECK_PRIVATE_NAMES` aponta); os testes
   `test_no_private_names_*` verificam os arquivos e os commits ainda não
   enviados contra ela, e são pulados sem ela. Rode `make ci` antes de todo
   push: depois do push, é público. Nunca leia esse arquivo numa sessão.
2. Faça commits com um endereço `noreply` do GitHub, nunca com um e-mail de
   trabalho: `git config user.email <id>+<login>@users.noreply.github.com`
   no clone. Confira isso antes do primeiro commit.
3. Nenhum dado real em lugar nenhum: nenhum hostname, credencial, tabela ou
   linha de um cluster CrateDB real em código, testes, fixtures, issues,
   pull requests ou capturas de tela. Só dados sintéticos.
4. Uma vulnerabilidade é reportada em privado (`SECURITY.md`), nunca em uma
   issue, um pull request, uma mensagem de commit ou uma discussão.

## Fluxo de estágios (restrição rígida)

Dois estágios. A `dev`, branch padrão, é onde toda mudança entra; a
`main` recebe só a promoção da `dev`. Um merge na `dev` não gera release;
uma promoção que incrementa a versão gera (`create_release.yml`).

1. Nunca faça push para a `dev` nem para a `main`. Só pull requests: o hook
   em `.claude/settings.json` nega o push, e os rulesets o recusam para
   todos (`docs/repository-settings.md`).
2. Todo pull request vai para a `dev`. A `main` recebe um só, vindo da
   `dev`, com merge commit; o check obrigatório `promotion` reprova um pull
   request para a `main` vindo de qualquer outra origem, inclusive depois
   de uma troca de base.
3. Aprovação antes do merge, nos dois estágios. O merge é uma ação do
   mantenedor: um agente nunca faz merge (`gh pr merge` é negado em
   `.claude/settings.json`).
4. Incremente a versão no pull request para a `dev` quando a mudança for
   relevante para uma release; a promoção a carrega (`release-management`).
5. Mantenedores: as branches de tarefa saem da `dev` e entram por merge
   local em `sprint/<topic>`, o gate roda uma vez ali, e um único pull
   request vai para a `dev`. Contribuidores: uma branch no próprio fork, um
   pull request para a `dev` (`git-workflow`).

## Stack

Não escolhida. O primeiro pull request com código do app a registra aqui,
com o motivo de cada escolha, e adiciona os seus targets ao `Makefile` e o
seu ecossistema ao `.github/dependabot.yml`. Seja ela qual for, isto já vale
(`SECURITY.md`, "Design rules for the app"):

- O navegador fala apenas com o cluster CrateDB que o usuário configurou:
  sem telemetria, sem CDN, sem web font ou script vindo de qualquer outro
  lugar.
- Todo valor vindo do banco é renderizado como texto, nunca como HTML.
- Credenciais nunca são gravadas em um armazenamento que o usuário não
  escolheu, nunca vão para log, nunca são postas em uma URL.

## Estrutura

```
AGENTS.md              this file; AGENTS.pt-BR.md is the same for people
.agents/skills/        git-workflow, issue-hygiene, release-management, quality-gate
.claude/agents/        pm, qa, cybersec (agents.pt-BR/: the same for people)
.claude/hooks/         block_protected_push.py and its tokenizer, shell_words.py
.claude/settings.json  permissions (allow/deny) and the push guard
.claude/skills         a link to ../.agents/skills
.github/               workflows/, rulesets/ (as applied), issue forms, PR template,
                       CODEOWNERS, dependabot.yml, release.yml
docs/                  repository-settings, agent-harness (each with .pt-BR.md)
tests/harness/         the hook's tests and the repository's structure checks
```

## Regras

1. **Uma regra vive em um único arquivo.** Este arquivo guarda regras; as
   skills guardam procedimentos; `docs/` guarda o como e o porquê. Quando o
   código e um documento discordam, o código vence e o documento é corrigido
   no mesmo pull request.
2. **Uma regra nomeia o teste que a garante**, quando existe um.
3. **Hooks nunca fazem falhar o comando que observam**, e precisam apenas do
   `python3` do sistema (3.9+) e da biblioteca padrão dele. Eles leem o
   `cwd` do payload, não o próprio diretório de trabalho.
   O `tests/harness/test_block_protected_push.py` cobre a trava.
4. **Workflows:** actions fixadas pelo SHA completo do commit, consultado
   com `gh api` e nunca digitado de memória, com a versão em um comentário
   ao final da linha; `permissions:` de menor privilégio, documentadas
   inline; nada de `pull_request_target`; nada de `${{ }}` com dados do pull
   request dentro de `run:`. O zizmor e o `p/ci` do semgrep garantem isso no
   gate, e o repositório recusa actions não fixadas e actions fora da sua
   allowlist (`docs/repository-settings.md`, "Actions").
5. **Versões exatas de ferramentas, dependências com cooldown.** As
   ferramentas rodam nas versões fixadas no `Makefile`, com as dependências
   delas resolvidas na data do seu `UV_EXCLUDE_NEWER`; uma release de
   dependência com menos de 7 dias não é adotada (essa data, o `cooldown`
   do Dependabot, o gerenciador de pacotes do app quando for escolhido).
6. **O escopo é o da issue.** O trabalho fica dentro dos critérios de aceite
   e do nível de abordagem da sua issue (`issue-hygiene`); qualquer coisa
   além disso é proposta, não feita.
7. **Stage por caminho.** Nunca `git add -A`, `git add .` ou
   `git commit -a`; nomeie os arquivos, e leia o `git diff --cached` antes
   de fazer commit.
8. **Construído do zero.** Nenhum código é copiado de outras UIs de
   administração do CrateDB. As funcionalidades são projetadas a partir da
   leitura da documentação e das tabelas de sistema do CrateDB.

## Decisões tomadas: não reabrir

Registradas para que nenhum agente gaste uma sessão rediscutindo-as. Mudar
uma delas é uma issue própria, aberta por um mantenedor.

- **Do zero** (2026-11-24): nenhum fork, nenhum código de UIs de
  administração do CrateDB existentes.
- **Apache-2.0**, para o código e para as contribuições a ele
  (`CONTRIBUTING.md`).
- **Dois estágios, `dev` → `main`** (2026-11-24). Na `dev`: merge commits
  para os pull requests de sprint dos mantenedores, squash permitido para o
  de um contribuidor. Na `main`: a promoção da `dev`, com merge commit.
- **As atualizações de dependências são automáticas**: atualizações de
  segurança do Dependabot assim que existe um advisory, atualizações de
  versão semanais e agrupadas, com cooldown de 7 dias. Manter o projeto com
  as correções em dia é um objetivo por si só.
- **Documentação bilíngue**, com o inglês como referência ("Idioma").
- **Independente da Crate.io.** "CrateDB" nomeia aquilo com que o cratedeck
  trabalha; o aviso de marca no README permanece.

## Lacunas conhecidas

O que o gate e as configurações ainda não fazem, para que ninguém presuma
que fazem.

- Sem código do app, então sem formatação, linting, checagem de tipos ou
  testes do app: eles chegam com a stack.
- O CodeQL (default setup) analisa a branch padrão, a `dev`: os workflows
  e os hooks em Python. Ele passa a cobrir a linguagem do app quando ela
  chegar à `dev`; confirme isso na aba Security depois do primeiro merge do
  app.
- Os padrões genéricos e as verificações de validade do secret scanning não
  estão disponíveis neste plano: a push protection só conhece tokens de
  provedores, e o `p/secrets` do semgrep mais a revisão cobrem o resto.

## Trabalhando aqui

- Branches, commits, pull requests: `git-workflow`. Issues e labels:
  `issue-hygiene`. Versões e releases: `release-management`. O gate:
  `quality-gate`.
- Agentes: o `pm` orquestra; o `qa` avalia se os testes pegariam a mudança
  caso ela estivesse errada; o `cybersec` revisa com base no `SECURITY.md`.
- Uma mudança em `.github/`, `.claude/`, `.agents/`, no `Makefile`, em
  `tests/harness/` ou em uma dependência precisa de uma nota de segurança no
  pull request e de uma revisão do `cybersec`.

## O quality gate

```bash
make check    # a developer's terminal
make ci       # verifying only; what .github/workflows/check.yml runs
```

## CI/CD

- `check.yml`: o gate nos pull requests para a `dev` e a `main`. O `gate`
  roda `make ci` em amd64 e arm64 (e o build do app, quando ele existir);
  o `check` acrescenta a dependency review e só passa quando todos os jobs
  da matriz passaram. Obrigatório.
- `pr-title.yml`: o título é um título Conventional Commits. Obrigatório.
- `promotion.yml`: um pull request para a `main` vem da `dev` deste
  repositório; roda de novo a cada edição, inclusive uma troca de base.
  Obrigatório na `main`.
- `create_release.yml`: em um push para a `main`, publica a release
  `v<version>` quando a versão é nova, com notas geradas e um SBOM.
- `scorecard.yml`: OpenSSF Scorecard, semanalmente e na `dev`; resultados
  na aba Security e no badge do README.
- O default setup do CodeQL e o Dependabot rodam a partir das configurações
  do repositório e do `.github/dependabot.yml`.
