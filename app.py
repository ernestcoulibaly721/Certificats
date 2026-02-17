import os
from flask import Flask, render_template, request, send_file
import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import traceback

app = Flask(__name__)

# Dossier temporaire pour éviter les problèmes de droits
TEMP_DIR = "/tmp"

@app.route('/')
def index():
    return render_template('traducteur.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    file = request.files['video']
    langue_dest = request.form.get('langue', 'en')
    
    if file:
        video_input = os.path.join(TEMP_DIR, "input_video.mp4")
        video_output = os.path.join(TEMP_DIR, "resultat.mp4")
        audio_temp = os.path.join(TEMP_DIR, "audio.wav")
        voice_temp = os.path.join(TEMP_DIR, "voice.mp3")
        
        file.save(video_input)
        
        try:
            # 1. Extraction Audio
            clip = mp.VideoFileClip(video_input)
            clip.audio.write_audiofile(audio_temp, bitrate="50k")
            
            # 2. Transcription
            r = sr.Recognizer()
            with sr.AudioFile(audio_temp) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data, language="fr-FR")
            
            # 3. Traduction
            translator = Translator()
            translated_text = translator.translate(text, dest=langue_dest).text
            
            # 4. Voix
            tts = gTTS(translated_text, lang=langue_dest)
            tts.save(voice_temp)
            
            # 5. Montage final
            new_audio = mp.AudioFileClip(voice_temp)
            final_clip = clip.set_audio(new_audio)
            final_clip.write_videofile(video_output, codec="libx264", fps=12, logger=None)
            
            # Fermeture propre
            clip.close()
            final_clip.close()
            
            return send_file(video_output, as_attachment=True)
            
        except Exception as e:
            # Affiche l'erreur complète pour qu'on puisse la lire
            error_details = traceback.format_exc()
            print(error_details)
            return f"Désolé, erreur technique : {str(e)}"

    return "Fichier manquant."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
        
