import tts_config as config
import numpy as np
import speech_recognition as sr
import whisper
import torch
import pyttsx3
import sounddevice as sd

from scipy.io.wavfile import read
from queue import Queue
from time import sleep


def main():

    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = config.energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False
    source = sr.Microphone(sample_rate=16000)

    # Load / Download model
    audio_model = load_stt_model(config)

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio: sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        data_queue.put(data)

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually but SpeechRecognizer provides a nice helper.
    recorder.listen_in_background(
        source, record_callback, phrase_time_limit=config.record_timeout
    )

    engine = init_tts_engine()

    # Cue the user that we're ready to go.
    print("Model loaded.")
    print("Listening...")

    while True:
        try:
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():

                # Combine audio data from queue
                audio_data = b"".join(data_queue.queue)
                data_queue.queue.clear()

                # Convert in-ram buffer to something the model can use directly without needing a temp file.
                # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
                # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
                audio_np = (
                    np.frombuffer(audio_data, dtype=np.int16).astype(
                        np.float32
                    )
                    / 32768.0
                )

                # Transcribe the audio.
                result = audio_model.transcribe(
                    audio_np, fp16=torch.cuda.is_available()
                )
                text = result["text"].strip()
                

                print(text)
                play_tts(engine, text)

            else:
                # Infinite loops are bad for processors, must sleep.
                sleep(0.25)
        except KeyboardInterrupt:
            break


def get_input_devices():
    # This function will now list output devices and return the name of the first one
    devices = sd.query_devices()
    output_devices = [d for d in devices if d["max_output_channels"] > 0]
    if output_devices:
        # Find the device ID for the given device name
        print("Device: {}".format(output_devices[8]["name"]))
        return output_devices[8]["index"]
    else:
        raise ValueError("No output devices found")


def init_tts_engine():
    sd.default.device = get_input_devices()
    engine = pyttsx3.init()
    engine.setProperty("voice", config.voice_id)
    engine.setProperty("rate", config.speech_rate)
    engine.setProperty("volume", config.volume)
    return engine


def load_stt_model(config: config):
    model = config.model
    if config.model != "large" and config.english:
        model = model + ".en"
    audio_model = whisper.load_model(model)
    return audio_model


def play_tts(engine, text):
    engine.save_to_file(text, "speech.wav")
    engine.runAndWait()
    sample_rate, data = read("speech.wav")
    sd.play(data, sample_rate)
    sd.wait()


if __name__ == "__main__":
    main()
