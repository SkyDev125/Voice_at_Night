import gtts
from pydub import AudioSegment
import sounddevice as sd
import numpy as np
import io

def play(audio_data, device_id):
    audio = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
    fs = audio.frame_rate

    if device_id is not None:
        sd.play(samples, samplerate=fs, device=device_id)
        sd.wait()  # Wait until the file is fully played
    else:
        raise ValueError(f"Device '{device_id}' not found.")

def text_to_speech(text: str) -> bytes:
    tts = gtts.gTTS(text, lang="en")
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)  # Rewind the buffer to the beginning
    return buf.read()

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

# Convert text to speech and play it directly from memory
audio_data = text_to_speech("Hello, World!")
play(audio_data, get_audio_input_device())