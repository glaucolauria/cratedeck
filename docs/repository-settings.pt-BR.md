# Configurações do repositório

[English](repository-settings.md) · **Português**

O que está configurado no GitHub para este repositório, por quê, e os
comandos que aplicam e auditam essa configuração. As configurações do GitHub
não ficam no git, então este arquivo é o registro delas: uma mudança de
configuração é um pull request que altera este arquivo, e os comandos abaixo
reproduzem o estado. Aplicado em 2026-11-24.

`R` abaixo é `repos/glaucolauria/cratedeck`.

## Geral

| Configuração | Valor | Por quê |
| --- | --- | --- |
| Descrição, topics | definidos | encontrabilidade |
| Branch padrão | `dev` | todo pull request entra ali; o Dependabot e as palavras de fechamento (`Closes #12`) agem na branch padrão |
| Issues, Discussions | ativados | issues para o trabalho, Discussions para perguntas e ideias |
| Wiki, Projects | desativados | a documentação fica no repositório, o trabalho nas issues |
| Merge commits | ativado | o pull request de sprint de um mantenedor mantém os commits das tarefas |
| Squash merging | ativado | o pull request de um contribuidor vira um commit com o título dele |
| Rebase merging | desativado | |
| Título do commit no merge e no squash | o título do pull request | a `dev` e a `main` se leem como as release notes |
| Delete head branches | ativado | uma branch morre com o seu pull request |
| Auto-merge | desativado | um mantenedor faz o merge, à mão |
| Suggest updating branches | ativado | |

```bash
# The stage branches: dev starts as a copy of main, then becomes the default.
gh api -X POST $R/git/refs -f ref=refs/heads/dev \
  -f sha="$(gh api $R/git/ref/heads/main --jq .object.sha)"
gh api -X PATCH $R -f default_branch=dev \
  -F has_wiki=false -F has_projects=false -F has_discussions=true -F has_issues=true \
  -F allow_merge_commit=true -F allow_squash_merge=true -F allow_rebase_merge=false \
  -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=COMMIT_MESSAGES \
  -f merge_commit_title=PR_TITLE -f merge_commit_message=PR_BODY \
  -F delete_branch_on_merge=true -F allow_auto_merge=false -F allow_update_branch=true
gh api -X PUT $R/topics -f 'names[]=cratedb' -f 'names[]=admin-ui' \
  -f 'names[]=database-admin' -f 'names[]=sql' -f 'names[]=sql-console' \
  -f 'names[]=self-hosted' -f 'names[]=database-tools'
```

## Rulesets

Os rulesets, como foram aplicados, estão em `.github/rulesets/`. Rulesets, em
vez da proteção de branch clássica, porque dois deles podem ser combinados:
um que ninguém contorna, e um que só o admin pode contornar, em um pull
request.

| Ruleset | Alvo | Regras | Bypass |
| --- | --- | --- | --- |
| `dev` | `refs/heads/dev` | sem exclusão, sem force push; um pull request é obrigatório (merge ou squash); `check` e `pr-title` precisam passar, vindos do GitHub Actions | **ninguém** |
| `main` | `refs/heads/main` | o mesmo, só merge commits, e o `promotion` também precisa passar | **ninguém** |
| `code-owner-review` | `dev` e `main` | uma aprovação, de um code owner; aprovações desatualizadas descartadas; o último push aprovado por alguém que não o seu autor; conversas resolvidas | admin do repositório, **só para pull requests** |
| `release-tags` | tags `v*` | sem exclusão, sem atualização, sem force push (a criação é permitida) | **ninguém**; numa emergência o ruleset é desativado, o que o log de auditoria registra |

- Os rulesets nomeiam as suas branches em vez de `~DEFAULT_BRANCH`: a
  branch padrão é a `dev`, e a `main` precisa continuar protegida seja
  qual for a padrão (`tests/harness/test_repository.py`).
- O pull request de um contribuidor precisa da aprovação do mantenedor, do
  gate verde e de um pull request; nada mais chega à `dev`.
- A `main` recebe só a promoção da `dev`. O `promotion` (`promotion.yml`)
  reprova um pull request para a `main` vindo de qualquer outra origem, e
  roda de novo quando a base de um pull request é trocada, para que um
  resultado verde de uma execução contra a `dev` não seja aproveitado. Só
  merge commits, então a `main` mantém o histórico da `dev` e a próxima
  promoção mostra só o que é novo.
- O mantenedor não pode aprovar o próprio pull request, então faz o merge
  pelo bypass do `code-owner-review`, que o botão de merge oferece
  explicitamente e os insights do ruleset registram. O ruleset `main`
  continua valendo: o pull request e o gate nunca são pulados.
- `check` é o job agregador do `check.yml`, para que os jobs da matriz do
  gate possam mudar sem mexer no ruleset. Renomear `check` ou `pr-title`
  bloqueia todo pull request até o ruleset acompanhar.

```bash
for f in dev main code-owner-review release-tags; do
  gh api -X POST $R/rulesets --input .github/rulesets/$f.json
done
# To change one: gh api -X PUT $R/rulesets/<id> --input .github/rulesets/<name>.json
```

**Depois que o CodeQL tiver analisado a `dev` uma vez**, adicione uma regra
de code scanning aos rulesets `dev` e `main`, para que um pull request que
introduz um alerta de severidade alta não possa entrar:

```json
{ "type": "code_scanning", "parameters": { "code_scanning_tools": [
  { "tool": "CodeQL", "security_alerts_threshold": "high_or_higher", "alerts_threshold": "errors" } ] } }
```

## Segurança e análise

| Recurso | Estado |
| --- | --- |
| Reporte privado de vulnerabilidades | ativado: os reportes chegam como rascunhos de advisory |
| Dependency graph, alertas do Dependabot | ativados |
| Atualizações de segurança do Dependabot | ativadas: um pull request assim que um advisory tem correção |
| Atualizações de versão do Dependabot | `.github/dependabot.yml`: semanais, agrupadas, cooldown de 7 dias |
| Secret scanning, push protection | ativados |
| Secret scanning: padrões genéricos, verificações de validade | não disponíveis neste plano (`SECURITY.md`, "Known limits") |
| CodeQL | default setup, suíte de queries estendida; analisa as linguagens que a branch padrão, a `dev`, tem |
| OpenSSF Scorecard | `.github/workflows/scorecard.yml` |
| Releases imutáveis | ativado: depois de publicada, os assets e a tag de uma release não podem mudar |

```bash
gh api -X PUT $R/vulnerability-alerts
gh api -X PUT $R/automated-security-fixes
gh api -X PUT $R/private-vulnerability-reporting
echo '{"security_and_analysis":{"secret_scanning":{"status":"enabled"},
  "secret_scanning_push_protection":{"status":"enabled"}}}' | gh api -X PATCH $R --input -
gh api -X PATCH $R/code-scanning/default-setup -f state=configured -f query_suite=extended
gh api -X PUT $R/immutable-releases
```

## Actions

| Configuração | Valor | Por quê |
| --- | --- | --- |
| Actions permitidas | as do próprio GitHub (`actions/*`, `github/*`) mais `astral-sh/setup-uv@*` e `ossf/scorecard-action@*` | uma action de terceiros é código com acesso à execução; adicionar uma é uma mudança revisada nesta lista |
| Exigir actions fixadas por SHA completo | ativado | uma tag pode ser movida por quem controla o repositório da action |
| `GITHUB_TOKEN` padrão | somente leitura; o Actions não pode aprovar pull requests | cada job pede o que precisa, documentado inline |
| Workflows de pull requests de fork | aprovação exigida para todo contribuidor externo | uma primeira execução vinda de um desconhecido não roda até um mantenedor tê-la lido |

```bash
echo '{"enabled":true,"allowed_actions":"selected","sha_pinning_required":true}' \
  | gh api -X PUT $R/actions/permissions --input -
echo '{"github_owned_allowed":true,"verified_allowed":false,
  "patterns_allowed":["astral-sh/setup-uv@*","ossf/scorecard-action@*"]}' \
  | gh api -X PUT $R/actions/permissions/selected-actions --input -
gh api -X PUT $R/actions/permissions/workflow \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=false
gh api -X PUT $R/actions/permissions/fork-pr-contributor-approval \
  -f approval_policy=all_external_contributors
```

Um workflow que precise de uma nova action de terceiros: adicione-a a
`patterns_allowed` no mesmo pull request, neste arquivo, e diga por quê.

## Labels

O conjunto que o `issue-hygiene` descreve: os padrões do GitHub mais
`chore`, `security`, `dependencies`, `github_actions`, `breaking-change` e
`triage`.

```bash
gh label create chore --color c5def5 --description "Tooling, process or maintenance" --force
# … one line per label; `gh label list` shows them all.
```

## Configurado à mão (sem API)

- **Imagem de social preview:** Settings → General → Social preview.
- **Conteúdo denunciado:** Settings → Moderation options → Reported
  content → aceitar denúncias de todos os usuários, para que o canal de
  denúncia do Código de Conduta chegue aos mantenedores.
- **E-mails de alertas de segurança:** Watch → Custom → Security alerts, na
  conta do mantenedor.

## Auditoria

Somente leitura; compare a saída com as tabelas acima.

```bash
gh api $R --jq '{default_branch, has_wiki, has_projects, has_discussions, allow_merge_commit,
  allow_squash_merge, allow_rebase_merge, delete_branch_on_merge, allow_auto_merge,
  security: .security_and_analysis}'
gh api $R/rulesets --jq '.[] | {id, name, enforcement}'
for id in $(gh api $R/rulesets --jq '.[].id'); do
  gh api $R/rulesets/$id --jq '{name, bypass: .bypass_actors, rules: [.rules[].type]}'
done
gh api $R/actions/permissions
gh api $R/actions/permissions/selected-actions
gh api $R/actions/permissions/workflow
gh api $R/actions/permissions/fork-pr-contributor-approval
gh api $R/code-scanning/default-setup --jq '{state, languages, query_suite}'
gh api $R/private-vulnerability-reporting
gh api $R/immutable-releases
gh api $R/vulnerability-alerts -i 2>&1 | head -1        # 204 = on
gh api $R/automated-security-fixes --jq .enabled          # true
```
