from enum import Enum

# TTS Configuration Settings

class Voice(Enum):
    HAZEL = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-GB_HAZEL_11.0"
    DAVID = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0"
    ZIRA = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"
    RYAN = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\TokenEnums\\NaturalVoiceEnumerator\\MicrosoftWindows.Voice.en-GB.Ryan.1"
    GUY = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\TokenEnums\\NaturalVoiceEnumerator\\MicrosoftWindows.Voice.en-US.Guy.1"

# Default voice
voice_id = Voice.GUY.value

# Speech rate (100 is default, lower is slower, higher is faster)
speech_rate = 150

# Pitch (50 is default, lower is lower pitch, higher is higher pitch)
pitch = 50

# Volume (1.0 is max, 0.0 is mute)
volume = 1