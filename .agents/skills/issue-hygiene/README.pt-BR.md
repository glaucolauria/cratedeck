# Higiene de issues

[English](SKILL.md) · **Português**

> Tradução para leitura. O agente carrega a versão em inglês, que é a referência: se as duas divergirem, vale o inglês.

**Quando usar:** no início de uma tarefa ou de um pedido que vai virar código no cratedeck, para propor a issue por um formulário curto e abri-la só com a resposta do usuário; e ao criar, refinar, rotular ou fazer a triagem de issues e pull requests. Contém o formulário de entrada, os níveis de abordagem que limitam quanto o agente projeta, o formato do corpo, os labels e os comandos.

Issues são públicas: o que o `AGENTS.md`, "Public repository", diz sobre
nomes, dados e vulnerabilidades vale para cada palavra delas.

## A entrada: propor, depois abrir

No início de uma tarefa ou de um pedido que vai virar código, **proponha a
issue; abra-a só com a resposta do usuário**. Pule isto para uma pergunta,
uma revisão, ou um pedido que já cita a sua issue.

Primeiro, procure uma que já exista:

```bash
gh issue list --state open --search "<keywords>" --limit 10
```

Depois pergunte, com o formulário de múltipla escolha da ferramenta quando
ela tiver um (senão, uma lista numerada), a resposta recomendada primeiro
em cada pergunta:

**Formulário 1. Criar a issue?**
- Criar "<título convencional, em inglês>" (recomendado).
- Usar a #n "<título>", quando a busca encontrou uma.
- Não criar: o trabalho segue sem issue.
- Outro: um título do próprio usuário.

**Formulário 2. Propriedades**
- **Labels:** o tipo (`enhancement`, `bug`, `chore`, `documentation`),
  mais `security`, `breaking-change`, `good first issue` ou `help wanted`
  quando se aplicarem.
- **Responsável:** o usuário (`@me`), ou ninguém quando a issue for
  destinada a um contribuidor.
- **Milestone:** uma aberta, ou nenhuma (`gh api repos/:owner/:repo/milestones`).

**Formulário 3. Abordagem**
- "Seguir o padrão do repositório" (primeira e recomendada quando o código
  já faz algo parecido), depois Baixa, Média, Alta (abaixo).
- **Sua sugestão:** nenhuma, ou a abordagem que o usuário propõe, em texto
  livre. Ela vai para o corpo, e o agente a segue.

Depois escreva o corpo e abra a issue:

```bash
gh issue create --title "<title>" --body-file <file> \
  --label <type> [--label …] [--assignee @me] [--milestone "<name>"]
```

## A abordagem: quanto projetar antes de programar

O nível decide quanto o agente investe em pensar a solução. **Testes não
fazem parte disso: todo nível é totalmente testado.**

| Abordagem | Fallbacks | Complexidade do código | Padrões de fora |
| --- | --- | --- | --- |
| **Seguir o padrão do repositório** | os que o código já tem | a do código ao redor | nenhum |
| **Baixa** | nenhum além dos critérios de aceite | o mínimo que os atende | nenhum |
| **Média** | as falhas prováveis (rede, um nó inacessível, um timeout, um resultado vazio) | um módulo ou uma abstração local é aceitável | só os que o repositório já usa |
| **Alta** | as prováveis e as raras, citando as que ficarem de fora | o que o design exigir | pesquisar o que ferramentas comparáveis fazem, comparar duas ou três opções, propor o design na issue antes de programar |

- **Quando o trabalho ultrapassa o nível**, pare e pergunte ("isto precisa
  de um retry para X, que a Baixa deixa de fora: passar para Média, ou
  deixar X de fora?"). Nunca aumente a solução por conta própria.
- **O pull request informa a abordagem da issue**, e por que o trabalho foi
  além dela, quando foi.

## O corpo: curto

O pull request traz o detalhe; a issue diz o quê e como saber que está
pronto.

1. O resultado, em uma ou duas frases, e para quem ele é.
2. Os critérios de aceite como checklist.
3. Uma linha: `Approach: <level>`, mais `Suggested: <text>` quando o
   usuário escreveu uma sugestão.
4. Para um bug: as versões do CrateDB e do cratedeck, os passos, o que
   aconteceu, o que era esperado. Reduzido a dados sintéticos.
5. `## Português (pt-BR)` com tudo o que está acima, quando quem abre é um
   mantenedor ou um agente trabalhando para um (`AGENTS.md`, "Language").

Um comentário é raro: uma linha, quando muda algo que a issue não consegue
mostrar (um bloqueio, uma mudança de escopo). O de um mantenedor: o inglês,
uma linha em branco, `**pt-BR:**` e o mesmo em português.

## Labels

| Label | Para |
| --- | --- |
| `bug`, `enhancement`, `chore`, `documentation` | o tipo: toda issue e todo pull request tem um |
| `security` | uma correção ou um hardening; nunca os detalhes de uma vulnerabilidade em aberto |
| `breaking-change` | quebra um fluxo do usuário, uma configuração, ou abandona uma versão do CrateDB |
| `dependencies`, `github_actions` | atualizações de dependências e de workflows (o Dependabot os aplica) |
| `triage` | definido pelos formulários de issue; removido quando um mantenedor já olhou |
| `good first issue`, `help wanted` | abertas a contribuidores: pequenas, bem definidas, com critérios de aceite |
| `question`, `duplicate`, `invalid`, `wontfix` | motivos de fechamento, ou um encaminhamento para as Discussions |

**Rotule o pull request também**: o `.github/release.yml` monta as release
notes a partir dos labels dos pull requests, e um pull request sem label cai
em "Other Changes".

## Triagem (mantenedores)

Para cada issue com `triage`:

1. Reproduzível, dentro do escopo, e não é uma vulnerabilidade? Uma
   vulnerabilidade reportada em público: agradeça a quem reportou, peça que
   use o reporte privado (`SECURITY.md`), e esconda os detalhes (edite, ou
   exclua o comentário).
2. Defina o label de tipo, remova `triage`; adicione `good first issue` ou
   `help wanted` quando um contribuidor puder pegá-la.
3. Uma pergunta ou uma ideia em aberto: encaminhe para as Discussions e
   feche como `question`.

## Dimensionamento

Uma issue, um incremento verificável. Divida o que não cabe em um ciclo
focado. Uma issue guarda-chuva só aponta para as suas sub-issues.

## Comandos

```bash
gh issue view <n> --json title,labels,assignees,milestone,state
gh issue edit <n> --add-label <label> --remove-label triage
gh issue edit <n> --add-assignee @me
gh pr view <n> --json closingIssuesReferences --jq '[.closingIssuesReferences[].number]'
```

Verifique o estado final, não os exit codes.
