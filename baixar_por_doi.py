r"""
Baixa PDFs pelo bot do Telegram @nielsbohr_bot, um DOI por vez.

Usa a SUA conta do Telegram (Telethon), nao um token de bot.
Nenhuma credencial fica neste arquivo: tudo vem de variaveis de ambiente.

  TG_API_ID, TG_API_HASH   -> https://my.telegram.org > API development tools
  TG_SESSION               -> caminho de um .session do Telethon ja logado
                              (sem a extensao .session). O script trabalha numa COPIA.

Uso:
  python baixar_por_doi.py --saida D:\pdfs 10.1227/neu.0000000000004150 10.1136/jnis-2023-020285
  python baixar_por_doi.py --saida D:\pdfs --arquivo dois.txt      (1 DOI por linha)

Saida: <saida>/<doi com / trocado por _>.pdf  +  <saida>/resultado_bot.json
Nunca clica em "Request" (gasta cota). So baixa quando o botao e "PDF".
"""
import argparse, asyncio, json, os, re, shutil, sys, tempfile

from telethon import TelegramClient

BOT = "nielsbohr_bot"


def validar(path, doi):
    """Confere DOI na 1a/2a pagina e numero de paginas. Devolve (ok, texto)."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return None, "pypdf ausente (pip install pypdf): nao validei"
    r = PdfReader(path)
    n = len(r.pages)
    t = " ".join((r.pages[k].extract_text() or "") for k in range(min(2, n)))
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    doi_ok = norm(doi) in norm(t)
    if n > 100:
        return False, f"{n} paginas: provavel livro de resumos"
    return doi_ok, f"{n} paginas, DOI {'confere' if doi_ok else 'NAO confere (conferir a mao)'}"


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dois", nargs="*")
    ap.add_argument("--arquivo")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--espera", type=int, default=30, help="segundos esperando a resposta do bot")
    a = ap.parse_args()

    dois = list(a.dois)
    if a.arquivo:
        dois += [l.strip() for l in open(a.arquivo, encoding="utf-8") if l.strip()]
    if not dois:
        sys.exit("Passe pelo menos um DOI.")

    try:
        api_id = int(os.environ["TG_API_ID"]); api_hash = os.environ["TG_API_HASH"]
        sessao = os.environ["TG_SESSION"]
    except KeyError as e:
        sys.exit(f"Falta a variavel de ambiente {e}. Veja o passo 1 da SKILL.md.")

    os.makedirs(a.saida, exist_ok=True)
    tmp = tempfile.mkdtemp()
    shutil.copy(sessao + ".session", os.path.join(tmp, "s.session"))  # copia: evita SQLite travado

    resultado = {}
    async with TelegramClient(os.path.join(tmp, "s"), api_id, api_hash, receive_updates=False) as c:
        bot = await c.get_entity(BOT)
        for doi in dois:
            doi = doi.strip()
            ultimo = (await c.get_messages(bot, limit=1))[0].id
            await c.send_message(bot, doi)
            resp = None
            for _ in range(max(1, a.espera // 3)):
                await asyncio.sleep(3)
                novas = [m for m in await c.get_messages(bot, limit=5, min_id=ultimo) if not m.out]
                if novas:
                    resp = max(novas, key=lambda m: m.id)
                    break
            if not resp:
                resultado[doi] = "sem resposta do bot"; print(doi, "->", resultado[doi], flush=True); continue

            botoes = [b.text for linha in (resp.buttons or []) for b in linha]
            primeiro = botoes[0] if botoes else ""
            if "PDF" in primeiro and primeiro.strip().startswith("\u2b07"):
                await resp.click(0, 0)
                destino = os.path.join(a.saida, re.sub(r"[^A-Za-z0-9._-]+", "_", doi) + ".pdf")
                salvo = None
                for _ in range(15):
                    await asyncio.sleep(3)
                    for m in [m for m in await c.get_messages(bot, limit=5, min_id=resp.id) if not m.out]:
                        if m.document:
                            salvo = await c.download_media(m, file=destino); break
                    if salvo: break
                if salvo:
                    ok, txt = validar(salvo, doi)
                    resultado[doi] = f"PDF salvo ({os.path.getsize(salvo)} B); {txt}"
                else:
                    resultado[doi] = "cliquei em PDF mas o arquivo nao chegou"
            else:
                resultado[doi] = f"sem PDF no bot (botao: {primeiro or 'nenhum'})"
            print(doi, "->", resultado[doi], flush=True)
            await asyncio.sleep(4)  # um por vez, sem metralhar o bot

    json.dump(resultado, open(os.path.join(a.saida, "resultado_bot.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    shutil.rmtree(tmp, ignore_errors=True)


asyncio.run(main())
