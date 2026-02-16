import os
from flask import Flask, render_template, request, send_file
import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS

# ... (garde ton code précédent pour Yak Auto-Immo) ...

@app.route('/traducteur')
def page_traducteur():
    return render_template('traducteur.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    file = request.files['video']
    target_lang = request.form.get('langue', 'en')
    
    if file:
        path = "input_video.mp4"
        file.save(path)
        
        # 1. Extraction Audio
        clip = mp.VideoFileClip(path)
        clip.audio.write_audiofile("audio.wav")
        
        # 2. Reconnaissance Vocale (Français par défaut ici)
        r = sr.Recognizer()
        with sr.AudioFile("audio.wav") as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="fr-FR")
            
        # 3. Traduction
        translator = Translator()
        translated = translator.translate(text, dest=target_lang).text
        
        # 4. Création de la nouvelle voix
        tts = gTTS(translated, lang=target_lang)
        tts.save("translated_voice.mp3")
        
        # 5. Fusion finale
        new_audio = mp.AudioFileClip("translated_voice.mp3")
        final_video = clip.set_audio(new_audio)
        final_video.write_videofile("output_video.mp4")
        
        return send_file("output_video.mp4", as_attachment=True)

    return "Erreur lors du traitement."
        
