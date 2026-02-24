import os
import json
import random
import threading
import time
import requests
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ceciotle_2026_key")

# --- KEEP ALIVE OTTIMIZZATO ---
def keep_alive():
    time.sleep(30) 
    while True:
        try:
            url = "https://ceciotle.onrender.com/"
            requests.get(url, timeout=10)
            print("Self-ping successful!")
        except Exception as e:
            print(f"Ping standby: {e}")
        time.sleep(300)

threading.Thread(target=keep_alive, daemon=True).start()

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

ARTISTI_LISTA = carica_artisti()

def feedback_artista(utente, corretto):
    res = {}
    # Sesso
    res['gender'] = [
        "CORRETTO" if utente["gender"] == corretto["gender"] else "ERRATO", 
        "✅" if utente["gender"] == corretto["gender"] else "❌", 
        "Uomo" if utente["gender"] == 'M' else "Donna" if utente["gender"] == 'F' else "Misto"
    ]
    # Genere
    res['genere'] = [
        "CORRETTO" if utente.get("genere", "").lower() == corretto.get("genere", "").lower() else "ERRATO", 
        "✅" if utente.get("genere", "").lower() == corretto.get("genere", "").lower() else "❌", 
        utente.get("genere", "N/D")
    ]
    # Debutto
    u_a = int(str(utente.get("debutto", 0)).replace(".", ""))
    c_a = int(str(corretto.get("debutto", 0)).replace(".", ""))
    res['debutto'] = ["CORRETTO" if u_a == c_a else "ERRATO", "✅" if u_a == c_a else ("⬆️" if u_a < c_a else "⬇️"), u_a]
    
    # Regione
    res['regione'] = [
        "CORRETTO" if utente.get("regione", "").lower() == corretto.get("regione", "").lower() else "ERRATO", 
        "✅" if utente.get("regione", "").lower() == corretto.get("regione", "").lower() else "❌", 
        utente.get("regione", "N/D")
    ]
    # Componenti
    u_c = int(utente.get("componenti", 1))
    c_c = int(corretto.get("componenti", 1))
    res['componenti'] = ["CORRETTO" if u_c == c_c else "ERRATO", "✅" if u_c == c_c else ("⬆️" if u_c < c_c else "⬇️"), u_c]

    # Popolarità
    u_p = int(str(utente.get("Popolarita", utente.get("popolarita", 0))).replace(".", ""))
    c_p = int(str(corretto.get("Popolarita", corretto.get("popolarita", 0))).replace(".", ""))
    res['popolarita'] = ["CORRETTO" if u_p == c_p else "ERRATO", "✅" if u_p == c_p else ("⬆️" if u_p > c_p else "⬇️"), u_p]
    
    return res

# --- ROTTE FLASK RIPRISTINATE ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if not ARTISTI_LISTA:
        return "Errore: Database artisti vuoto o non trovato.", 500
    
    # Inizializza la partita se la sessione è vuota
    if 'target' not in session:
        return redirect(url_for('restart'))

    if request.method == 'POST':
        if session.get('fine_giochi'):
            return redirect(url_for('index'))

        scelta_nome = request.form.get('nome', '').strip()
        artista_scelto = next((a for a in ARTISTI_LISTA if a['nome'].lower() == scelta_nome.lower()), None)

        if artista_scelto:
            feedback = feedback_artista(artista_scelto, session['target'])
            cronologia = session.get('cronologia', [])
            
            # Aggiungiamo in cima alla lista per visualizzare l'ultimo tentativo per primo
            cronologia.insert(0, {
                'nome': artista_scelto['nome'],
                'feedback': feedback
            })
            session['cronologia'] = cronologia
            
            if artista_scelto['nome'] == session['target']['nome']:
                session['vittoria'] = True
                session['fine_giochi'] = True
            elif len(cronologia) >= 10:
                session['fine_giochi'] = True
            
            session.modified = True
        return redirect(url_for('index'))

    return render_template('index.html', 
                           tentativi=len(session.get('cronologia', [])),
                           vittoria=session.get('vittoria', False),
                           fine_giochi=session.get('fine_giochi', False),
                           target=session.get('target'),
                           cronologia=session.get('cronologia', []),
                           artisti_nomi=[a['nome'] for a in ARTISTI_LISTA])

@app.route('/restart')
def restart():
    if not ARTISTI_LISTA:
        return "Errore: Database vuoto.", 500
    session['target'] = random.choice(ARTISTI_LISTA)
    session['cronologia'] = []
    session['vittoria'] = False
    session['fine_giochi'] = False
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
