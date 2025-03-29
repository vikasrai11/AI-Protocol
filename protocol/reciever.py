import time
import numpy as np
import sounddevice as sd
import google.generativeai as genai
from scipy.signal import spectrogram

# Configure Gemini API
genai.configure(api_key="Reciever Gemini API key")

# Define frequency range for binary decoding
FREQ_0 = 1000  # Binary '0'
FREQ_1 = 2000  # Binary '1'
SAMPLE_RATE = 44100
DURATION = 1.5  # Increased duration for better capture

def decode_binary_from_sound(audio_signal):
    """Decodes binary data from received audio signal."""
    frequencies, _, Sxx = spectrogram(audio_signal, SAMPLE_RATE)

    # Normalize Sxx to avoid detection issues
    Sxx = Sxx / np.max(Sxx) if np.max(Sxx) > 0 else Sxx

    binary_data = ''
    for i in range(Sxx.shape[1]):  # Iterate over time slices
        freq_slice = Sxx[:, i]
        
        # Check energy in the target frequency bands
        freq_0_energy = np.sum(freq_slice[(frequencies >= FREQ_0 - 50) & (frequencies <= FREQ_0 + 50)])
        freq_1_energy = np.sum(freq_slice[(frequencies >= FREQ_1 - 50) & (frequencies <= FREQ_1 + 50)])

        if freq_1_energy > freq_0_energy:
            binary_data += '1'
        else:
            binary_data += '0'

    return binary_data

def binary_to_text(binary_data):
    """Converts binary data to readable text."""
    text = ''
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) == 8:
            text += chr(int(byte, 2))
    return text

def receive_message():
    """Listens for an incoming message, retrying if necessary."""
    print("Receiver Waiting for sender to start communication...")
    
    while True:
        audio_signal = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()
        
        binary_data = decode_binary_from_sound(audio_signal.flatten())

        if binary_data.count('1') > 5:  # Ensure at least some data was received
            message = binary_to_text(binary_data)
            print(f"Receiver Received: {message}")
            return message
        else:
            print("Receiver: No valid data received, retrying...")

def get_gemini_response(prompt):
    """Fetches a response from Gemini AI."""
    response = genai.chat(messages=[prompt])
    return response.last

if __name__ == "__main__":
    while True:
        received_message = receive_message()
        reply = get_gemini_response(received_message)
        print(f"Receiver Sent: {reply}")
