import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS

def traduire_video(video_path, langue_destination='en'):
    # 1. Extraire l'audio
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile("temp_audio.wav")
    
    # 2. Transformer l'audio en texte
    r = sr.Recognizer()
    with sr.AudioFile("temp_audio.wav") as source:
        audio_data = r.record(source)
        texte_original = r.recognize_google(audio_data, language="fr-FR")
        
    # 3. Traduire le texte
    translator = Translator()
    traduction = translator.translate(texte_original, dest=langue_destination).text
    
    # 4. Créer la nouvelle voix
    tts = gTTS(traduction, lang=langue_destination)
    tts.save("voix_traduite.mp3")
    
    # 5. Remplacer l'audio dans la vidéo
    nouvel_audio = mp.AudioFileClip("voix_traduite.mp3")
    video_finale = video.set_audio(nouvel_audio)
    video_finale.write_videofile("video_traduite.mp4")
    
