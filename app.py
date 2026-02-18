import os
import json
import random
from flask import Flask, request, jsonify

app = Flask(__name__)

# Caricamento artisti
def carica_artisti():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "Artisti.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

artisti = carica_artisti()

# Seleziona artista del giorno
def scegli_artista_del_giorno():
    if not artisti:
        return None
    return random.choice(artisti)

# Feedback artista
def feedback_artista(utente, corretto):
    # Nome
    if utente.get("nome", "").lower() == corretto.get("nome", "").lower():
        nome_feedback = "Esatto!"
    elif utente.get("nome", "").lower() in corretto.get("nome", "").lower() or \
         corretto.get("nome", "").lower() in utente.get("nome", "").lower():
        nome_feedback = "Quasi, ci sei andato vicino!"
    else:
        nome_feedback = "Artista errato."

    # Anno debutto
    anno_feedback = ""
    if "debutto" in utente and "debutto" in corretto:
        try:
            delta = int(utente["debutto"]) - int(corretto["debutto"])
            if delta == 0 and utente.get("nome", "").lower() == corretto.get("nome", "").lower():
                anno_feedback = f"{corretto['debutto']}"
            elif -10 <= delta < 0:
                anno_feedback = "Ci sei quasi! Debutto più recente."
            elif 0 < delta <= 10:
                anno_feedback = "Ci sei quasi! Debutto meno recente."
        except ValueError:
            pass

    # Regione
    regione_feedback = ""
    if utente.get("regione", "").lower() == corretto.get("regione", "").lower():
        regione_feedback = f"Viene da: {corretto.get('regione', '')}"

    # Gender
    gender_feedback = ""
    if utente.get("gender", "").lower() == corretto.get("gender", "").lower():
        gender_value = corretto.get("gender", "").lower()
        simbolo = "♂" if gender_value == "m" else "♀" if gender_value == "f" else ""
        gender_feedback = simbolo

    # Genere musicale
    genere_feedback = ""
    if utente.get("nome", "").lower() == corretto.get("nome", "").lower():
        genere_corretto = corretto.get("genere", "").lower()
        if genere_corretto in ["cantautore", "cantautore/pop"]:
            genere_feedback = "L'artista è un cantautore"
        else:
            genere_feedback = f"La mia banda suona il {genere_corretto}"

    # Numero componenti
    componenti_feedback = ""
    if "componenti" in utente and "componenti" in corretto:
        try:
            diff = int(utente["componenti"]) - int(corretto["componenti"])
            if diff == 0:
                componenti_feedback = f"Numero componenti corretto: {corretto['componenti']}"
            elif diff < 0:
                componenti_feedback = "Il gruppo ha più componenti."
            else:
                componenti_feedback = "Il gruppo ha meno componenti."
        except ValueError:
            pass

    return {
        "nome": nome_feedback,
        "debutto": anno_feedback,
        "regione": regione_feedback,
        "gender": gender_feedback,
        "genere": genere_feedback,
        "componenti": componenti_feedback
    }

# Endpoint per giocare
@app.route("/gioca", methods=["POST"])
def gioca():
    data = request.json
    artista = scegli_artista_del_giorno()
    if not artista:
        return jsonify({"error": "Nessun artista disponibile"}), 404

    # Trova artista inserito dall'utente nel JSON
    utente_candidato = next(
        (a for a in artisti if a.get("nome", "").lower() == data.get("nome", "").lower()),
        {"nome": data.get("nome", "")}
    )

    feedback = feedback_artista(utente_candidato, artista)
    return jsonify(feedback)

# Endpoint base (puoi renderizzare una pagina HTML se vuoi)
@app.route("/")
def index():
    return "Benvenuto a Indovina l'Artista!"

# Flask server su Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
