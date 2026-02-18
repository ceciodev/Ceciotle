def feedback_artista(utente, corretto):
    # Inizializziamo i feedback come stringhe vuote
    nome_feedback = ""
    anno_feedback = ""
    regione_feedback = ""
    gender_feedback = ""
    genere_feedback = ""
    componenti_feedback = ""

    # --- Nome ---
    u_nome = str(utente.get("nome") or "").strip().lower()
    c_nome = str(corretto.get("nome") or "").strip().lower()
    
    if u_nome == c_nome:
        nome_feedback = "Esatto!"
    elif u_nome and (u_nome in c_nome or c_nome in u_nome):
        nome_feedback = "Quasi, ci sei andato vicino!"
    else:
        nome_feedback = "Artista errato."

    # --- Debutto (Protezione contro errori di conversione) ---
    try:
        # Usiamo str() prima di int() per gestire eventuali oggetti non stringa
        u_deb = int(str(utente.get("debutto") or 0))
        c_deb = int(str(corretto.get("debutto") or 0))
        
        if u_deb != 0 and c_deb != 0:
            delta = u_deb - c_deb
            if delta == 0 and nome_feedback == "Esatto!":
                anno_feedback = f"Debutto: {c_deb}"
            elif -10 <= delta < 0:
                anno_feedback = "Ci sei quasi! Debutto più recente."
            elif 0 < delta <= 10:
                anno_feedback = "Ci sei quasi! Debutto meno recente."
    except (ValueError, TypeError):
        anno_feedback = "Data non disponibile"

    # --- Regione ---
    u_reg = str(utente.get("regione") or "").strip().lower()
    c_reg = str(corretto.get("regione") or "").strip().lower()
    if u_reg == c_reg and c_reg != "":
        regione_feedback = f"Viene da: {corretto.get('regione')}"

    # --- Gender ---
    u_gen = str(utente.get("gender") or "").strip().lower()
    c_gen = str(corretto.get("gender") or "").strip().lower()
    if u_gen == c_gen and c_gen != "":
        if c_gen == "m": gender_feedback = "♂"
        elif c_gen == "f": gender_feedback = "♀"
        else: gender_feedback = "Gruppo/Altro"

    # --- Genere musicale ---
    if nome_feedback == "Esatto!":
        genere_feedback = f"Genere: {corretto.get('genere', 'N/D')}"

    # --- Componenti ---
    try:
        u_comp = int(str(utente.get("componenti") or 0))
        c_comp = int(str(corretto.get("componenti") or 0))
        
        if u_comp != 0 and c_comp != 0:
            diff = u_comp - c_comp
            if diff == 0:
                componenti_feedback = f"Componenti: {c_comp}"
            else:
                componenti_feedback = "Più componenti" if diff < 0 else "Meno componenti"
    except (ValueError, TypeError):
        componenti_feedback = ""

    return nome_feedback, anno_feedback, regione_feedback, gender_feedback, genere_feedback, componenti_feedback
