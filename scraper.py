import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser
import json
import os

HISTORICO_ARQ = "historico.json"
MAX_ITENS = 30  # quantas notícias ficam visíveis no feed


# ==================================================
# HISTÓRICO
# ==================================================
def carregar_historico():
    if os.path.exists(HISTORICO_ARQ):
        with open(HISTORICO_ARQ, "r") as f:
            return json.load(f)
    return []


def salvar_historico(h):
    with open(HISTORICO_ARQ, "w") as f:
        json.dump(h, f)


# ==================================================
# GE
# ==================================================
def extrair_ge():
    URL = "https://ge.globo.com/futebol/brasileirao-serie-a/"
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    noticias = []

    for a in soup.find_all("a", class_="feed-post-link"):
        titulo = a.get_text(strip=True)
        link = a.get("href")

        if not link:
            continue

        try:
            r2 = requests.get(link)
            s2 = BeautifulSoup(r2.text, "html.parser")

            data_tag = s2.find("meta", {"property": "article:published_time"})
            data = parser.parse(data_tag["content"]) if data_tag else datetime.now()

            img_tag = s2.find("meta", {"property": "og:image"})
            imagem = img_tag["content"] if img_tag else ""

        except:
            continue

        noticias.append({
            "titulo": titulo,
            "link": link,
            "data": data.strftime("%Y-%m-%d %H:%M:%S"),
            "imagem": imagem
        })

    return noticias


# ==================================================
# GERAÇÃO DO FEED
# ==================================================
def gerar_feed():
    print("Coletando notícias...")

    historico = carregar_historico()

    # adiciona novas ao histórico
    for n in extrair_ge():
        if not any(h["link"] == n["link"] for h in historico):
            historico.append(n)

    # ordenar por data mais recente
    historico.sort(key=lambda x: x["data"], reverse=True)

    # manter só os últimos X
    historico = historico[:MAX_ITENS]

    salvar_historico(historico)

    # gerar xml
    items = ""
    for n in historico:
        data = datetime.strptime(n["data"], "%Y-%m-%d %H:%M:%S")

        items += f"""
        <item>
          <title>{n['titulo']}</title>
          <link>{n['link']}</link>
          <guid>{n['link']}</guid>
          <description><![CDATA[
            <img src="{n['imagem']}" />
            <p>{n['titulo']}</p>
          ]]></description>
          <pubDate>{data.strftime('%a, %d %b %Y %H:%M:%S -0300')}</pubDate>
        </item>
        """

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Central de Notícias do Futebol</title>
    <link>https://rssbot-production.up.railway.app/feed</link>
    <description>Atualizado automaticamente</description>
    <language>pt-br</language>
    {items}
  </channel>
</rss>
"""

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(rss)

    print(f"Feed atualizado com {len(historico)} itens.")


if __name__ == "__main__":
    gerar_feed()
