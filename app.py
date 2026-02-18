import os
import json
import random
from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = "chiave_segretissima"  # necessaria per session

# ------------------ Caricamento dati ------------------

def carica_artisti():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "Artisti.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

artisti = carica_artisti()

def scegli_artista_del_giorno():
    if not artisti:
        return None
    if "artist" not in session:
        session["artist"] = random.choice(artisti)
    return session["artist"]

# ------------------ Logica feedback ------------------

def feedback_artista(utente, corretto):
    # Nome
    if utente.get("nome", "").lower() == corretto.get("nome", "").lower():
        nome_feedback = "Esatto!"
    elif utente.get("nome", "").lower() in corretto.get("nome", "").lower() or corretto.get("nome", "").lower() in utente.get("nome", "").lower():
        nome_feedback = "Quasi, ci sei andato vicino!"
    else:
        nome_feedback = "Artista errato."

    # Anno di debutto
    anno_feedback = ""
    try:
        delta = int(utente.get("debutto", 0)) - int(corretto.get("debutto", 0))
        if delta == 0 and nome_feedback == "Esatto!":
            anno_feedback = f"{corretto['debutto']}"
        elif -10 <= delta < 0:
            anno_feedback = "Ci sei quasi! Debutto più recente."
        elif 0 < delta <= 10:
            anno_feedback = "Ci sei quasi! Debutto meno recente."
    except ValueError:
        pass

    # Regione
    regione_feedback = ""
    if utente.get("regione", "").lower() == corretto.get("regione", "").lower():
        regione_feedback = f"Viene da: {corretto.get('regione', '')}"

    # Gender
    gender_feedback = ""
    if utente.get("gender", "").lower() == corretto.get("gender", "").lower():
        gender_value = corretto.get("gender", "").lower()
        gender_feedback = "♂" if gender_value == "m" else "♀" if gender_value == "f" else ""

    # Genere musicale
    genere_feedback = ""
    if nome_feedback == "Esatto!":
        genere_corretto = corretto.get("genere", "")
        if genere_corretto.lower() in ["cantautore", "cantautore/pop"]:
            genere_feedback = "L'artista è un cantautore"
        else:
            genere_feedback = f"La mia banda suona il {genere_corretto}"

    # Componenti
    componenti_feedback = ""
    try:
        diff = int(utente.get("componenti", 0)) - int(corretto.get("componenti", 0))
        if diff == 0:
            componenti_feedback = f"Numero componenti corretto: {corretto['componenti']}"
        elif diff < 0:
            componenti_feedback = "Il gruppo ha più componenti."
        else:
            componenti_feedback = "Il gruppo ha meno componenti."
    except ValueError:
        pass

    return nome_feedback, anno_feedback, regione_feedback, gender_feedback, genere_feedback, componenti_feedback

# ------------------ Route web ------------------

@app.route("/", methods=["GET", "POST"])
def index():
    artist = scegli_artista_del_giorno()
    feedback = None

    if request.method == "POST":
        nome_input = request.form.get("nome", "").strip()
        utente_candidato = next(
            (a for a in artisti if a.get("nome", "").lower() == nome_input.lower()),
            {"nome": nome_input}
        )
        feedback = feedback_artista(utente_candidato, artist)

    return render_template("index.html", feedback=feedback)
