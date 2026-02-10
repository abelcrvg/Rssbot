import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser
import json
import os

URL = "https://ge.globo.com/futebol/brasileirao-serie-a/"
HISTORICO_ARQ = "historico.json"


# ===============================
# HISTÓRICO
# ===============================
def carregar_historico():
    if os.path.exists(HISTORICO_ARQ):
        with open(HISTORICO_ARQ, "r") as f:
            return set(json.load(f))
    return set()


def salvar_historico(h):
    with open(HISTORICO_ARQ, "w") as f:
        json.dump(list(h), f)


# ===============================
# EXTRAÇÃO
# ===============================
def extrair_noticias():
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    links = soup.find_all("a", class_="feed-post-link")

    noticias = []

    for a in links:
        titulo = a.get_text(strip=True)
        link = a.get("href")

        if not link or "/brasileirao-serie-a/" not in link:
            continue

        try:
            r2 = requests.get(link)
            s2 = BeautifulSoup(r2.text, "html.parser")

            data_tag = s2.find("meta", {"property": "article:published_time"})
            if data_tag:
                data_real = parser.parse(data_tag["content"])
            else:
                data_real = datetime.now()

            img_tag = s2.find("meta", {"property": "og:image"})
            imagem = img_tag["content"] if img_tag else ""

        except Exception:
            continue

        # apenas últimas 24 horas
        if data_real < datetime.now() - timedelta(days=1):
            continue

        noticias.append({
            "titulo": titulo,
            "link": link,
            "data": data_real,
            "imagem": imagem
        })

    return noticias


# ===============================
# GERAÇÃO DO RSS
# ===============================
def gerar_feed():
    print("Buscando notícias...")

    noticias = extrair_noticias()
    historico = carregar_historico()

    novas = []

    for n in noticias:
        if n["link"] not in historico:
            novas.append(n)
            historico.add(n["link"])

    if not novas:
        print("Nenhuma novidade.")
        return

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
    <title>Brasileirão Série A – Últimas 24h</title>
    <link>{URL}</link>
    <description>Atualizado automaticamente</description>
    <language>pt-br</language>
    {items}
  </channel>
</rss>
"""

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(rss)

    salvar_historico(historico)

    print(f"{len(novas)} notícias novas adicionadas.")


# executar manualmente se quiser
if __name__ == "__main__":
    gerar_feed()
