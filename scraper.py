import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser

URL = "https://ge.globo.com/futebol/brasileirao-serie-a/"

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

        # entrar na matéria
        try:
            r2 = requests.get(link)
            s2 = BeautifulSoup(r2.text, "html.parser")

            # data real da notícia
            data_tag = s2.find("meta", {"property": "article:published_time"})
            if data_tag and data_tag.get("content"):
                data_real = parser.parse(data_tag["content"])
            else:
                data_real = datetime.now()

            # imagem principal
            img_tag = s2.find("meta", {"property": "og:image"})
            imagem = img_tag["content"] if img_tag else ""

        except Exception as e:
            continue

        # só das últimas 24 horas
        if data_real < datetime.now() - timedelta(days=1):
            continue

        noticias.append({
            "titulo": titulo,
            "link": link,
            "data": data_real,
            "imagem": imagem
        })

    return noticias

def gerar_feed():
    noticias = extrair_noticias()

    if not noticias:
        print("Nenhuma notícia recente nas últimas 24h.")
        return

    items = ""

    for n in noticias:
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
    <description>Atualizado automaticamente com imagens e datas</description>
    <language>pt-br</language>
    {items}
  </channel>
</rss>
"""

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(rss)

    print("Feed atualizado com", len(noticias), "notícias.")

if __name__ == "__main__":
    gerar_feed()
