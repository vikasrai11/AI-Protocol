import time
import numpy as np
import sounddevice as sd
import google.generativeai as genai
from scipy.io.wavfile import write

# Configure Gemini API
genai.configure(api_key="Sender Gemini API key")

# Define frequency range for binary encoding
FREQ_0 = 1000  # Binary '0'
FREQ_1 = 2000  # Binary '1'
SAMPLE_RATE = 44100
DURATION = 1.0  # Duration of each signal in seconds

def text_to_binary(text):
    """Converts text to binary representation."""
    return ''.join(format(ord(c), '08b') for c in text)

def generate_tone(frequency):
    """Generates a sine wave for the given frequency."""
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), False)
    return 0.5 * np.sin(2 * np.pi * frequency * t)

def send_message(message):
    """Encodes and transmits message via sound."""
    binary_data = text_to_binary(message)
    signal = np.concatenate([generate_tone(FREQ_1 if bit == '1' else FREQ_0) for bit in binary_data])
    sd.play(signal, SAMPLE_RATE)
    write("message.wav", SAMPLE_RATE, signal)
    print(f"Sender Sent: {message}")
    time.sleep(len(signal) / SAMPLE_RATE + 1)  # Ensure receiver gets the message

def get_gemini_response(prompt):
    """Fetches a response from Gemini AI."""
    response = genai.chat(messages=[prompt])
    return response.last  # Get latest AI response

if __name__ == "__main__":
    message = "Hello, Gemini. How are you?"
    while True:
        send_message(message)
        message = get_gemini_response(message)
