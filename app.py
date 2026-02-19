import os
import json
import random
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
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
    Genera il feedback per ogni caratteristica.
    Restituisce una lista di stati (CORRETTO/ERRATO o frecce per numeri).
    """
    # Struttura feedback: [0:Nome, 1:Gender, 2:GenereMusicale, 3:Debutto, 4:Regione, 5:Componenti]
    f = ["ERRATO"] * 6 
    
    # 1. NOME
    if utente["nome"].lower() == corretto["nome"].lower():
        f[0] = "CORRETTO"

    # 2. GENDER
    if utente["gender"] == corretto["gender"]:
        f[1] = "CORRETTO"

    # 3. GENERE MUSICALE
    if utente["genere"].lower() == corretto["genere"].lower():
        f[2] = "CORRETTO"

    # 4. ANNO DI DEBUTTO (Con frecce)
    u_a = int(utente.get("debutto", 0))
    c_a = int(corretto.get("debutto", 0))
    if u_a == c_a:
        f[3] = "CORRETTO"
    else:
        f[3] = "⬆️" if u_a < c_a else "⬇️"

    # 5. REGIONE
    if utente["regione"].lower() == corretto["regione"].lower():
        f[4] = "CORRETTO"

    # 6. COMPONENTI (Con frecce)
    u_c = int(utente.get("componenti", 0))
    c_c = int(corretto.get("componenti", 0))
    if u_c == c_c:
        f[5] = "CORRETTO"
    else:
        f[5] = "⬆️" if u_c < c_c else "⬇️"

    return f

@app.route("/", methods=["GET", "POST"])
def index():
    if not artisti:
        return "Errore: File Artisti.json non trovato o vuoto."

    if "target_name" not in session:
        session["target_name"] = random.choice(artisti)["nome"]
        session["tentativi"] = 0
        session["cronologia"] = []

    target = next((a for a in artisti if a["nome"] == session["target_name"]), artisti[0])
    vittoria = False
    fine_giochi = False

    if request.method == "POST" and session["tentativi"] < 10:
        nome_input = request.form.get("nome", "").strip()
        u_cand = next((a for a in artisti if a["nome"].lower() == nome_input.lower()), None)
        
        if u_cand:
            session["tentativi"] += 1
            res = feedback_artista(u_cand, target)
            
            # Salviamo i dati reali dell'artista scelto insieme agli stati del feedback
            session["cronologia"].insert(0, {
                "nome": u_cand["nome"],
                "gender": u_cand["gender"],
                "genere": u_cand["genere"],
                "debutto": u_cand["debutto"],
                "regione": u_cand["regione"],
                "componenti": u_cand["componenti"],
                "feedback": res
            })
            session.modified = True
            
            if u_cand["nome"].lower() == target["nome"].lower():
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
                           target=target)

@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
