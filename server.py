from flask import Flask, send_file
import os
import threading
import time
import scraper  # usa seu arquivo scraper.py

app = Flask(__name__)

INTERVALO = 30 * 60  # 30 minutos


def atualizacao_automatica():
    while True:
        try:
            print("Atualizando feed automaticamente...")
            scraper.gerar_feed()
            print("Atualizado.")
        except Exception as e:
            print("Erro ao atualizar:", e)

        time.sleep(INTERVALO)


@app.route("/")
def home():
    return "Servidor online."


@app.route("/feed")
def feed():
    caminho = os.path.join(os.path.dirname(__file__), "feed.xml")
    return send_file(caminho, mimetype="application/rss+xml")


if __name__ == "__main__":
    # inicia a thread do relógio
    t = threading.Thread(target=atualizacao_automatica)
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port=8080)
