import os
import json
import random
from flask import Flask, render_template, request, session

app = Flask(__name__)
# La chiave segreta serve per gestire la sessione (l'artista scelto)
app.secret_key = os.environ.get("SECRET_KEY", "chiave_segretissima_123")

def carica_artisti():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "Artisti.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            dati = json.load(f)
            return dati if isinstance(dati, list) else []
    except Exception as e:
        print(f"Errore caricamento file: {e}")
        return []

# Carichiamo la lista una volta sola all'avvio
artisti = carica_artisti()

def feedback_artista(utente, corretto):
    # Inizializzazione feedback
    nome_f = ""
    anno_f = ""
    regione_f = ""
    gender_f = ""
    genere_f = ""
    comp_f = ""

    # --- Nome ---
    u_nome = str(utente.get("nome") or "").strip().lower()
    c_nome = str(corretto.get("nome") or "").strip().lower()
    
    if u_nome == c_nome:
        nome_f = "Esatto!"
    elif u_nome and (u_nome in c_nome or c_nome in u_nome):
        nome_f = "Quasi, ci sei andato vicino!"
    else:
        nome_f = "Artista errato."

    # --- Debutto (Protezione int) ---
    try:
        u_deb = int(str(utente.get("debutto") or 0))
        c_deb = int(str(corretto.get("debutto") or 0))
        if u_deb != 0 and c_deb != 0:
            delta = u_deb - c_deb
            if delta == 0:
                anno_f = f"Anno corretto: {c_deb}"
            elif -10 <= delta < 0:
                anno_f = "Ci sei quasi! Debutto più recente."
            elif 0 < delta <= 10:
                anno_f = "Ci sei quasi! Debutto meno recente."
    except (ValueError, TypeError):
        anno_f = "Data non disponibile"

    # --- Regione ---
    u_reg = str(utente.get("regione") or "").strip().lower()
    c_reg = str(corretto.get("regione") or "").strip().lower()
    if u_reg == c_reg and c_reg != "":
        regione_f = f"Viene da: {corretto.get('regione')}"

    # --- Gender ---
    u_gen = str(utente.get("gender") or "").strip().lower()
    c_gen = str(corretto.get("gender") or "").strip().lower()
    if u_gen == c_gen and c_gen != "":
        if c_gen == "m": gender_f = "Maschio (♂)"
        elif c_gen == "f": gender_f = "Femmina (♀)"
        else: gender_f = "Gruppo / Altro"

    # --- Genere Musicale ---
    if nome_f != "Artista errato.":
        genere_f = f"Genere: {corretto.get('genere', 'N/D')}"

    # --- Componenti ---
    try:
        u_comp = int(str(utente.get("componenti") or 0))
        c_comp = int(str(corretto.get("componenti") or 0))
        if u_comp != 0 and c_comp != 0:
            diff = u_comp - c_comp
            if diff == 0:
                comp_f = f"Componenti: {c_comp}"
            else:
                comp_f = "Il gruppo è più numeroso" if diff < 0 else "Il gruppo ha meno membri"
    except (ValueError, TypeError):
        pass

    return nome_f, anno_f, regione_f, gender_f, genere_f, comp_f

def scegli_artista_del_giorno():
    if not artisti:
        return {"nome": "Nessun Artista", "debutto": 0, "regione": "", "gender": "", "genere": "", "componenti": 0}
    
    if "artist_name" not in session:
        scelto = random.choice(artisti)
        session["artist_name"] = scelto["nome"]
        return scelto
    
    nome_salvato = session["artist_name"]
    for a in artisti:
        if a["nome"] == nome_salvato:
            return a
    return artisti[0]

@app.route("/", methods=["GET", "POST"])
def index():
    artist = scegli_artista_del_giorno()
    feedback = None

    if request.method == "POST":
        nome_input = request.form.get("nome", "").strip()
        # Trova l'artista scelto dall'utente nella lista caricata dal JSON
        utente_candidato = next(
            (a for a in artisti if a.get("nome", "").lower() == nome_input.lower()),
            {"nome": nome_input, "debutto": 0, "regione": "", "gender": "", "genere": "", "componenti": 0}
        )
        feedback = feedback_artista(utente_candidato, artist)

    # CORREZIONE: Passiamo anche 'artisti' al template per popolare la <select>
    return render_template("index.html", feedback=feedback, artisti=artisti)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
