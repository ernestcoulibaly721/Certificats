import os
from flask import Flask, render_template, request, send_file
import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS

app = Flask(__name__)

@app.route('/')
def index():
    # Cette page te servira de menu
    return render_template('traducteur.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    file = request.files['video']
    langue_dest = request.form.get('langue', 'en')
    
    if file:
        video_path = "entree.mp4"
        file.save(video_path)
        
        # 1. Extraction du son de ta vidéo
        clip = mp.VideoFileClip(video_path)
        clip.audio.write_audiofile("audio_temp.wav")
        
        # 2. IA : Écoute et transformation en texte
        r = sr.Recognizer()
        with sr.AudioFile("audio_temp.wav") as source:
            audio_data = r.record(source)
            texte_origine = r.recognize_google(audio_data, language="fr-FR")
            
        # 3. IA : Traduction du texte
        translator = Translator()
        traduction = translator.translate(texte_origine, dest=langue_dest).text
        
        # 4. IA : Création de la nouvelle voix traduite
        tts = gTTS(traduction, lang=langue_dest)
        tts.save("voix_finale.mp3")
        
        # 5. Fusion : Mettre la nouvelle voix sur l'image
        nouvel_audio = mp.AudioFileClip("voix_finale.mp3")
        video_finale = clip.set_audio(nouvel_audio)
        video_finale.write_videofile("video_traduite.mp4")
        
        return send_file("video_traduite.mp4", as_attachment=True)

    return "Erreur lors de l'envoi."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
            
