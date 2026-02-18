import os
import json
import random
from flask import Flask, render_template, request, session

app = Flask(__name__)
# Render usa questa chiave per criptare i dati di gioco (la sessione)
app.secret_key = os.environ.get("SECRET_KEY", "chiave_segreta_indovina_artista_2026")

def carica_artisti():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "Artisti.json")
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                dati = json.load(f)
                return dati if isinstance(dati, list) else []
        return []
    except Exception as e:
        print(f"Errore caricamento JSON: {e}")
        return []

artisti = carica_artisti()

def feedback_artista(utente, corretto):
    f = ["", "", "", "", "", ""] # Nome, Anno, Regione, Gender, Genere, Comp
    
    # Nome
    u_n = str(utente.get("nome") or "").strip().lower()
    c_n = str(corretto.get("nome") or "").strip().lower()
    if u_n == c_n: f[0] = "Esatto!"
    elif u_n in c_n or c_n in u_n: f[0] = "Quasi!"
    else: f[0] = "Errato."

    # Anno
    try:
        u_a = int(str(utente.get("debutto") or 0))
        c_a = int(str(corretto.get("debutto") or 0))
        if u_a != 0 and c_a != 0:
            if u_a == c_a: f[1] = f"Anno corretto: {c_a}"
            else: f[1] = "Più recente" if u_a < c_a else "Meno recente"
    except: pass

    # Regione
    if str(utente.get("regione") or "").lower() == str(corretto.get("regione") or "").lower():
        f[2] = f"Regione: {corretto.get('regione')}"

    # Gender
    if str(utente.get("gender") or "").lower() == str(corretto.get("gender") or "").lower():
        gen = str(corretto.get("gender")).upper()
        f[3] = "♂" if gen == "M" else "♀" if gen == "F" else "Gruppo"

    # Genere Musicale
    if f[0] != "Errato.":
        f[4] = f"Genere: {corretto.get('genere')}"

    # Componenti
    try:
        u_c = int(str(utente.get("componenti") or 0))
        c_c = int(str(corretto.get("componenti") or 0))
        if u_c != 0 and c_c != 0:
            if u_c == c_c: f[5] = f"Membri: {c_c}"
            else: f[5] = "Di più" if u_c < c_c else "Di meno"
    except: pass

    return f

@app.route("/", methods=["GET", "POST"])
def index():
    if not artisti:
        return "Errore: File Artisti.json non trovato o vuoto."

    # Gestione Artista del Giorno via Sessione
    if "target_name" not in session:
        session["target_name"] = random.choice(artisti)["nome"]
    
    target = next((a for a in artisti if a["nome"] == session["target_name"]), artisti[0])
    feedback = None

    if request.method == "POST":
        nome_input = request.form.get("nome", "").strip()
        u_cand = next((a for a in artisti if a["nome"].lower() == nome_input.lower()), {"nome": nome_input})
        feedback = feedback_artista(u_cand, target)

    return render_template("index.html", feedback=feedback, artisti=artisti)

if __name__ == "__main__":
    # IMPORTANTE: Questa riga permette a Render di vedere l'app sulla porta corretta
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
