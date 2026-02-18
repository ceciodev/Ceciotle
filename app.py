import os
import json
import random
from flask import Flask, render_template, request, session

app = Flask(__name__)
# Usa una variabile d'ambiente per la sicurezza, o una stringa fissa
app.secret_key = os.environ.get("SECRET_KEY", "chiave_segretissima_123")

def carica_artisti():
    # Cerca il file nella stessa cartella di questo script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "Artisti.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            dati = json.load(f)
            return dati if isinstance(dati, list) else []
    except Exception as e:
        print(f"Errore caricamento file: {e}") # Apparirà nei log di Render
        return []

artisti = carica_artisti()

def scegli_artista_del_giorno():
    if not artisti:
        return {"nome": "Artista Mancante", "debutto": "0", "regione": "", "gender": "", "genere": "", "componenti": "0"}
    
    # SALVIAMO SOLO IL NOME NELLA SESSIONE
    if "artist_name" not in session:
        scelto = random.choice(artisti)
        session["artist_name"] = scelto["nome"]
        return scelto
    
    # Recuperiamo l'oggetto completo partendo dal nome salvato
    nome_salvato = session["artist_name"]
    for a in artisti:
        if a["nome"] == nome_salvato:
            return a
    return artisti[0]

# ... (resta invariata la funzione feedback_artista)

@app.route("/", methods=["GET", "POST"])
def index():
    artist = scegli_artista_del_giorno()
    feedback = None

    if request.method == "POST":
        nome_input = request.form.get("nome", "").strip()
        utente_candidato = next(
            (a for a in artisti if a.get("nome", "").lower() == nome_input.lower()),
            {"nome": nome_input, "debutto": "0", "regione": "", "gender": "", "genere": "", "componenti": "0"}
        )
        feedback = feedback_artista(utente_candidato, artist)

    return render_template("index.html", feedback=feedback)

# AGGIUNGI QUESTO PER RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
