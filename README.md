# 🎯 CV Analyzer 

Application web permettant d'analyser automatiquement un CV PDF et de le comparer à une offre d'emploi grâce à un LLM local (Ollama).

## ✨ Fonctionnalités
- 📄 Import et extraction de texte depuis un CV PDF
- 💼 Comparaison avec une offre d'emploi collée en texte
- 🛠️ Détection automatique des compétences techniques et fonctionnelles
- 🎯 Score de compatibilité en pourcentage
- ❌ Identification des compétences manquantes
- 💡 Conseils d'amélioration personnalisés
- ⚡ Affichage en streaming temps réel (aucun timeout)

## 🛠️ Stack technique
- **Python** — langage principal
- **Streamlit** — interface web
- **PyMuPDF** — extraction du texte PDF
- **Ollama** — LLM local (qwen2.5:1.5b par défaut)

## 🚀 Installation

# 1. Cloner le projet
git clone https://github.com/ton-pseudo/cv-analyzer.git
cd cv-analyzer

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Télécharger le modèle Ollama
ollama pull qwen2.5:1.5b

# 4. Lancer l'application
python -m streamlit run app.py

## ⚙️ Changer de modèle
Dans `analyzer.py`, ligne 13 :
MODELE = "qwen2.5:1.5b"  # léger et rapide
MODELE = "qwen2.5:3b"    # meilleure qualité
MODELE = "qwen3:4b"      # qualité maximale (plus lent)

## 📁 Structure
cv-analyzer/
├── app.py            # Interface Streamlit
├── analyzer.py       # Appel au LLM via Ollama
├── extractor.py      # Extraction du texte PDF
└── requirements.txt
