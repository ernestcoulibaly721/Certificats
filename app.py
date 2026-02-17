import os
import asyncio
import traceback
import time
from flask import Flask, render_template, request, send_file
import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator
import edge_tts

app = Flask(__name__)
TEMP_DIR = "/tmp"

async def generate_voice(text, voice_name, output_path):
    """Génère la voix masculine via Edge-TTS"""
    # On s'assure que le fichier n'existe pas déjà
    if os.path.exists(output_path):
        os.remove(output_path)
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)

@app.route('/')
def index():
    return render_template('traducteur.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    file = request.files['video']
    langue_dest = request.form.get('langue', 'en')
    
    if not file:
        return "Aucun fichier reçu."

    # ID unique pour éviter les mélanges de fichiers entre les tests
    timestamp = int(time.time())
    video_input = os.path.join(TEMP_DIR, f"in_{timestamp}.mp4")
    video_output = os.path.join(TEMP_DIR, f"out_{timestamp}.mp4")
    audio_temp = os.path.join(TEMP_DIR, f"audio_{timestamp}.wav")
    voice_temp = os.path.join(TEMP_DIR, f"voice_{timestamp}.mp3")
    
    file.save(video_input)
    
    try:
        # 1. Extraction Audio
        clip = mp.VideoFileClip(video_input)
        clip.audio.write_audiofile(audio_temp, bitrate="50k", logger=None)
        
        # 2. Transcription
        r = sr.Recognizer()
        with sr.AudioFile(audio_temp) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="fr-FR")
        
        # 3. Traduction
        translator = Translator()
        translated_text = translator.translate(text, dest=langue_dest).text
        
        # 4. CHOIX DE LA VOIX D'HOMME (FORCÉ)
        # Henri pour le français, Guy pour l'anglais
        if langue_dest == 'fr':
            selected_voice = "fr-FR-HenriNeural"
        else:
            selected_voice = "en-US-GuyNeural"
        
        # Exécution de la génération de voix
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_voice(translated_text, selected_voice, voice_temp))
        loop.close()
        
        # 5. Fusion de la nouvelle voix
        new_audio = mp.AudioFileClip(voice_temp)
        final_clip = clip.set_audio(new_audio)
        
        final_clip.write_videofile(
            video_output, 
            codec="libx264", 
            audio_codec="aac",
            fps=12, 
            preset="ultrafast",
            logger=None
        )
        
        # Fermeture des clips pour libérer Render
        clip.close()
        new_audio.close()
        final_clip.close()
        
        return send_file(video_output, as_attachment=True)
        
    except Exception as e:
        return f"Erreur : {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
