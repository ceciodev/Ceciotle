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
    # Aspetta 30 secondi per dare tempo a Flask/Gunicorn di legarsi alla porta
    time.sleep(30) 
    while True:
        try:
            url = "https://ceciotle.onrender.com/"
            requests.get(url, timeout=10)
            print("Self-ping successful!")
        except Exception as e:
            print(f"Ping standby: {e}")
        
        time.sleep(300) # 5 minuti

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
        print(f"Errore JSON: {e}")
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
    # Debutto (Conversione sicura a int)
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
    u_p = int(str(utente.get("popolarita", 0)).replace(".", ""))
    c_p = int(str(corretto.get("popolarita", 0)).replace(".", ""))
    res['popolarita'] = ["CORRETTO" if u_p == c_p else "ERRATO", "✅" if u_p == c_p else ("⬆️" if u_p < c_p else "⬇️"), f"{u_p:,}".replace(",", ".")]
