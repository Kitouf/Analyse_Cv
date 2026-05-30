# analyzer.py
# Rôle : construire le prompt et interroger Ollama en local via streaming.
# Le streaming évite le timeout : on lit la réponse au fur et à mesure.

import requests
import json

# Modèles légers recommandés pour CPU faible puissance :
#   ollama pull qwen2.5:1.5b   ← meilleur choix (~1 Go, ~30-45 sec)
#   ollama pull tinyllama       ← ultra léger (~600 Mo, ~20-30 sec)
#   ollama pull qwen2.5:3b     ← si tu veux plus de qualité (~2 Go, ~90 sec)
MODELE = "qwen2.5:1.5b"

# URL de l'API Ollama (toujours en local)
OLLAMA_URL = "http://localhost:11434/api/generate"

# Nombre max de caractères du CV envoyés au LLM.
# Réduire = moins de tokens = réponse plus rapide.
MAX_CARACTERES_CV = 1500


def tronquer_cv(texte_cv: str) -> str:
    """
    Tronque le texte du CV à MAX_CARACTERES_CV caractères.
    Un CV bien rédigé contient l'essentiel dans les 1500 premiers caractères.
    Cela réduit significativement le temps de traitement.
    """
    if len(texte_cv) <= MAX_CARACTERES_CV:
        return texte_cv
    texte_tronque = texte_cv[:MAX_CARACTERES_CV]
    return texte_tronque + "\n\n[... CV tronqué pour optimiser la vitesse d'analyse ...]"


def construire_prompt(texte_cv: str, offre_emploi: str) -> str:
    """
    Construit le prompt envoyé au LLM.
    On limite aussi la taille de l'offre d'emploi à 1000 caractères
    pour rester dans un volume raisonnable de tokens.
    """
    cv_court = tronquer_cv(texte_cv)
    offre_courte = offre_emploi[:1000]

    prompt = f"""Tu es un expert RH. Analyse ce CV par rapport à l'offre d'emploi.
Réponds en Markdown avec exactement ces sections :

## 📋 Résumé du profil
(2-3 phrases)

## 🛠️ Compétences détectées
**Techniques :** (liste courte)
**Fonctionnelles :** (liste courte)
**Niveau :** (Junior / Intermédiaire / Senior)

## ✅ Points forts
(3 points max)

## ⚠️ Points faibles
(3 points max)

## 🎯 Score de compatibilité
**Score : XX%**
(1 phrase d'explication)

## ❌ Compétences manquantes
(liste courte)

## 💡 Conseils d'amélioration
(3 conseils max)

CV :
{cv_court}

Offre :
{offre_courte}"""

    return prompt


def analyser_en_stream(texte_cv: str, offre_emploi: str):
    """
    Interroge Ollama en mode streaming et génère les morceaux de texte
    au fur et à mesure qu'ils arrivent.

    C'est un générateur Python (yield) : Streamlit l'affiche en temps réel
    avec st.write_stream(), sans aucun timeout.
    """
    prompt = construire_prompt(texte_cv, offre_emploi)

    # qwen3 active le "thinking mode" par défaut → on le désactive
    if "qwen3" in MODELE:
        prompt = "/no_think\n" + prompt

    corps_requete = {
        "model": MODELE,
        "prompt": prompt,
        "stream": True  # Mode streaming : réponse chunk par chunk
    }

    try:
        with requests.post(
            OLLAMA_URL,
            json=corps_requete,
            stream=True,
            timeout=30  # 30s juste pour établir la connexion initiale
        ) as reponse:

            reponse.raise_for_status()

            # Chaque ligne est un objet JSON avec un champ "response"
            for ligne in reponse.iter_lines():
                if ligne:
                    try:
                        chunk = json.loads(ligne)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue

    except requests.exceptions.ConnectionError:
        yield (
            "❌ **Erreur de connexion à Ollama.**\n\n"
            "Vérifie qu'Ollama est bien lancé :\n"
            "```\nollama serve\n```\n"
            f"Et que le modèle est téléchargé :\n```\nollama pull {MODELE}\n```"
        )
    except requests.exceptions.Timeout:
        yield (
            "❌ **Ollama ne répond pas.**\n\n"
            "Lance Ollama avec `ollama serve` puis réessaie."
        )
    except Exception as e:
        yield f"❌ **Erreur inattendue :** {str(e)}"