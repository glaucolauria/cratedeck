# Fluxo de git

[English](SKILL.md) · **Português**

> Tradução para leitura. O agente carrega a versão em inglês, que é a referência: se as duas divergirem, vale o inglês.

**Quando usar:** sempre que começar o desenvolvimento de uma tarefa no cratedeck, criar branches, commits ou pull requests, ou entregar o trabalho concluído. Nomes de branch, formato de commit, a branch de sprint, o relatório de entrega e a pergunta sobre o próximo passo antes de um pull request, a promoção da dev para a main, e o que faz um merge em cada estágio.

As regras estão no `AGENTS.md` ("Public repository", "Stage flow"); isto
aqui é o procedimento. Não deduza o processo a partir dos nomes de branch
que já estão no histórico.

## O modelo de estágios

Dois estágios. A `dev`, branch padrão, recebe todo pull request; a `main`
recebe só a promoção da `dev`, e uma promoção que incrementa a versão gera
a release (`release-management`).

**Nunca faça push para a `dev` nem para a `main`.** O hook em
`.claude/settings.json` nega um push cujo destino seja `dev`, `main` ou
`master`; os rulesets o recusam para todos, inclusive o mantenedor.

## Antes do primeiro commit em um clone

```bash
git config user.email    # must be <id>+<login>@users.noreply.github.com
```

Se ele mostrar um endereço de trabalho ou pessoal, pare e peça ao usuário
que configure o `noreply` neste clone (`AGENTS.md`, "Public repository").
O e-mail de um commit fica público no momento do push.

Antes de todo push, `make ci` com a lista de nomes privados do mantenedor
no lugar: ela verifica os commits ainda não enviados e os arquivos em busca
de nomes que nunca podem ser publicados. Se os dois testes
`test_no_private_names_*` foram pulados, diga isso e pergunte antes do
push.

## Branches

```
feat/<issue>-<slug>      fix/<issue>-<slug>      chore/<issue>-<slug>
refactor/<issue>-<slug>  docs/<issue>-<slug>     ci/<issue>-<slug>
sprint/<topic>           a maintainer's integration branch for several task branches
```

- **Um mantenedor** cria a branch a partir da `dev`. As branches de tarefa
  entram por merge em `sprint/<topic>` **localmente** (um merge local não
  roda CI); o `make ci` roda uma vez ali; `qa` e `cybersec` revisam o diff
  consolidado; um único pull request vai para a `dev`. Uma tarefa isolada
  pode ir direto da sua branch de tarefa para um pull request.
- **Um contribuidor** trabalha em uma branch do seu fork, criada a partir
  da `dev`, e abre o pull request a partir dela para a `dev`.

Em cada branch de tarefa, rode só o que é rápido e relevante; o gate
completo roda uma vez, na branch que vira o pull request. Uma branch morre
com o seu pull request (`delete_branch_on_merge`).

## Commits

Conventional Commits, em inglês, no imperativo:

```
feat(console): add query history
fix(tables): quote schema names with dots
ci(actions): pin dependency-review-action by sha
```

Tipos: `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `ci`, `build`,
`perf`, `revert`. O corpo diz o *porquê*; o diff já diz o quê. Uma mudança
e o teste que a comprova são um único commit.

- **Stage por caminho** (`AGENTS.md`, regra 7): `git add <files>`, depois
  leia o `git diff --cached`. O `git commit -m` faz commit de tudo o que está
  em stage, inclusive o que um passo anterior deixou ali.
- **O agente faz commits nas branches de tarefa e de sprint**; ele só faz
  push e abre um pull request quando o usuário pede (passo 4 abaixo).
- **Atribuição de IA.** Um commit que um agente escreveu, ou ajudou a
  escrever, termina com o trailer `Co-Authored-By:` da sua ferramenta e do
  seu modelo. Se a ferramenta não o adicionou (`git log -1 --format=%B`) e o
  commit ainda não foi enviado, faça amend com
  `--trailer "Co-Authored-By: <tool> <model> <vendor noreply>"`. Depois do
  push, nunca reescreva o histórico por isso.

## Da tarefa ao pull request

### 1. Antes de programar

Leia os critérios de aceite e a abordagem da issue (`issue-hygiene`). Diga
em uma linha o que será executado para ver a mudança funcionando (o app
contra um contêiner local do CrateDB, quando houver um app), ou que não há
nada para executar (documentação, ferramental).

### 2. Desenvolver

Commits pequenos na branch de tarefa. O gate completo (`quality-gate`) uma
vez na branch que vira o pull request, depois `qa` e `cybersec` no diff
consolidado.

### 3. A entrega

Quando o trabalho estiver pronto e o gate verde, e antes de qualquer pull
request, faça um relatório no chat, no idioma do usuário, nesta ordem:

1. **Veja funcionando.** Um link ou o comando para cada tela ou
   comportamento que a mudança toca. Quando não houver nada para abrir,
   diga isso.
2. **O que foi feito.** De três a seis bullets.
3. **Testes.** O que rodou e o resultado; os testes adicionados ou
   alterados; as linhas alteradas que ficaram sem cobertura, e por quê.
4. **Segurança.** Cada achado do `cybersec` e o que aconteceu com ele:
   corrigido, aceito com o motivo, ou registrado em issue. Sem achados,
   diga isso; se nenhum caminho relevante para a segurança foi tocado
   (`SECURITY.md`), diga isso no lugar.
5. **Sua parte.** Um checklist do que só o usuário pode fazer: olhar uma
   tela, mudar uma configuração, aprovar, fazer merge.

### 4. O próximo passo: pergunte

Com o formulário de múltipla escolha da ferramenta, quando ela tiver um,
senão com uma lista numerada, a resposta recomendada primeiro:

- Fazer push e abrir o pull request (recomendado quando o gate está verde e
  nada em "Sua parte" o impede).
- Fazer push e abri-lo como draft, quando algo em "Sua parte" vem antes.
- Revisar localmente primeiro. O agente espera.
- Outro: o que mudar.

### 5. Depois do pull request

Envie os links: o pull request e a issue. Depois confira o estado final,
não os exit codes: `gh pr view <n> --json closingIssuesReferences,labels,assignees`.

## Pull requests

- **Título** no formato Conventional Commits, em inglês: é a linha nas
  release notes e o título do merge commit na `dev`. O check `pr-title`
  garante isso.
- **Issues fechadas:** uma palavra de fechamento por issue,
  `Closes #12, closes #15`; confirme com `closingIssuesReferences` depois de
  abrir.
- **Corpo:** as seções do template; o corpo de um mantenedor (ou do agente
  dele) termina com a seção `## Português (pt-BR)` completa (`AGENTS.md`,
  "Language"). Curto: ~15–25 linhas por idioma para uma tarefa, ~30–40 para
  uma sprint (citando cada issue que ela fecha). Nunca vazio, nunca o título
  repetido.
- **Impacto de segurança:** uma linha, mesmo que seja "none". Uma mudança
  em um caminho que o `SECURITY.md` lista leva uma nota escrita e uma
  revisão do `cybersec`.
- **Versão:** decidida e, quando relevante para a release, incrementada na
  branch (`release-management`).
- **Label** no pull request (`bug`, `enhancement`, `chore`, `security`,
  `documentation`, `dependencies`, `github_actions`, mais
  `breaking-change`): as release notes são montadas a partir dele.
- `gh pr create --base dev --assignee "@me" --label <type> --title … --body-file …`.

## Promovendo a dev para a main

Só quando o mantenedor pedir: um pull request da `dev` para a `main`, com
a mesma entrega e a mesma pergunta sobre o próximo passo de qualquer outro.

- `gh pr create --base main --head dev --assignee "@me" --label <type> --title … --body-file …`.
  O título diz o que sai: `chore(release): v<version>` quando a versão
  mudou, `chore: promote dev to main` quando não mudou.
- O corpo cita cada pull request e cada issue que ele promove. A versão foi
  incrementada no pull request para a `dev` que precisava disso, nunca
  aqui.
- O check obrigatório `promotion` (`promotion.yml`) reprova um pull
  request para a `main` cuja origem seja qualquer coisa além da `dev` deste
  repositório, e roda de novo quando a base é trocada.

## Merge

O mantenedor faz o merge; um agente nunca faz. Todo pull request, para a
`dev` ou para a `main`, entra como merge commit, com o título do pull
request: squash e rebase estão desligados, no repositório e nos rulesets.
Os commits de um pull request ficam como foram escritos, e a `main` mantém
o histórico da `dev`, então a próxima promoção mostra só o que é novo. Ao
fazer merge do próprio pull request, o mantenedor usa o bypass do ruleset
para a revisão do code owner: o gate e o próprio pull request nunca são
contornados (`docs/repository-settings.md`).
