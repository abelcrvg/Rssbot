from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Servidor online."

@app.route("/feed")
def feed():
    caminho = os.path.join(os.path.dirname(__file__), "feed.xml")
    return send_file(caminho, mimetype="application/rss+xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
