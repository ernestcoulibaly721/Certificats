import os
import asyncio
import traceback
from flask import Flask, render_template, request, send_file
import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator
import edge_tts

app = Flask(__name__)

# Dossier temporaire pour Render
TEMP_DIR = "/tmp"

async def generate_voice(text, voice_name, output_path):
    """Fonction pour générer la voix masculine avec Edge-TTS"""
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

    # Chemins des fichiers temporaires
    video_input = os.path.join(TEMP_DIR, "input_video.mp4")
    video_output = os.path.join(TEMP_DIR, "resultat_final.mp4")
    audio_temp = os.path.join(TEMP_DIR, "audio.wav")
    voice_temp = os.path.join(TEMP_DIR, "voice.mp3")
    
    file.save(video_input)
    
    try:
        # 1. Extraction Audio
        clip = mp.VideoFileClip(video_input)
        # On réduit la qualité audio pour aller plus vite
        clip.audio.write_audiofile(audio_temp, bitrate="50k", logger=None)
        
        # 2. Transcription (Audio -> Texte)
        r = sr.Recognizer()
        with sr.AudioFile(audio_temp) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="fr-FR")
        
        # 3. Traduction
        translator = Translator()
        translated_text = translator.translate(text, dest=langue_dest).text
        
        # 4. Choix de la voix d'HOMME selon la langue
        # Henri = Français Homme, Guy = Anglais Homme
        selected_voice = "fr-FR-HenriNeural" if langue_dest == 'fr' else "en-US-GuyNeural"
        
        # Génération de la voix (Asyncio est nécessaire pour edge-tts)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_voice(translated_text, selected_voice, voice_temp))
        loop.close()
        
        # 5. Montage final
        new_audio = mp.AudioFileClip(voice_temp)
        # On synchronise la durée de la voix avec la vidéo
        final_clip = clip.set_audio(new_audio)
        
        # Écriture de la vidéo (Optimisée pour Render Free)
        final_clip.write_videofile(
            video_output, 
            codec="libx264", 
            audio_codec="aac",
            fps=12, 
            preset="ultrafast", # Pour gagner du temps et éviter le timeout
            logger=None
        )
        
        # Nettoyage de la mémoire
        clip.close()
        new_audio.close()
        final_clip.close()
        
        return send_file(video_output, as_attachment=True)
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(error_details)
        return f"Erreur technique détaillée : {str(e)}"

if __name__ == '__main__':
    # On récupère le port donné par Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
