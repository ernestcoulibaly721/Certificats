import os
from flask import Flask, render_template, request, send_file
import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS

app = Flask(__name__)

# --- Ta partie Certificats existante (si tu en as déjà une) ---

@app.route('/')
def index():
    return "Bienvenue sur ton portail : Certificats & Traduction Vidéo"

# --- NOUVELLE PARTIE : TRADUCTEUR DE VOIX ---

@app.route('/traducteur')
def page_traducteur():
    return render_template('traducteur.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    file = request.files['video']
    langue_dest = request.form.get('langue', 'en') # 'en' pour anglais, 'fr' pour français
    
    if file:
        video_path = "input_video.mp4"
        file.save(video_path)
        
        # 1. Extraire le son
        clip = mp.VideoFileClip(video_path)
        clip.audio.write_audiofile("audio_temp.wav")
        
        # 2. Écouter le son (Français -> Texte)
        r = sr.Recognizer()
        with sr.AudioFile("audio_temp.wav") as source:
            audio_data = r.record(source)
            texte_origine = r.recognize_google(audio_data, language="fr-FR")
            
        # 3. Traduire le texte
        translator = Translator()
        traduction = translator.translate(texte_origine, dest=langue_dest).text
        
        # 4. Créer la nouvelle voix artificielle
        tts = gTTS(traduction, lang=langue_dest)
        tts.save("voix_traduit.mp3")
        
        # 5. Coller la nouvelle voix sur la vidéo
        nouvel_audio = mp.AudioFileClip("voix_traduit.mp3")
        video_finale = clip.set_audio(nouvel_audio)
        video_finale.write_videofile("resultat_traduit.mp4")
        
        return send_file("resultat_traduit.mp4", as_attachment=True)

    return "Erreur lors du transfert."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
    
