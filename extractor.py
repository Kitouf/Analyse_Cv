# extractor.py
# Rôle : extraire le texte brut d'un fichier PDF uploadé via Streamlit.
# On utilise PyMuPDF (importé sous le nom "fitz").

import fitz  # PyMuPDF


def extraire_texte_pdf(fichier_uploade) -> str:
    """
    Prend un fichier uploadé par Streamlit (objet BytesIO-like)
    et retourne le texte complet du PDF sous forme de chaîne.

    Paramètre :
        fichier_uploade : l'objet retourné par st.file_uploader()

    Retour :
        str : le texte brut extrait page par page
    """
    # Lire les octets bruts du fichier uploadé
    octets = fichier_uploade.read()

    # Ouvrir le PDF depuis les octets (sans passer par le disque)
    document = fitz.open(stream=octets, filetype="pdf")

    texte_complet = []

    # Parcourir chaque page et extraire le texte
    for numero_page in range(len(document)):
        page = document[numero_page]
        texte_page = page.get_text()  # extraction du texte brut
        texte_complet.append(texte_page)

    # Fermer le document proprement
    document.close()

    # Joindre toutes les pages avec un saut de ligne entre chacune
    return "\n".join(texte_complet)
