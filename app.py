import os
from flask import Flask, render_template, request, jsonify

# --- PARTIE 1 : Configuration du Dossier de Téléchargement ---
# IMPORTANT : Ce dossier 'uploads' doit exister à la racine de votre dépôt GitHub.
UPLOAD_FOLDER = 'uploads' 
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- PARTIE 2 : Route d'Accueil ---
# Sert votre page HTML avec le formulaire.
@app.route('/')
def index():
    # Assurez-vous que votre fichier HTML est bien dans le dossier 'templates'
    return render_template('index.html')

# --- PARTIE 3 : Route de Traduction (Nouveau code pour recevoir le fichier) ---
# Cette fonction est appelée par le JavaScript (via fetch('/translate')).
@app.route('/translate', methods=['POST'])
def translate_video():
    # 1. Vérification que la clé 'video' est bien présente
    if 'video' not in request.files:
        return jsonify({'error': 'Le fichier vidéo est manquant dans la requête. (Clé "video" non trouvée)'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné.'}), 400

    if file:
        # 2. Sauvegarde du fichier reçu dans le dossier 'uploads'
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Sur Render, cela enregistre le fichier temporairement
        file.save(filepath) 
        
        # 3. Récupération des options envoyées par le JavaScript
        source_lang = request.form.get('source_lang')
        target_lang = request.form.get('target_lang')
        
        # 4. SIMULATION DE RÉUSSITE : Le fichier est reçu, mais la traduction n'est pas faite.
        # Nous renvoyons une URL de téléchargement imaginaire.
        translated_file_url = f"/downloads/translated_{filename}" 
        
        return jsonify({
            'success': True, 
            'message': f"Le serveur a bien reçu votre vidéo ({filename}). Prochaine étape : Lancer le modèle d'IA.",
            'download_url': translated_file_url 
        })

    return jsonify({'error': 'Une erreur inconnue est survenue lors de l\'enregistrement.'}), 500

if __name__ == '__main__':
    # Nous utilisons 'host=0.0.0.0' pour que Render puisse lancer l'application correctement.
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)
      
