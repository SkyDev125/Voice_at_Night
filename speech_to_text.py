#! python3.7
import tts_config as config

import argparse
import os
import numpy as np
import speech_recognition as sr
import whisper
import torch
import pyttsx3
import sounddevice as sd


from queue import Queue
from time import sleep
from sys import platform

def get_audio_input_device():
    # This function will now list output devices and return the name of the first one
    devices = sd.query_devices()
    output_devices = [d for d in devices if d['max_output_channels'] > 0]
    if output_devices:
        # Find the device ID for the given device name
        print("Device: {}".format(output_devices[8]['name']))
        return output_devices[8]['index']
    else:
        raise ValueError("No output devices found")

def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="small", help="Model to use",
                        choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--non_english", action='store_true',
                        help="Don't use the english model.")
    parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=2,
                        help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=3,
                        help="How much empty space between recordings before we "
                                "consider it a new line in the transcription.", type=float)
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()

    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False
    source = sr.Microphone(sample_rate=16000)

    # Load / Download model
    model = args.model
    if args.model != "large" and not args.non_english:
        model = model + ".en"
    audio_model = whisper.load_model(model)

    record_timeout = args.record_timeout

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio:sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        data_queue.put(data)

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually but SpeechRecognizer provides a nice helper.
    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    # Cue the user that we're ready to go.
    print("Model loaded.\n")

    selected_device = get_audio_input_device()
    engine = pyttsx3.init()
    engine.setProperty('voice', config.voice_id)
    engine.setProperty('rate', config.speech_rate)
    engine.setProperty('volume', config.volume)
    engine.setProperty('pitch', config.pitch)

    while True:
        try:
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():
                
                # Combine audio data from queue
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()
                
                # Convert in-ram buffer to something the model can use directly without needing a temp file.
                # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
                # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                # Read the transcription.
                result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                text = result['text'].strip()

                engine.say(text)
                engine.runAndWait()

            else:
                # Infinite loops are bad for processors, must sleep.
                sleep(0.25)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
