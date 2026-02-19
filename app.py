import os
import json
import random
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ceciotle_2026_key")

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

# Carichiamo la lista una volta sola all'avvio
ARTISTI_LISTA = carica_artisti()

def feedback_artista(utente, corretto):
    f = ["ERRATO"] * 6
    if utente["nome"].lower() == corretto["nome"].lower(): f[0] = "CORRETTO"
    if utente["gender"] == corretto["gender"]: f[1] = "CORRETTO"
    if utente["genere"].lower() == corretto["genere"].lower(): f[2] = "CORRETTO"
    
    u_a, c_a = int(utente.get("debutto", 0)), int(corretto.get("debutto", 0))
    f[3] = "CORRETTO" if u_a == c_a else ("⬆️" if u_a < c_a else "⬇️")
    
    if utente["regione"].lower() == corretto["regione"].lower(): f[4] = "CORRETTO"
    
    u_c, c_c = int(utente.get("componenti", 0)), int(corretto.get("componenti", 0))
    f[5] = "CORRETTO" if u_c == c_c else ("⬆️" if u_c < c_c else "⬇️")
    
    return f

@app.route("/", methods=["GET", "POST"])
def index():
    if not ARTISTI_LISTA:
        return "Errore: File Artisti.json non trovato o vuoto.", 500

    if "target_name" not in session:
        session["target_name"] = random.choice(ARTISTI_LISTA)["nome"]
        session["tentativi"] = 0
        session["cronologia"] = []

    target = next((a for a in ARTISTI_LISTA if a["nome"] == session["target_name"]), ARTISTI_LISTA[0])
    vittoria = False
    fine_giochi = False

    if request.method == "POST" and session["tentativi"] < 10:
        nome_input = request.form.get("nome", "").strip()
        u_cand = next((a for a in ARTISTI_LISTA if a["nome"].lower() == nome_input.lower()), None)
        
        if u_cand:
            session["tentativi"] += 1
            res = feedback_artista(u_cand, target)
            session["cronologia"].insert(0, {
                "nome": u_cand["nome"], "gender": u_cand["gender"],
                "genere": u_cand["genere"], "debutto": u_cand["debutto"],
                "regione": u_cand["regione"], "componenti": u_cand["componenti"],
                "feedback": res
            })
            session.modified = True
            
            if u_cand["nome"].lower() == target["nome"].lower():
                vittoria = True
                fine_giochi = True
            elif session["tentativi"] >= 10:
                fine_giochi = True

    return render_template("index.html", artisti=ARTISTI_LISTA, tentativi=session.get("tentativi", 0), 
                           cronologia=session.get("cronologia", []), fine_giochi=fine_giochi, 
                           vittoria=vittoria, target=target)

@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
