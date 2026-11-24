# Gate de qualidade

[English](SKILL.md) · **Português**

> Tradução para leitura. O agente carrega a versão em inglês, que é a referência: se as duas divergirem, vale o inglês.

**Quando usar:** sempre que for rodar, alterar ou revisar o quality gate do cratedeck, ou escrever testes para ele. Os targets do Makefile, o que o check.yml roda em cada arquitetura, quando rodar o quê, as versões fixadas das ferramentas, as supressões e o checklist de revisão.

O `Makefile` define os comandos e fixa a versão de cada ferramenta; o
`.github/workflows/check.yml` roda os mesmos targets. Quando este arquivo e
eles discordarem, eles vencem, e este arquivo é corrigido.

## Os targets

| Target | Roda | Observações |
| --- | --- | --- |
| `test` | pytest sobre `tests/` | os testes da trava de push e as verificações de estrutura do repositório (`tests/harness`) |
| `security` | semgrep, `--error` | `p/python`, `p/secrets`, `p/security-audit`, `p/cwe-top-25`, `p/owasp-top-ten`, `p/ci` sobre `.github .claude .agents tests` |
| `workflows` | zizmor | os workflows e o `dependabot.yml`; auditorias online quando `GH_TOKEN` está definido |
| `check` | tudo o que está acima | o terminal de um desenvolvedor; pode reescrever arquivos quando existirem formatadores |
| `ci` | o mesmo, só verificando | o que o `check.yml` roda |
| `clean` | remove `.cache/` | |

Toda ferramenta roda via `uvx` na versão exata das variáveis do `Makefile`,
então o único requisito é o `uv`. O `UV_EXCLUDE_NEWER`, exportado pelo
`Makefile`, resolve as dependências das próprias ferramentas numa data fixa:
mover um pin é mover essa data também, para pelo menos 7 dias antes do dia,
num pull request `dependencies`. Caches e relatórios vão para `.cache/`.

**Os targets do app** (`install`, `fmt`, `lint`, `types`, os testes do app,
`build`) chegam com a stack, no mesmo pull request que adiciona o código do
app, junto com os seus steps no `check.yml` e os seus packs em `SEMGREP`.

## No CI

O `check.yml` em todo pull request para a `dev` ou a `main`:

- `gate`, uma matriz sobre `ubuntu-24.04` (amd64) e `ubuntu-24.04-arm`
  (arm64): um step por target do `make ci`, cada um rodando mesmo depois que
  um anterior falhou, para que uma única execução reporte todas as falhas.
  O build do app entra nessa matriz.
- `check`, depois de todos os jobs da matriz: a dependency review (novas
  dependências com advisory de severidade moderada ou pior, ou com uma
  licença incompatível com Apache-2.0), e então falha a menos que todos os
  jobs da matriz tenham passado. O `check` é o status obrigatório nos dois
  estágios.

O `promotion.yml`, em todo pull request para a `main` e a cada edição de
um (inclusive uma troca de base), falha a menos que a origem seja a `dev`
deste repositório. Obrigatório só na `main`.

O `make -k ci` reporta todas as falhas em um terminal, como o gate faz. Uma
falha em uma só arquitetura é exatamente a informação para a qual a matriz
existe: leia o log desse job antes de rodar qualquer coisa de novo, e rode
de novo só os jobs que falharam (`gh run rerun <id> --failed`).

## Quando rodar o quê

```bash
make test        # while changing the hooks or the repository's structure
make workflows   # after touching .github/workflows or dependabot.yml
make ci          # once, on the branch that becomes the pull request
```

## Testes

- Um teste verifica comportamento, não que o código rodou: a decisão do hook
  para um dado comando, um arquivo que a verificação de estrutura exige.
- Uma correção de bug tem um teste de regressão que falha antes da
  correção.
- O `tests/harness/test_block_protected_push.py` lista cada forma de comando
  que a trava precisa negar ou deixar passar; uma forma nova que se descubra
  passando vira primeiro um caso ali.
- O `tests/harness/test_repository.py` guarda a estrutura do repositório:
  versões em português, frontmatter de skills e agentes, actions fixadas por
  SHA, permissões e timeouts dos workflows, os rulesets dos estágios e os
  seus checks obrigatórios, o script que reserva a `main` para a `dev`, e
  nenhum nome privado nos arquivos nem nos commits ainda não enviados
  (contra a lista local do mantenedor, `AGENTS.md`, "Public repository";
  pulado onde ela não existe, como no CI).

## Supressões

Corrija primeiro. Depois, a supressão mais restrita possível, com o motivo
ao lado: `# nosemgrep: <rule-id> <why>`, `# noqa: <code>  # <why>`, um
`# zizmor: ignore[<audit>] <why>` do zizmor. Nunca um disable no arquivo
inteiro por causa de uma linha. Toda supressão também ganha uma linha no
`SECURITY.md`, "Security exceptions", no mesmo pull request.

## Checklist de revisão

1. `make ci` verde, nas duas arquiteturas no CI.
2. Os testes cobrem os caminhos de falha, não só o feliz.
3. Uma mudança relevante para a segurança (`SECURITY.md`) tem um teste
   negativo quando possível, e uma nota escrita.
4. Uma ferramenta nova ou um pin de versão muda na variável do `Makefile`,
   em um pull request com o label `dependencies`.
