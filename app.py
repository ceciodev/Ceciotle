import os
import json
import random
from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = "chiave_segretissima"  # serve per session

# Load artists
def carica_artisti():
    file_path = os.path.join(os.path.dirname(__file__), "Artisti.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

artisti = carica_artisti()

def scegli_artista_del_giorno():
    if not artisti:
        return None
    # Usa session per mantenerlo stabile durante la visita
    if "artist" not in session:
        session["artist"] = random.choice(artisti)
    return session["artist"]

def feedback_artista(utente, corretto):
    nome_fb = "Esatto!" if utente.get("nome", "").lower() == corretto.get("nome", "").lower() else "Artista errato."
    anno_fb = corretto.get("debutto", "")
    regione_fb = corretto.get("regione", "")
    gender_fb = "♂" if corretto.get("gender","").lower()=="m" else "♀"
    genere_fb = corretto.get("genere", "")
    componenti_fb = corretto.get("componenti", "")
    return nome_fb, anno_fb, regione_fb, gender_fb, genere_fb, componenti_fb

@app.route("/", methods=["GET", "POST"])
def index():
    artist = scegli_artista_del_giorno()
    feedback = None

    if request.method == "POST":
        nome_input = request.form.get("nome", "").strip()
        utente_candidato = next((a for a in artisti if a.get("nome", "").lower() == nome_input.lower()), {"nome": nome_input})
        feedback = feedback_artista(utente_candidato, artist)

    return render_template("index.html", feedback=feedback)
