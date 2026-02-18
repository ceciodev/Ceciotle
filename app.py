import os
import json
import random
from flask import Flask, render_template, request, session

app = Flask(__name__)
# Chiave segreta per gestire la sessione (tentativi e artista del giorno)
app.secret_key = os.environ.get("SECRET_KEY", "spotle_italiano_key_2026")

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
    """
    Genera il feedback con emoji per ogni caratteristica.
    Struttura: [Nome, Debutto, Regione, Gender, Genere, Membri]
    """
    f = ["", "", "", "", "", ""] 
    OK = "✅"
    NO = "❌"
    SU = "⬆️"
    GIU = "⬇️"
    
    # 1. NOME
    u_n = str(utente.get("nome") or "").strip().lower()
    c_n = str(corretto.get("nome") or "").strip().lower()
    f[0] = OK if u_n == c_n else NO

    # 2. ANNO DI DEBUTTO
    try:
        u_a = int(str(utente.get("debutto") or 0))
        c_a = int(str(corretto.get("debutto") or 0))
        if u_a == c_a: 
            f[1] = f"Debutto: {c_a} {OK}"
        else:
            freccia = SU if u_a < c_a else GIU
            f[1] = f"Debutto: {u_a} {freccia}"
    except: 
        f[1] = f"Debutto {NO}"

    # 3. REGIONE
    u_r = str(utente.get("regione") or "").lower()
    c_r = str(corretto.get("regione") or "").lower()
    f[2] = f"Regione {OK}" if u_r == c_r else f"Regione {NO}"

    # 4. GENDER
    u_g = str(utente.get("gender") or "").upper()
    c_g = str(corretto.get("gender") or "").upper()
    f[3] = f"Gender {OK}" if u_g == c_g else f"Gender {NO}"

    # 5. GENERE MUSICALE
    u_gen = str(utente.get("genere") or "").lower()
    c_gen = str(corretto.get("genere") or "").lower()
    f[4] = f"Genere {OK}" if u_gen == c_gen else f"Genere {NO}"

    # 6. COMPONENTI
    try:
        u_c = int(str(utente.get("componenti") or 0))
        c_c = int(str(corretto.get("componenti") or 0))
        if u_c == c_c: 
            f[5] = f"Membri: {c_c} {OK}"
        else:
            freccia = SU if u_c < c_c else GIU
            f[5] = f"Membri: {u_c} {freccia}"
    except: 
        f[5] = f"Membri {NO}"

    return f

@app.route("/", methods=["GET", "POST"])
def index():
    if not artisti:
        return "Errore: File Artisti.json non trovato o vuoto."

    # Inizializzazione della sessione di gioco
    if "target_name" not in session:
        session["target_name"] = random.choice(artisti)["nome"]
        session["tentativi"] = 0
        session["cronologia"] = []

    target = next((a for a in artisti if a["nome"] == session["target_name"]), artisti[0])
    vittoria = False
    fine_giochi = False

    if request.method == "POST" and session["tentativi"] < 10:
        nome_input = request.form.get("nome", "").strip()
        # Cerchiamo l'artista inserito nella nostra lista
        u_cand = next((a for a in artisti if a["nome"].lower() == nome_input.lower()), None)
        
        if u_cand:
            session["tentativi"] += 1
            res = feedback_artista(u_cand, target)
            
            # Aggiungiamo il tentativo in cima alla lista (per vederlo subito)
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
