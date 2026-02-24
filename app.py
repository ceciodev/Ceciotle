import os
import json
import random
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
# Chiave segreta per le sessioni (fondamentale per i tentativi)
app.secret_key = os.environ.get("SECRET_KEY", "ceciotle_super_secret_2026")

def carica_artisti():
    """Carica il database dal file JSON"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "Artisti.json")
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                dati = json.load(f)
                return dati if isinstance(dati, list) else []
        print(f"ERRORE: File {file_path} non trovato!")
        return []
    except Exception as e:
        print(f"Errore caricamento JSON: {e}")
        return []

# Carichiamo la lista all'avvio
ARTISTI_LISTA = carica_artisti()

def feedback_artista(utente, corretto):
    """Confronta l'artista scelto con quello segreto"""
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

    # Popolarità (gestisce sia 'Popolarita' che 'popolarita')
    u_p = int(str(utente.get("Popolarita", utente.get("popolarita", 0))).replace(".", ""))
    c_p = int(str(corretto.get("Popolarita", corretto.get("popolarita", 0))).replace(".", ""))
    res['popolarita'] = ["CORRETTO" if u_p == c_p else "ERRATO", "✅" if u_p == c_p else ("⬆️" if u_p > c_p else "⬇️"), f"{u_p:,}".replace(",", ".")]
    
    return res

# --- ROTTE ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if not ARTISTI_LISTA:
        return "Database non trovato. Assicurati che Artisti.json sia nella cartella principale.", 500
    
    # Se la sessione è nuova, avvia partita
    if 'target' not in session:
        return redirect(url_for('restart'))

    if request.method == 'POST':
        if session.get('fine_giochi'):
            return redirect(url_for('index'))

        scelta_nome = request.form.get('nome', '').strip()
        # Cerca l'artista nel database (case insensitive)
        artista_scelto = next((a for a in ARTISTI_LISTA if a['nome'].lower() == scelta_nome.lower()), None)

        if artista_scelto:
            cronologia = session.get('cronologia', [])
            
            # Evita duplicati nello stesso gioco
            if not any(t['nome'] == artista_scelto['nome'] for t in cronologia):
                feedback = feedback_artista(artista_scelto, session['target'])
                cronologia.insert(0, {'nome': artista_scelto['nome'], 'feedback': feedback})
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
        return "Errore database", 500
    session['target'] = random.choice(ARTISTI_LISTA)
    session['cronologia'] = []
    session['vittoria'] = False
    session['fine_giochi'] = False
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Indispensabile per Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
