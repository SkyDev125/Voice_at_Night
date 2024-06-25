import numpy as np
import speech_recognition as sr
import whisper
import torch
import pyttsx3
import sounddevice as sd
import globals

from scipy.io.wavfile import read
from queue import Queue
from time import sleep
import tempfile
import os


def get_tts_voices():
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    return {voice.name: voice.id for voice in voices}


def stt_main(
    voice_id,
    speech_rate,
    volume,
    model,
    english,
    energy_threshold,
    record_timeout,
    output_device,
):
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False
    source = sr.Microphone(sample_rate=16000)

    # Load / Download model
    audio_model = load_stt_model(model, english)

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
    stop_listening = recorder.listen_in_background(
        source, record_callback, phrase_time_limit=record_timeout
    )

    engine = init_tts_engine(output_device, voice_id, speech_rate, volume)

    # Create temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_file_path = temp_file.name
    temp_file.close()  # Close the file so it can be reopened later

    # Cue the user that we're ready to go.
    print("Model loaded.")
    print("Listening...")

    while globals.stt_running:
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
                play_tts(engine, text, temp_file_path)

            else:
                # Infinite loops are bad for processors, must sleep.
                sleep(0.25)
        except Exception as e:
            print(f"Error: {e}")
            break

    cleanup_temp_file(temp_file_path)
    stop_listening()
    print("Stopped STT-TTS")


def get_output_devices():
    devices = sd.query_devices()
    output_devices = {
        d["name"]: d["index"] for d in devices if d["max_output_channels"] > 0
    }
    if output_devices:
        return output_devices
    else:
        raise ValueError("No output devices found")


def init_tts_engine(output_device, voice_id, speech_rate, volume):
    sd.default.device = output_device
    engine = pyttsx3.init()
    engine.setProperty("voice", voice_id)
    engine.setProperty("rate", speech_rate)
    engine.setProperty("volume", volume)
    return engine


def load_stt_model(model, english):
    if model != "large" and english:
        model = model + ".en"
    audio_model = whisper.load_model(model)
    return audio_model


def play_tts(engine, text, temp_file_path):
    # Overwrite the temporary file with new speech output
    engine.save_to_file(text, temp_file_path)
    engine.runAndWait()

    # Read the audio data from the temporary file
    sample_rate, data = read(temp_file_path)

    # Play the audio data
    sd.play(data, sample_rate)
    sd.wait()


def cleanup_temp_file(temp_file_path):
    os.remove(temp_file_path)


if __name__ == "__main__":
    stt_main()
