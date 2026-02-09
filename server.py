from flask import Flask, send_file

app = Flask(__name__)

@app.route("/feed")
def feed():
    return send_file("feed.xml", mimetype="application/rss+xml")

app.run(host="0.0.0.0", port=8000)
