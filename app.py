import os
from flask import Flask, render_template, request, send_file
import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS

# C'EST CETTE LIGNE QUI MANQUAIT :
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('traducteur.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    file = request.files['video']
    langue_dest = request.form.get('langue', 'en')
    
    if file:
        video_path = "input_video.mp4"
        file.save(video_path)
        
        try:
            # 1. Extraction Audio (Optimisée)
            clip = mp.VideoFileClip(video_path)
            clip.audio.write_audiofile("audio_temp.wav", bitrate="50k")
            
            # 2. Reconnaissance vocale
            r = sr.Recognizer()
            with sr.AudioFile("audio_temp.wav") as source:
                audio_data = r.record(source)
                texte_origine = r.recognize_google(audio_data, language="fr-FR")
                
            # 3. Traduction
            translator = Translator()
            traduction = translator.translate(texte_origine, dest=langue_dest).text
            
            # 4. Création de la voix
            tts = gTTS(traduction, lang=langue_dest)
            tts.save("voix_traduit.mp3")
            
            # 5. Fusion légère (FPS réduit pour Render Free)
            nouvel_audio = mp.AudioFileClip("voix_traduit.mp3")
            video_finale = clip.set_audio(nouvel_audio)
            
            output_filename = "resultat_traduit.mp4"
            video_finale.write_videofile(output_filename, 
                                         codec="libx264", 
                                         audio_codec="aac",
                                         temp_audiofile='temp-audio.m4a', 
                                         remove_temp=True, 
                                         fps=15)
            
            # Libération immédiate de la mémoire
            clip.close()
            video_finale.close()
            
            return send_file(output_filename, as_attachment=True)
            
        except Exception as e:
            return f"Erreur technique : {str(e)}"

    return "Aucun fichier reçu."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
                
