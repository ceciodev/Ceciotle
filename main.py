import os
from flask import Flask

app = Flask(__name__)

# i tuoi endpoint qui

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
import json
import random


def carica_artisti():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "Artisti.json")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Errore: file '{file_path}' non trovato.")
        return []
    except json.JSONDecodeError:
        print(f"Errore: file '{file_path}' non è un JSON valido.")
        return []


def scegli_artista_del_giorno(artisti):
    if not artisti:
        return None
    return random.choice(artisti)


def feedback_artista(utente, corretto):
    # Nome
    if utente.get("nome", "").lower() == corretto.get("nome", "").lower():
        nome_feedback = "Esatto!"
    elif (utente.get("nome", "").lower() in corretto.get("nome", "").lower() or
          corretto.get("nome", "").lower() in utente.get("nome", "").lower()):
        nome_feedback = "Quasi, ci sei andato vicino!"
    else:
        nome_feedback = "Artista errato."

    # Anno di debutto
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

    # Sesso (gender)
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

    return nome_feedback, anno_feedback, regione_feedback, gender_feedback, genere_feedback, componenti_feedback


def gioca_a_indovina_artista(artista, artisti):
    if not artista:
        print("Nessun artista disponibile per il gioco.")
        return

    print("Indovina l'artista!")
    tentativi = 10
    nome_artista = artista.get("nome")

    for i in range(tentativi):
        nome_input = input(f"Tentativo {i + 1}/{tentativi} - Nome: ").strip()

        utente_candidato = next(
            (a for a in artisti if a.get("nome", "").lower() == nome_input.lower()),
            {"nome": nome_input}
        )

        nome_fb, anno_fb, regione_fb, gender_fb, genere_fb, componenti_fb = feedback_artista(
            utente_candidato, artista
        )

        print(f"Nome: {nome_fb}")
        if anno_fb:
            print(f"Debutto: {anno_fb}")
        if regione_fb:
            print(f"Regione: {regione_fb}")
        if gender_fb:
            print(f"Sesso: {gender_fb}")
        if genere_fb:
            print(f"Genere: {genere_fb}")
        if componenti_fb:
            print(f"Componenti: {componenti_fb}")

        if nome_fb == "Esatto!":
            print("RISPOSTA ESATTA! HAI VINTO!")
            return

    print(f"Hai esaurito i tentativi! L'artista corretto era: {nome_artista}")


def main():
    artisti = carica_artisti()
    artista = scegli_artista_del_giorno(artisti)
    gioca_a_indovina_artista(artista, artisti)


if __name__ == "__main__":
    main()

