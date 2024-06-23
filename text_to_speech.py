import gtts
import pygame

from time import sleep
from pydub import AudioSegment
from pygame import mixer, _sdl2 as devices

def play(file_path: str, device: str):
    print("Play: {}\r\nDevice: {}".format(file_path, device))
    pygame.mixer.init(devicename=device)
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    duration = get_audio_duration(file_path)
    sleep(duration)
    pygame.mixer.quit()

def text_to_speech(text):
    tts = gtts.gTTS(text, lang="en")
    tts.save('temp.mp3')

def get_audio_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    duration_in_seconds = len(audio) / 1000  # Converting milliseconds to seconds
    return duration_in_seconds

def get_audio_input_device():
    # Initializing mixer
    mixer.init()  

    # Selecting the specified device
    audio_devices = devices.audio.get_audio_device_names(False)
    selected_device = audio_devices[1]  

    # Quitting mixer
    mixer.quit()

    return selected_device