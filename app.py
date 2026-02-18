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
    
    if not file: return "Aucun fichier reçu."

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
            text_origine = r.recognize_google(audio_data, language="fr-FR")
        
        # 3. Traduction
        translator = Translator()
        # Note: Googletrans supporte 'bm' (Bambara) de façon limitée
        translated = translator.translate(text_origine, dest=langue_dest)
        translated_text = translated.text
        
        # 4. Choix de la voix
        # Pour le Bambara (bm), on utilise une voix FR par défaut car la voix BM n'existe pas encore
        voices = {
            'fr': 'fr-FR-HenriNeural',
            'en': 'en-US-GuyNeural',
            'es': 'es-ES-AlvaroNeural',
            'bm': 'fr-FR-HenriNeural' 
        }
        selected_voice = voices.get(langue_dest, "en-US-GuyNeural")
        
        # 5. Génération Audio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_voice(translated_text, selected_voice, voice_temp))
        loop.close()
        
        # 6. Montage final
        new_audio = mp.AudioFileClip(voice_temp)
        final_clip = clip.set_audio(new_audio)
        
        # Optionnel: Ajout du texte sur la vidéo si c'est du Bambara
        if langue_dest == 'bm':
            txt_clip = mp.TextClip(translated_text, fontsize=24, color='white', bg_color='black', method='caption', size=clip.size)
            txt_clip = txt_clip.set_duration(clip.duration).set_position(('center', 'bottom'))
            final_clip = mp.CompositeVideoClip([final_clip, txt_clip])

        final_clip.write_videofile(video_output, codec="libx264", audio_codec="aac", fps=12, preset="ultrafast", logger=None)
        
        clip.close()
        new_audio.close()
        final_clip.close()
        
        return send_file(video_output, as_attachment=True)
        
    except Exception as e:
        return f"Détails de l'erreur : {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
        
