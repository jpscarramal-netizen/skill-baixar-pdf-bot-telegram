---
name: baixar-pdf-bot-telegram
description: Baixa PDFs de artigos pelo bot do Telegram @nielsbohr_bot, mandando um DOI por vez pela conta do JP (Telethon) e clicando no botao "PDF" quando ele aparece. Use quando faltarem PDFs depois de tentar editora/Chrome/Scholar, ou quando o JP disser "manda o DOI pro bot", "tenta pelo nielsbohr", "baixa pelo telegram".
---

# Baixar PDF pelo @nielsbohr_bot (Telegram)

O bot recebe um **DOI** e responde com uma mensagem de botoes. Se tiver o artigo, o primeiro botao e
**"⬇️ PDF | tamanho"**; clicando nele, o bot manda o arquivo. Se nao tiver, o primeiro botao e
**"📦 Request (10 - n)"** (pedido ao bot, parece gastar uma cota; **nao clicar sem o JP autorizar**).

Nao existe token de bot aqui: a automacao usa a **conta do Telegram do JP** (Telethon), igual ao
pipeline `telegram-aulas`.

## Quando usar (ordem de tentativa)

1. Rota da editora pelo Chrome/Edge (clique real em "View PDF", ver skill `baixar-artigos-scholar`).
2. Botao [PDF] do Google Scholar.
3. **Este bot**, pelo DOI. Resolveu 7 de 15 pendentes que as outras rotas nao pegaram
   (Neurosurgery, J Neurosurg e AJNR vieram por aqui).

## Passo a passo

### 1. Preparar (uma vez so)

- `pip install telethon pypdf cryptg`
- Credenciais da API do Telegram: https://my.telegram.org > *API development tools* > criar app.
  Anote `api_id` e `api_hash`.
- Uma sessao do Telethon ja logada na conta do JP (arquivo `.session`). No projeto do JP ja existe
  `C:\Users\joaop\Claude contexto\telegram-aulas\sessao_aulas.session`. Se nao existir, logar uma vez
  com `TelegramClient("minha_sessao", api_id, api_hash)` e digitar o codigo que chega no Telegram.
- Definir as variaveis de ambiente (PowerShell):

```powershell
$env:TG_API_ID   = "<api_id>"
$env:TG_API_HASH = "<api_hash>"
$env:TG_SESSION  = "C:\caminho\da\sessao"     # SEM a extensao .session
$env:PYTHONIOENCODING = "utf-8"               # as respostas do bot trazem emoji
```

**Nunca** colocar `api_hash` nem o `.session` no GitHub: a sessao da acesso total a conta.

### 2. Testar com UM DOI

```powershell
python baixar_por_doi.py --saida D:\pdfs 10.1227/neu.0000000000004150
```

Saida esperada: `PDF salvo (741304 B); 11 paginas, DOI confere`. Se vier
`sem PDF no bot (botao: 📦 Request (10 - 1))`, o bot nao tem o artigo.

### 3. Rodar a lista, um DOI por vez

```powershell
python baixar_por_doi.py --saida D:\pdfs --arquivo dois.txt
```

`dois.txt` = um DOI por linha. O script espera ate 30 s a resposta, clica no botao PDF, espera o
arquivo, valida e passa ao proximo com 4 s de pausa. O resumo fica em `D:\pdfs\resultado_bot.json`.

### 4. Validar antes de aceitar (obrigatorio)

O script ja confere, mas **conferir de novo** quando for entregar:

- O **DOI impresso na 1a ou 2a pagina** bate com o do registro.
- **Mais de 100 paginas = livro de resumos**, descartar mesmo que o DOI bata.
- Titulo tambem confere (se o titulo nao bater mas o DOI bater, olhar a primeira pagina a mao).

### 5. Registrar

Renomear para o padrao do projeto e atualizar o manifesto (status baixado/pendente por artigo).
Os que o bot nao tem vao para a lista de pendentes manuais.

## Armadilhas conhecidas

- **Um DOI por vez.** Varios ao mesmo tempo misturam as respostas. O script ja espera cada um.
- **Copiar a sessao** antes de usar (o script faz sozinho): o SQLite da sessao trava se outro script
  estiver aberto com ela. O pipeline `telegram-aulas` usa `receive_updates=False` pelo mesmo motivo.
- **Erro de encoding no terminal** (`charmap ... can't encode '\U0001f4e6'`): faltou
  `PYTHONIOENCODING=utf-8`.
- **Queda de rede no meio** (`WinError 1236/1231`): o Telethon reconecta sozinho; conferir no fim
  o que realmente chegou em disco.
- **"Request" nao e download.** Nao clicar sem o JP dizer que pode gastar a cota.
- Resumo de congresso (suplemento) quase nunca tem PDF completo: nao insistir.

## Arquivos

- `baixar_por_doi.py` — script (sem credenciais; tudo por variavel de ambiente).
