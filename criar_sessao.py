r"""
Cria a SUA sessao do Telegram (Telethon). Rode uma vez por pessoa/conta.

  TG_API_ID, TG_API_HASH  -> https://my.telegram.org > API development tools (cada pessoa cria o seu)

Uso:
  python criar_sessao.py minha_sessao

Vai pedir seu telefone (com +55...), o codigo que chega no app do Telegram e, se tiver, a senha de
duas etapas. Gera o arquivo minha_sessao.session. Esse arquivo da acesso TOTAL a sua conta:
nao envie para ninguem e nao suba no GitHub.
"""
import asyncio, os, sys
from telethon import TelegramClient

nome = sys.argv[1] if len(sys.argv) > 1 else "minha_sessao"
try:
    api_id = int(os.environ["TG_API_ID"]); api_hash = os.environ["TG_API_HASH"]
except KeyError as e:
    sys.exit(f"Falta a variavel de ambiente {e}. Veja o passo 2 do README.")


async def main():
    async with TelegramClient(nome, api_id, api_hash) as c:  # pede telefone/codigo no terminal
        eu = await c.get_me()
        print(f"Logado como {eu.first_name}. Sessao salva em {os.path.abspath(nome)}.session")


asyncio.run(main())
