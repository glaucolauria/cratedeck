# Política de segurança

[English](SECURITY.md) · **Português**

O cratedeck é uma UI de administração para o CrateDB: quem o executa dá a
ele acesso a um cluster de banco de dados, normalmente com privilégios
administrativos. Um defeito aqui pode alcançar os dados desse cluster e os
seus usuários e, pela automação do repositório, as máquinas das pessoas que
o mantêm. Esta política diz como reportar uma vulnerabilidade, o que o
projeto trata como relevante para a segurança, e quais proteções existem e
quais não existem.

## Versões suportadas

O cratedeck está em pré-alfa e ainda não tem release. Quando tiver, as
correções entram na `main` e saem na release seguinte; a versão suportada é
a última release. Não há backport para releases anteriores.

## Como reportar uma vulnerabilidade

**Reporte em privado. Não abra uma issue, um pull request ou uma discussão**
descrevendo um defeito explorável: tudo ali é público.

Use o reporte privado de vulnerabilidades do GitHub:
[Security → Report a vulnerability](https://github.com/glaucolauria/cratedeck/security/advisories/new).
Só os mantenedores veem o reporte. Escreva em inglês ou português, e inclua
o que é afetado, as versões do cratedeck e do CrateDB, os passos para
reproduzir e o acesso de que um atacante precisa. Nunca teste contra um
cluster que não é seu.

O que acontece depois:

- Uma confirmação de recebimento em até 7 dias.
- Uma avaliação, e um plano ou uma correção, tão logo a severidade exija.
  A correção passa por um pull request normal que nomeia o que fecha sem os
  passos para explorar.
- Um advisory publicado, com crédito a quem reportou, a menos que a pessoa
  prefira outra coisa. Não há bug bounty.

## O que torna uma mudança relevante para a segurança

Qualquer um destes itens exige uma nota de segurança escrita no pull request
(o risco, o que foi verificado, o que não foi), um teste de caminho negativo
quando possível, e uma revisão do agente `cybersec` e de um mantenedor antes
do merge:

- Qualquer coisa em `.github/`: workflows, `dependabot.yml`, `CODEOWNERS`,
  os rulesets. Mudanças de workflow são mudanças de segurança.
- O harness de agentes: `.claude/` (settings e hooks), `.agents/`, o
  `Makefile` e `tests/harness/`. Eles executam na máquina de um mantenedor
  quando uma branch é baixada e trabalhada.
- Uma dependência adicionada, removida ou atualizada.
- No app, quando ele existir: como as credenciais do CrateDB são informadas,
  mantidas, enviadas e esquecidas; o SQL que o próprio app monta; como os
  dados do banco são renderizados; qualquer requisição de rede; como o app é
  servido e configurado (headers, orientações de CORS, a imagem de
  contêiner).

## Regras de design do app

Valem desde a primeira linha de código do app, e uma mudança que quebra uma
delas é uma vulnerabilidade, não uma funcionalidade:

1. **Só o cluster configurado.** O navegador fala com o cluster CrateDB que
   o usuário configurou e com nada mais: sem telemetria, sem CDN, sem web
   font, sem verificação de atualização. Tudo de que o app precisa está no
   build dele.
2. **Dado é texto.** Todo valor vindo do banco (linhas, nomes, mensagens,
   texto de erro) é renderizado como texto, nunca como HTML.
3. **Identificadores entre aspas, valores com bind.** O SQL do próprio
   usuário é enviado como foi escrito, por design. O SQL que o app monta a
   partir de nomes que leu (schemas, tabelas, colunas, usuários) coloca cada
   identificador entre aspas e passa cada valor como parâmetro.
4. **Credenciais ficam onde estão.** Nunca em log, nunca em uma URL, nunca
   gravadas em um armazenamento que o usuário não escolheu, nunca enviadas a
   nada além do cluster configurado.
5. **Menor privilégio na documentação.** As orientações de configuração
   nunca recomendam uma origem CORS curinga junto com credenciais, nem um
   superusuário onde um usuário mais restrito serviria.

## Controles em vigor

- **Rulesets de branch na `main`.** Um pull request é obrigatório e o gate
  (`check`, `pr-title`) precisa passar, para todos, inclusive o mantenedor;
  force pushes e exclusão são bloqueados. A aprovação de um code owner é
  exigida, e só um admin do repositório pode contornar essa aprovação, e
  apenas em um pull request (`docs/repository-settings.md`).
- **Releases são imutáveis.** Tags `v*` não podem ser movidas nem
  excluídas, por ninguém, e os assets de uma release publicada não podem
  ser substituídos.
- **Análise estática no gate.** semgrep com `--error`
  (`p/python`, `p/secrets`, `p/security-audit`, `p/cwe-top-25`,
  `p/owasp-top-ten`, `p/ci`), zizmor sobre os workflows, e CodeQL
  (default setup) na `main` e em todo pull request.
- **Cadeia de suprimentos dos workflows.** Actions fixadas pelo SHA completo
  do commit, exigido pela configuração do repositório; só as actions do
  próprio GitHub e uma allowlist explícita podem rodar; `GITHUB_TOKEN`
  somente leitura por padrão e ampliado por job, com um comentário; nenhum
  workflow usa `pull_request_target`; execuções de workflow de
  contribuidores de primeira vez e externos esperam a aprovação de um
  mantenedor.
- **Secrets.** Secret scanning e push protection estão ativos. Nenhum
  workflow guarda um secret próprio do repositório.
- **Dependências.** Os alertas e as atualizações de segurança do Dependabot
  estão ativos; as atualizações de versão vêm semanalmente, agrupadas, com
  cooldown de 7 dias. A dependency review do gate recusa uma nova
  dependência, em qualquer escopo, com advisory conhecido de severidade
  moderada ou pior, ou sob uma licença fora da sua allowlist de licenças
  permissivas. As ferramentas do próprio gate são fixadas, com as
  dependências delas resolvidas numa data fixa de pelo menos 7 dias atrás.
- **Toda release traz um SBOM** (CycloneDX), anexado pelo
  `create_release.yml`; sem um lockfile para gerá-lo, não há release.
- **O OpenSSF Scorecard** avalia o repositório semanalmente; os resultados
  ficam na aba Security.
- **A trava de push** (`.claude/hooks/block_protected_push.py`) recusa o
  push de um agente para a `main` antes que ele saia da máquina. Uma
  conveniência: os rulesets são a barreira.

## Vulnerabilidades aceitas

Vulnerabilidades conhecidas com as quais o projeto decidiu conviver, cada
uma até a sua data de revisão. Vazio é o estado normal.

| IDs | Pacote e versão | Por que foi aceita | Revisar até |
| --- | --- | --- | --- |
| | | | |

## Exceções de segurança

Uma linha por lugar onde uma verificação de segurança é instruída a não
olhar (um `nosemgrep`, um ignore do zizmor, um controle desligado). O motivo
fica ao lado da supressão; esta tabela acrescenta onde ela foi aprovada e
quando é revista.

| Onde | Regra | Por quê | Aprovada em | Revisar até |
| --- | --- | --- | --- | --- |
| | | | | |

## Limites conhecidos

Declarados para que ninguém presuma uma proteção que não existe.

- **O secret scanning só conhece tokens de provedores.** Padrões genéricos
  (senhas, chaves privadas sem formato conhecido) e verificações de validade
  não estão disponíveis neste plano; o `p/secrets` do semgrep e a revisão
  cobrem esses casos.
- **Um único mantenedor.** A revisão do code owner pode ser contornada pelo
  admin do repositório, em pull requests, para que o mantenedor possa fazer
  merge do próprio trabalho: nesses casos, o gate e a nota de segurança
  escrita são a revisão.
- **A trava de push não é uma barreira.** Ela não vê aliases do git,
  scripts nem refs movidas pela API (`docs/agent-harness.md`).
- **Sem exigência de commits assinados.** Commits não são verificados como
  regra.
- **Alguns pins são invisíveis para a automação.** As ferramentas do gate e
  a data de resolução delas (`Makefile`) e a versão do uv (`check.yml`)
  mudam à mão; o Dependabot não as vê. Os pacotes de regras do semgrep são
  baixados do registry a cada execução, sem fixação.
- **A verificação de nomes privados só roda onde a lista está.** A lista de
  nomes que nunca podem ser publicados fica fora do repositório, então o CI
  não consegue verificá-la: o `make ci` do mantenedor antes de um push é o
  controle.

## Fora do escopo

- A segurança do próprio CrateDB: reporte ao projeto dele.
- Um cluster exposto sem autenticação, ou um deploy do cratedeck acessível
  a pessoas que não deveriam administrar o cluster: isso é configuração do
  operador, embora a documentação não deva incentivá-lo.
- Contas do GitHub comprometidas ou um operador já privilegiado.
