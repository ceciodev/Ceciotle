def feedback_artista(utente, corretto):
    # Nome
    u_nome = str(utente.get("nome", "")).lower()
    c_nome = str(corretto.get("nome", "")).lower()
    
    if u_nome == c_nome:
        nome_feedback = "Esatto!"
    elif u_nome in c_nome or c_nome in u_nome:
        nome_feedback = "Quasi, ci sei andato vicino!"
    else:
        nome_feedback = "Artista errato."

    # Debutto
    anno_feedback = ""
    try:
        u_deb = int(utente.get("debutto") or 0)
        c_deb = int(corretto.get("debutto") or 0)
        delta = u_deb - c_deb
        if delta == 0 and nome_feedback == "Esatto!":
            anno_feedback = f"Debutto: {c_deb}"
        elif -10 <= delta < 0:
            anno_feedback = "Ci sei quasi! Debutto più recente."
        elif 0 < delta <= 10:
            anno_feedback = "Ci sei quasi! Debutto meno recente."
    except (ValueError, TypeError):
        anno_feedback = "Anno non disponibile"

    # Regione
    regione_feedback = ""
    if str(utente.get("regione", "")).lower() == str(corretto.get("regione", "")).lower():
        regione_feedback = f"Viene da: {corretto.get('regione', 'Sconosciuto')}"

    # Gender
    gender_feedback = ""
    g_val = str(corretto.get("gender", "")).lower()
    if str(utente.get("gender", "")).lower() == g_val:
        gender_feedback = "♂" if g_val == "m" else "♀" if g_val == "f" else "Gruppo/Altro"

    # Genere musicale
    genere_feedback = ""
    if nome_feedback == "Esatto!":
        genere_feedback = f"Genere: {corretto.get('genere', 'N/D')}"

    # Componenti
    componenti_feedback = ""
    try:
        u_comp = int(utente.get("componenti") or 0)
        c_comp = int(corretto.get("componenti") or 0)
        diff = u_comp - c_comp
        if diff == 0:
            componenti_feedback = f"Componenti: {c_comp}"
        else:
            componenti_feedback = "Più componenti" if diff < 0 else "Meno componenti"
    except (ValueError, TypeError):
        componenti_feedback = "Dato componenti non valido"

    return nome_feedback, anno_feedback, regione_feedback, gender_feedback, genere_feedback, componenti_feedback
