# Baixar PDF de artigo pelo bot do Telegram @nielsbohr_bot

Manda um **DOI** para o bot e baixa o PDF automaticamente. Funciona com a **sua própria conta do
Telegram**: cada pessoa cria a sua sessão (passo 2). Não precisa de token de bot nem de nada de
terceiros.

Como o bot responde:

- Tem o artigo → botão **"⬇️ PDF | tamanho"** → o script clica e salva o arquivo.
- Não tem → botão **"📦 Request (10 - n)"**. É um pedido ao bot, parece gastar uma cota sua, então
  o script **nunca** clica nele.

## Passo a passo

### 1. Instalar

```powershell
pip install telethon pypdf cryptg
```

(`cryptg` só acelera; `pypdf` serve para conferir o PDF baixado.)

### 2. Criar a SUA sessão do Telegram (uma vez)

1. Entre em https://my.telegram.org com o seu telefone, abra **API development tools** e crie um
   app (nome e short name podem ser qualquer coisa). Anote o `api_id` e o `api_hash`.
2. No PowerShell:

```powershell
$env:TG_API_ID   = "<seu api_id>"
$env:TG_API_HASH = "<seu api_hash>"
python criar_sessao.py minha_sessao
```

3. Digite o telefone (com `+55...`), o código que chega no app do Telegram e a senha de duas
   etapas, se tiver. Vai aparecer `minha_sessao.session` na pasta.
4. Abra o Telegram uma vez e mande `/start` para `@nielsbohr_bot`, para o chat existir.

> **Segurança:** o `.session` dá acesso total à sua conta. Não compartilhe e não suba no GitHub
> (o `.gitignore` já bloqueia). O `api_hash` também é seu e não deve ser compartilhado.

### 3. Testar com UM DOI

```powershell
$env:TG_API_ID   = "<seu api_id>"
$env:TG_API_HASH = "<seu api_hash>"
$env:TG_SESSION  = "C:\caminho\minha_sessao"     # sem a extensão .session
$env:PYTHONIOENCODING = "utf-8"                  # as respostas do bot trazem emoji
python baixar_por_doi.py --saida .\pdfs 10.1227/neu.0000000000004150
```

Saída esperada: `PDF salvo (741304 B); 11 paginas, DOI confere`. Se vier
`sem PDF no bot (botao: 📦 Request ...)`, o bot não tem esse artigo.

### 4. Rodar a lista, um DOI por vez

Crie `dois.txt` com um DOI por linha e rode:

```powershell
python baixar_por_doi.py --saida .\pdfs --arquivo dois.txt
```

O script espera até 30 s pela resposta, clica no botão PDF, espera o arquivo, valida e passa ao
próximo com 4 s de pausa. O resumo fica em `pdfs\resultado_bot.json`.

### 5. Conferir antes de usar

- O **DOI impresso na 1ª ou 2ª página** bate com o que você pediu.
- **Mais de 100 páginas = livro de resumos**: descarte, mesmo que o DOI bata.
- Se o título não bater mas o DOI bater, olhe a primeira página à mão.

## Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| `charmap ... can't encode '\U0001f4e6'` | Faltou `PYTHONIOENCODING=utf-8`. |
| `database is locked` | Outro script está com a sessão aberta. O script já trabalha numa cópia; feche o outro. |
| `WinError 1236/1231` no meio | Queda de rede. O Telethon reconecta sozinho; confira no fim o que chegou em disco. |
| `sem resposta do bot` | Aumente `--espera 60` ou confirme o passo 2.4. |
| Resumo de congresso (suplemento) | Quase nunca tem PDF completo. Não insista. |

## Ordem sugerida de tentativa

1. Link do PDF na página da editora (acesso institucional).
2. Botão [PDF] do Google Scholar.
3. Este bot, pelo DOI.

## Uso responsável

Use apenas para artigos que você tem direito de acessar. Respeite os termos do Telegram (não
dispare em massa: o script já espera entre os pedidos) e a legislação de direitos autorais do seu país.
