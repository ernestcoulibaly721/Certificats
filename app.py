import os
import traceback
import time
from flask import Flask, render_template, request, send_file
import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment

app = Flask(__name__)
TEMP_DIR = "/tmp"

def transformer_en_voix_homme(input_path, output_path):
    """Baisse la tonalité pour simuler une voix d'homme"""
    sound = AudioSegment.from_file(input_path)
    # On baisse le pitch (octaves)
    new_sample_rate = int(sound.frame_rate * 0.8) # 0.8 = plus grave
    low_pitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    low_pitch_sound = low_pitch_sound.set_frame_rate(44100)
    low_pitch_sound.export(output_path, format="mp3")

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
    voice_raw = os.path.join(TEMP_DIR, f"voice_raw_{timestamp}.mp3")
    voice_man = os.path.join(TEMP_DIR, f"voice_man_{timestamp}.mp3")
    
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
        
        # 4. Génération Voix Google (Stable)
        tts = gTTS(translated_text, lang=langue_dest)
        tts.save(voice_raw)
        
        # 5. Transformation en voix d'homme
        transformer_en_voix_homme(voice_raw, voice_man)
        
        # 6. Fusion finale
        new_audio = mp.AudioFileClip(voice_man)
        final_clip = clip.set_audio(new_audio)
        
        final_clip.write_videofile(
            video_output, 
            codec="libx264", 
            audio_codec="aac",
            fps=12, 
            preset="ultrafast",
            logger=None
        )
        
        clip.close()
        new_audio.close()
        final_clip.close()
        
        return send_file(video_output, as_attachment=True)
        
    except Exception as e:
        return f"Erreur : {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
