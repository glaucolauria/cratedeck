# O harness de agentes

[English](agent-harness.md) · **Português**

O cratedeck é desenvolvido com agentes de código, pelo seu mantenedor e,
sejam bem-vindos, por contribuidores. As regras e os procedimentos que eles
seguem estão escritos no repositório, em arquivos que toda ferramenta lê,
para que o resultado seja o mesmo qualquer que seja o agente que a pessoa
usa. Esta página diz que arquivos são esses, qual ferramenta lê o quê, e o
que faz o único hook.

## As peças

| Onde | O quê | Carregado |
| --- | --- | --- |
| `AGENTS.md` | as regras do repositório, declaradas uma única vez | em toda sessão, em toda ferramenta |
| `.agents/skills/<name>/SKILL.md` | procedimentos: `git-workflow`, `issue-hygiene`, `release-management`, `quality-gate` | sob demanda, quando a tarefa corresponde à descrição da skill |
| `.claude/agents/<name>.md` | sub-agentes com uma função restrita: `pm`, `qa`, `cybersec` | sob demanda, nas ferramentas que leem este formato |
| `.claude/hooks/` | a trava de push | antes de cada comando de shell, no Claude Code |
| `.claude/settings.json` | as permissões do Claude Code (allow e deny) e o hook | em toda sessão do Claude Code |

Não há `CLAUDE.md`: o Claude Code lê o `AGENTS.md` quando não existe um, e
um `CLAUDE.md` ou `CLAUDE.local.md` o esconderia. Notas pessoais vão em
`~/.claude/CLAUDE.md`.

Todo arquivo de instrução tem uma versão em português para pessoas
(`AGENTS.pt-BR.md`, `<skill>/README.pt-BR.md`,
`.claude/agents.pt-BR/<name>.md`). Nenhuma ferramenta as carrega, então não
custam tokens; elas mudam no mesmo pull request que o inglês.

## Qual ferramenta lê o quê

| Ferramenta | `AGENTS.md` | Skills | Agentes | Hook e permissões |
| --- | --- | --- | --- | --- |
| Claude Code (CLI, extensões de IDE) | sim | `.claude/skills`, um link para `.agents/skills` | `.claude/agents/` | sim |
| Codex | sim | `.agents/skills/` | não | não |
| Cursor, Gemini CLI, Copilot e outros | sim | `.agents/skills/`, onde a ferramenta suporta skills | não | não |

Uma ferramenta sem o hook perde uma conveniência, não um controle: os
rulesets recusam um push para a `dev` ou a `main` vindo de qualquer pessoa. Uma
ferramenta sem sub-agentes roda as mesmas revisões na sessão principal,
seguindo o arquivo do agente como checklist.

No Windows, o git pode fazer checkout de `.claude/skills` como um arquivo
comum em vez de um link: ative `core.symlinks` (e o Modo de Desenvolvedor),
ou aponte a ferramenta diretamente para `.agents/skills/`.

## A trava de push

`.claude/hooks/block_protected_push.py`, um hook `PreToolUse` no Bash: ele
nega um `git push` cujo destino seja `dev`, `main` ou `master`, onde quer que o
push esteja na linha de comando (depois de `;` ou `&&`, em uma linha
seguinte, atrás de `FOO=1` ou `sudo`, dentro de `sh -c`), com `HEAD` e um
push sem argumentos resolvidos para a branch atual, e `--all` e `--mirror`
recusados. Um destino que ele não consegue ler (`$BRANCH`) é recusado em
vez de adivinhado.

- Ele precisa apenas do `python3` do sistema (3.9+), só com a biblioteca
  padrão, e nunca faz falhar o comando que observa.
- É uma salvaguarda, não uma barreira: não expande aliases do git
  (`git -c alias.p=push p`), não lê scripts nem vê uma ref movida pela API.
  Os rulesets são a barreira.
- `tests/harness/test_block_protected_push.py` nomeia cada forma de comando
  que ele precisa negar e cada uma que precisa deixar passar, incluindo
  esses limites.

## Permissões

O `.claude/settings.json` permite, sem confirmação, alguns comandos somente
leitura exatos (`git status`, `git diff`, `gh pr view`, os targets de gate
do `make`), nunca um prefixo que também aceite uma opção capaz de escrever
um arquivo ou rodar um programa (`git diff --output`,
`git fetch --upload-pack`). Ele nega a leitura de arquivos de segredos
(`.env*`, chaves, `~/.ssh`, `~/.aws`, o token do `gh`, a lista local de
nomes privados), force pushes, `gh pr merge`, `gh repo delete` e
executores de pacotes (`npx`, `npm exec`, `pnpm dlx`, `bunx`). Isso evita
erros; não é um sandbox: um target do `make` roda o que quer que o branch
em checkout contenha.

## Confiança

Ao abrir um clone no Claude Code, você é perguntado se confia na pasta; o
hook e as configurações passam então a valer. **Leia `.claude/`,
`.agents/`, o `Makefile` e `tests/` em um pull request antes de fazer
checkout dele e trabalhar nele com um agente ou rodar `make`**: são
instruções e código que vão rodar com as suas credenciais. O `CODEOWNERS` os coloca sob a revisão do mantenedor pelo
mesmo motivo.

## Alterando o harness

Uma mudança em qualquer um desses arquivos é um pull request como qualquer
outro, com uma nota de segurança (`SECURITY.md`), a sua versão em português,
e `make ci` verde: `tests/harness/test_repository.py` verifica que cada
skill e cada agente tem o seu frontmatter e a sua versão em português com
os mesmos títulos.
