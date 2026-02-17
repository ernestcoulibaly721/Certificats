# Modifie cette partie dans ton app.py
def process_video():
    # ... début du code ...
    
    # 1. Extraction Audio (Ajoute 'bitrate' pour que ce soit plus rapide)
    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile("audio_temp.wav", bitrate="50k")
    
    # ... transcription et traduction ...

    # 4. Création de la voix
    tts = gTTS(traduction, lang=langue_dest)
    tts.save("voix_traduit.mp3")
    
    # 5. Fusion optimisée pour les serveurs gratuits
    nouvel_audio = mp.AudioFileClip("voix_traduit.mp3")
    video_finale = clip.set_audio(nouvel_audio)
    
    # AJOUTE CES PARAMÈTRES ici pour économiser la RAM :
    video_finale.write_videofile("resultat_traduit.mp4", 
                                 codec="libx264", 
                                 audio_codec="aac",
                                 temp_audiofile='temp-audio.m4a', 
                                 remove_temp=True, 
                                 fps=15) # On baisse les images par seconde pour que ça passe
    
    # TRÈS IMPORTANT : Ferme les fichiers pour libérer la mémoire
    clip.close()
    video_finale.close()
    
    return send_file("resultat_traduit.mp4", as_attachment=True)
    
