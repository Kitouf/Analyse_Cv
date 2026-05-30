# app.py
# Point d'entrée de l'application.
# Lance avec : streamlit run app.py
 
import streamlit as st
from extractor import extraire_texte_pdf
from analyzer import analyser_en_stream, MODELE, MAX_CARACTERES_CV
 
# ─────────────────────────────────────────────
# Configuration de la page Streamlit
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CV Analyzer & Job Matcher",
    page_icon="🎯",
    layout="centered"
)
 
# ─────────────────────────────────────────────
# CSS personnalisé pour un rendu plus soigné
# ─────────────────────────────────────────────
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
    }
    h1 {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1a1a2e;
        margin-bottom: 0.2rem;
    }
    .sous-titre {
        color: #555;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .bloc-info {
        background-color: #f0f4ff;
        border-left: 4px solid #4f46e5;
        border-radius: 8px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #333;
    }
    div.stButton > button {
        background-color: #4f46e5;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #3730a3;
    }
</style>
""", unsafe_allow_html=True)
 
 
# ─────────────────────────────────────────────
# En-tête
# ─────────────────────────────────────────────
st.markdown("# 🎯 CV Analyzer & Job Matcher")
st.markdown(
    '<p class="sous-titre">Importe ton CV et colle une offre d\'emploi '
    'pour obtenir une analyse de compatibilité instantanée.</p>',
    unsafe_allow_html=True
)
 
# Bandeau d'info sur le modèle utilisé
st.markdown(
    f'<div class="bloc-info">🤖 Modèle actif : <strong>{MODELE}</strong> &nbsp;|&nbsp; '
    f'✂️ CV tronqué à <strong>{MAX_CARACTERES_CV} caractères</strong> pour la vitesse &nbsp;|&nbsp; '
    f'⚡ Réponse en streaming (affichage immédiat)</div>',
    unsafe_allow_html=True
)
st.markdown("---")
 
 
# ─────────────────────────────────────────────
# Étape 1 : Upload du CV
# ─────────────────────────────────────────────
st.markdown("### 📄 Étape 1 — Ton CV")
fichier_cv = st.file_uploader(
    label="Charge ton CV au format PDF",
    type=["pdf"],
    help="Seuls les fichiers PDF sont acceptés."
)
 
if fichier_cv is not None:
    with st.expander("👁️ Aperçu du texte extrait (optionnel)"):
        texte_extrait = extraire_texte_pdf(fichier_cv)
        if texte_extrait.strip():
            nb_caracteres = len(texte_extrait)
            st.caption(
                f"📏 {nb_caracteres} caractères extraits — "
                f"{'✂️ sera tronqué à ' + str(MAX_CARACTERES_CV) + ' chars pour l\'analyse' if nb_caracteres > MAX_CARACTERES_CV else '✅ taille ok, pas de troncature'}"
            )
            st.text_area(
                label="Texte brut extrait du PDF",
                value=texte_extrait[:3000] + ("..." if len(texte_extrait) > 3000 else ""),
                height=200,
                disabled=True
            )
        else:
            st.warning("⚠️ Aucun texte détecté. Le PDF est peut-être un scan image.")
 
 
# ─────────────────────────────────────────────
# Étape 2 : Offre d'emploi
# ─────────────────────────────────────────────
st.markdown("### 💼 Étape 2 — L'offre d'emploi")
offre_emploi = st.text_area(
    label="Colle ici le texte de l'offre d'emploi (les 1000 premiers caractères seront utilisés)",
    placeholder=(
        "Ex : Nous recherchons un développeur Python avec 2 ans d'expérience, "
        "maîtrise de FastAPI, Docker, et des bases en Machine Learning..."
    ),
    height=200
)
 
 
# ─────────────────────────────────────────────
# Étape 3 : Bouton d'analyse
# ─────────────────────────────────────────────
st.markdown("### 🚀 Étape 3 — Lancer l'analyse")
bouton_analyser = st.button("🔍 Analyser mon CV")
 
 
# ─────────────────────────────────────────────
# Étape 4 : Traitement et affichage en streaming
# ─────────────────────────────────────────────
if bouton_analyser:
 
    if fichier_cv is None:
        st.error("❌ Merci de charger un fichier CV en PDF.")
        st.stop()
 
    if not offre_emploi.strip():
        st.error("❌ Merci de coller le texte de l'offre d'emploi.")
        st.stop()
 
    # Relire le fichier (le curseur peut être à la fin après l'aperçu)
    fichier_cv.seek(0)
    texte_cv = extraire_texte_pdf(fichier_cv)
 
    if not texte_cv.strip():
        st.error(
            "❌ Impossible d'extraire le texte du PDF. "
            "Le fichier est peut-être un scan image."
        )
        st.stop()
 
    st.markdown("---")
    st.markdown("## 📊 Résultats de l'analyse")
    st.caption("⚡ Génération en cours — le texte s'affiche au fur et à mesure...")
 
    # st.write_stream() consomme le générateur et affiche chaque token en temps réel.
    # Pas de timeout possible : on lit au fil de l'eau.
    resultat_complet = st.write_stream(
        analyser_en_stream(texte_cv, offre_emploi)
    )
 
    # Bouton de téléchargement une fois la réponse complète
    if resultat_complet:
        st.markdown("---")
        st.download_button(
            label="💾 Télécharger l'analyse (Markdown)",
            data=resultat_complet,
            file_name="analyse_cv.md",
            mime="text/markdown"
        )
 
 
# ─────────────────────────────────────────────
# Pied de page
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small>CV Analyzer — Powered by Ollama · Projet portfolio étudiant</small></center>",
    unsafe_allow_html=True
)
