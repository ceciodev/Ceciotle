import os
import json
import random
import threading
import time
import requests
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ceciotle_2026_key")

# --- KEEP ALIVE OTTIMIZZATO ---
def keep_alive():
    # Aspetta che il server sia effettivamente attivo prima di pingare
    time.sleep(20) 
    while True:
        try:
            # Sostituisci con il tuo URL reale se diverso
            url = "https://ceciotle.onrender.com/"
            requests.get(url, timeout=10)
            print("Self-ping successful!")
        except Exception as e:
            print(f"Ping failed (normale se il server si sta ancora avviando): {e}")
        
        time.sleep(300) # 5 minuti

# Facciamo partire il thread solo se non siamo in modalità debug (evita doppie istanze)
if os.environ.get("RENDER"):
    threading.Thread(target=keep_alive, daemon=True).start()

def carica_artisti():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "Artisti.json")
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                dati = json.load(f)
                return dati if isinstance(dati, list) else []
        print(f"File non trovato: {file_path}")
        return []
    except Exception as e:
        print(f"Errore caricamento JSON: {e}")
        return []

ARTISTI_LISTA = carica_artisti()

def feedback_artista(utente, corretto):
    res = {}
    
    # Sesso
    res['gender'] = [
        "CORRETTO" if utente["gender"] == corretto["gender"] else "ERRATO", 
        "✅" if utente["gender"] == corretto["gender"] else "❌", 
        "Uomo" if utente["gender"] == 'M' else "Donna" if utente["gender"] == 'F' else "Misto"
    ]
    
    # Genere Musicale
    res['genere'] = [
        "CORRETTO" if utente.get("genere", "").lower() == corretto.get("genere", "").lower() else "ERRATO", 
        "✅" if utente.get("genere", "").lower() == corretto.get("genere", "").lower() else "❌", 
        utente.get("genere", "N/D")
    ]
    
    # Debutto
    u_a = int(utente.get("debutto", 0))
    c_a = int(corretto.get("debutto", 0))
    segno_a = "✅" if u_a == c_a else ("⬆️" if u_a < c_a else "⬇️")
    res['debutto'] = ["CORRETTO" if u_a == c_a else "ERRATO", segno_a, u_a]
    
    # Regione
    res['regione'] = [
        "CORRETTO" if utente.get("regione", "").lower() == corretto.get("regione", "").lower() else "ERRATO", 
        "✅" if utente.get("regione", "").lower() == corretto.get("regione", "").lower() else "❌", 
        utente.get("regione", "N/D")
    ]
    
    # Componenti
    u_c = int(utente.get("componenti", 1))
    c_c = int(corretto.get("componenti", 1))
    segno_c = "✅" if u_c == c_c else ("⬆️" if u_c < c_c else "⬇️")
    res['componenti'] = ["CORRETTO" if u_c == c_c else "ERRATO", segno_c, u_c]

    # Popolarità (Ascoltatori Mensili)
    u_p = int(utente.get("popolarita", 0))
    c_p = int(corretto.get("popolarita", 0))
    segno_p = "✅" if u_p == c_p else ("⬆️" if u_p < c_p else "⬇️")
    res['popolarita'] = ["CORRETTO" if u_p == c_p else "ERRATO", segno_p, f"{u_p:,}".replace(",", ".")]
    
    return res

@app.route("/", methods=["GET", "POST"])
def index():
    if not ARTISTI_LISTA:
        return "Errore: Il file JSON è vuoto o non è stato caricato correttamente.", 500

    if "target_name" not in session:
        target_obj = random.choice(ARTISTI_LISTA)
        session["target_name"] = target_obj["nome"]
        session["tentativi"] = 0
        session["cronologia"] = []

    # Cerchiamo il target corrente nella lista
    target = next((a for a in ARTISTI_LISTA if a["nome"] == session["target_name"]), ARTISTI_LISTA[0])
    
    vittoria = False
    fine_giochi = False

    if request.method == "POST":
        tentativi_attuali = session.get("tentativi", 0)
        
        if tentativi_attuali < 10:
            nome_input = request.form.get("nome", "").strip()
            # Confronto flessibile per gestire accenti e spazi
            u_cand = next((a for a in ARTISTI_LISTA if a["nome"].lower() == nome_input.lower()), None)
            
            if u_cand:
                session["tentativi"] = tentativi_attuali + 1
                res = feedback_artista(u_cand, target)
                
                # Inseriamo in cima alla lista per vederlo subito
                session["cronologia"].insert(0, {"nome": u_cand["nome"], "feedback": res})
                session.modified = True
                
                if u_cand["nome"].lower() == target["nome"].lower():
                    vittoria = True
                    fine_giochi = True
                elif session["tentativi"] >= 10:
                    fine_giochi = True

    return render_template("index.html", 
                           artisti=ARTISTI_LISTA, 
                           tentativi=session.get("tentativi", 0), 
                           cronologia=session.get("cronologia", []), 
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
