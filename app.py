import os
import json
import random
from flask import Flask, render_template, request, session

app = Flask(__name__)
# Chiave segreta per gestire i tentativi nella sessione dell'utente
app.secret_key = os.environ.get("SECRET_KEY", "chiave_segreta_spotle_2026")

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
    # Struttura feedback: [Nome, Anno, Regione, Gender, Genere, Comp]
    f = ["", "", "", "", "", ""] 
    
    # 1. NOME
    u_n = str(utente.get("nome") or "").strip().lower()
    c_n = str(corretto.get("nome") or "").strip().lower()
    if u_n == c_n: 
        f[0] = "Corretto"
    else: 
        f[0] = "Errato"

    # 2. ANNO (DEBUTTO)
    try:
        u_a = int(str(utente.get("debutto") or 0))
        c_a = int(str(corretto.get("debutto") or 0))
        if u_a == c_a: f[1] = f"Anno: {c_a} (OK)"
        else: f[1] = f"Debutto: {'Dopo il' if u_a < c_a else 'Prima del'} {u_a}"
    except: f[1] = "Anno non disponibile"

    # 3. REGIONE
    u_r = str(utente.get("regione") or "").lower()
    c_r = str(corretto.get("regione") or "").lower()
    if u_r == c_r: f[2] = f"Regione: {corretto.get('regione')} (OK)"
    else: f[2] = "Regione Errata"

    # 4. GENDER
    u_g = str(utente.get("gender") or "").upper()
    c_g = str(corretto.get("gender") or "").upper()
    if u_g == c_g: f[3] = f"Gender: {c_g} (OK)"
    else: f[3] = "Gender Errato"

    # 5. GENERE MUSICALE
    u_gen = str(utente.get("genere") or "").lower()
    c_gen = str(corretto.get("genere") or "").lower()
    if u_gen == c_gen: f[4] = f"Genere: {corretto.get('genere')} (OK)"
    else: f[4] = "Genere Errato"

    # 6. COMPONENTI
    try:
        u_c = int(str(utente.get("componenti") or 0))
        c_c = int(str(corretto.get("componenti") or 0))
        if u_c == c_c: f[5] = f"Membri: {c_c} (OK)"
        else: f[5] = f"{'Più di' if u_c < c_c else 'Meno di'} {u_c} membri"
    except: f[5] = "Dato non disponibile"

    return f

@app.route("/", methods=["GET", "POST"])
def index():
    if not artisti:
        return "Errore: File Artisti.json non trovato o vuoto."

    # Inizializzazione sessione di gioco
    if "target_name" not in session:
        session["target_name"] = random.choice(artisti)["nome"]
        session["tentativi"] = 0
        session["cronologia"] = [] # Per mostrare i tentativi precedenti

    target = next((a for a in artisti if a["nome"] == session["target_name"]), artisti[0])
    vittoria = False
    fine_giochi = False

    if request.method == "POST" and session["tentativi"] < 10:
        nome_input = request.form.get("nome", "").strip()
        u_cand = next((a for a in artisti if a["nome"].lower() == nome_input.lower()), None)
        
        if u_cand:
            session["tentativi"] += 1
            res = feedback_artista(u_cand, target)
            session["cronologia"].insert(0, {"nome": u_cand["nome"], "feedback": res})
            session.modified = True
            
            if u_cand["nome"] == target["nome"]:
                vittoria = True
                fine_giochi = True
            elif session["tentativi"] >= 10:
                fine_giochi = True

    return render_template("index.html", 
                           artisti=artisti, 
                           tentativi=session["tentativi"], 
                           cronologia=session["cronologia"],
                           fine_giochi=fine_giochi,
                           vittoria=vittoria,
                           target=target if fine_giochi else None)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
