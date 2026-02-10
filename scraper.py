import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser
import json
import os

HISTORICO_ARQ = "historico.json"


# ==================================================
# HISTÓRICO
# ==================================================
def carregar_historico():
    if os.path.exists(HISTORICO_ARQ):
        with open(HISTORICO_ARQ, "r") as f:
            return set(json.load(f))
    return set()


def salvar_historico(h):
    with open(HISTORICO_ARQ, "w") as f:
        json.dump(list(h), f)


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

        if not link or "/brasileirao-serie-a/" not in link:
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
            "data": data,
            "imagem": imagem
        })

    return noticias


# ==================================================
# ESPN
# ==================================================
def extrair_espn():
    URL = "https://www.espn.com.br/futebol/"
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    noticias = []

    for a in soup.find_all("a", href=True):
        link = a["href"]

        if "/artigo/" not in link:
            continue

        titulo = a.get_text(strip=True)
        if not titulo:
            continue

        try:
            r2 = requests.get(link)
            s2 = BeautifulSoup(r2.text, "html.parser")

            img_tag = s2.find("meta", {"property": "og:image"})
            imagem = img_tag["content"] if img_tag else ""

        except:
            continue

        noticias.append({
            "titulo": titulo,
            "link": link,
            "data": datetime.now(),
            "imagem": imagem
        })

    return noticias


# ==================================================
# UOL
# ==================================================
def extrair_uol():
    URL = "https://www.uol.com.br/esporte/futebol/"
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    noticias = []

    for a in soup.find_all("a", href=True):
        link = a["href"]

        if "/noticias/" not in link:
            continue

        titulo = a.get_text(strip=True)
        if not titulo:
            continue

        noticias.append({
            "titulo": titulo,
            "link": link,
            "data": datetime.now(),
            "imagem": ""
        })

    return noticias


# ==================================================
# LANCE
# ==================================================
def extrair_lance():
    URL = "https://www.lance.com.br/"
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    noticias = []

    for a in soup.find_all("a", href=True):
        link = a["href"]

        if "/futebol/" not in link:
            continue

        titulo = a.get_text(strip=True)
        if not titulo:
            continue

        noticias.append({
            "titulo": titulo,
            "link": link,
            "data": datetime.now(),
            "imagem": ""
        })

    return noticias


# ==================================================
# GERAÇÃO DO FEED
# ==================================================
def gerar_feed():
    print("Coletando fontes...")

    noticias = (
        extrair_ge()
        + extrair_espn()
        + extrair_uol()
        + extrair_lance()
    )

    agora = datetime.now()
    historico = carregar_historico()

    novas = []

    for n in noticias:
        if n["link"] in historico:
            continue

        if n["data"] < agora - timedelta(days=1):
            continue

        novas.append(n)
        historico.add(n["link"])

    if not novas:
        print("Nenhuma novidade.")
        return

    # ordenar mais recentes primeiro
    novas.sort(key=lambda x: x["data"], reverse=True)

    items = ""
    for n in novas:
        items += f"""
        <item>
          <title>{n['titulo']}</title>
          <link>{n['link']}</link>
          <guid>{n['link']}</guid>
          <description><![CDATA[
            <img src="{n['imagem']}" />
            <p>{n['titulo']}</p>
          ]]></description>
          <pubDate>{n['data'].strftime('%a, %d %b %Y %H:%M:%S -0300')}</pubDate>
        </item>
        """

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Central de Notícias do Futebol</title>
    <link>https://rssbot-production.up.railway.app/feed</link>
    <description>GE + ESPN + UOL + Lance</description>
    <language>pt-br</language>
    {items}
  </channel>
</rss>
"""

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(rss)

    salvar_historico(historico)

    print(f"{len(novas)} novidades publicadas.")


if __name__ == "__main__":
    gerar_feed()
