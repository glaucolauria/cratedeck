# Como contribuir com o cratedeck

[English](CONTRIBUTING.md) · **Português**

Obrigado por considerar contribuir. O cratedeck é jovem, então as
contribuições mais úteis agora são nos contar o que você precisa de uma UI
de administração para o CrateDB e, quando o app existir, pull requests
pequenos e bem testados.

Todos que participam seguem o [Código de Conduta](CODE_OF_CONDUCT.pt-BR.md).
Escreva em inglês ou português; os dois são bem-vindos em todo lugar.

## Formas de contribuir

- **Ideias e perguntas:** [Discussions](https://github.com/glaucolauria/cratedeck/discussions).
- **Bugs e funcionalidades concretas:** uma issue, por um dos formulários.
- **Código e documentação:** um pull request, de preferência para uma issue
  com o label `good first issue` ou `help wanted`. Para algo maior, comente
  na issue antes, para que a abordagem seja combinada antes do trabalho.
- **Vulnerabilidades:** nunca em público. Veja o [SECURITY.pt-BR.md](SECURITY.pt-BR.md).

## Antes de começar

- Tudo aqui é público, para sempre: issues, pull requests, commits e o
  e-mail de autor deles. Use o seu endereço `noreply` do GitHub nos commits
  ([guia do GitHub](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address)).
- Nunca cole credenciais, hostnames ou dados de um cluster real em uma
  issue, um teste ou uma captura de tela. Reduza o caso a dados sintéticos.
- Você precisa de `git`, [`uv`](https://docs.astral.sh/uv/) (ele roda cada
  ferramenta do gate em uma versão fixada) e `make`. Os requisitos do
  próprio app serão listados aqui quando ele chegar.

## Fluxo de desenvolvimento

1. Faça um fork do repositório e crie uma branch a partir da `dev`, a
   branch padrão: `feat/<issue>-<slug>`, `fix/<issue>-<slug>`,
   `docs/<issue>-<slug>`…
2. Faça a mudança, com os testes que a comprovam.
3. Rode o gate: `make ci`. Pull requests rodam os mesmos targets em amd64 e
   arm64.
4. Abra um pull request para a `dev` e preencha o template. A `main` guarda
   o que foi lançado e só recebe a `dev`, quando um mantenedor a promove;
   um pull request para a `main` vindo de qualquer outra branch reprova no
   check `promotion`.

A primeira execução de workflow de um novo contribuidor espera um mantenedor
aprová-la; isso é uma configuração de segurança, não um julgamento da sua
mudança.

## Commits e pull requests

- **Commits:** [Conventional Commits](https://www.conventionalcommits.org),
  em inglês: `feat(console): add query history`,
  `fix(tables): quote schema names with dots`. Tipos: `feat`, `fix`,
  `chore`, `refactor`, `docs`, `test`, `ci`, `build`, `perf`, `revert`.
- **Título do pull request:** a mesma forma. Ele vira a linha nas release
  notes, e um check falha até ele se encaixar.
- **Corpo do pull request:** o quê e por quê, como você verificou, o impacto
  de segurança (uma linha, mesmo que seja "nenhum"), e se uma ferramenta de
  IA ajudou. A seção em português do template é para os mantenedores; pule-a
  se quiser.
- **Assistência de IA** é bem-vinda e declarada: diga qual ferramenta, o que
  ela gerou e o que você conferiu. Um trailer `Co-Authored-By:` nos commits
  nomeia a ferramenta.
- **Um assunto por pull request.** Refatorações ou formatação sem relação
  com ele vão em outro.

## Revisão e merge

Um mantenedor revisa todo pull request; a aprovação do code owner e um gate
verde são exigidos para o merge. Um pull request para a `dev` pode entrar
com um merge commit ou com squash em um único commit com o título do pull
request.

Mudanças em `.github/`, `.claude/`, `.agents/`, no `Makefile` ou em
`tests/harness/` rodam no CI ou nas máquinas dos mantenedores, então recebem
uma revisão mais cuidadosa e uma nota de segurança escrita. Espere
perguntas.

## Documentação

A documentação voltada a usuários é escrita em inglês e português (um
arquivo `.pt-BR.md` ao lado do inglês). Se você escrever só uma das duas,
diga isso no pull request e um mantenedor adiciona a outra.

## Licença

O cratedeck é licenciado sob a [Apache License 2.0](LICENSE). Ao enviar uma
contribuição, você concorda que ela é licenciada nos mesmos termos (seção 5
da licença). Só envie trabalho que você tem o direito de licenciar assim, e
não copie código de outros projetos, incluindo outras UIs de administração
do CrateDB: o cratedeck é escrito do zero.
