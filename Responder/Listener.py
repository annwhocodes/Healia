import whisper
import sounddevice as sd
import numpy as np

class WhisperListener:
    """
    A class to handle speech recognition using OpenAI's Whisper model.
    It records audio, processes it, and transcribes speech to text.
    """

    def __init__(self, model_size: str = "base") -> None:
        """
        Initializes the WhisperListener with a specified model.

        Args:
            model_size (str): Whisper model size. Options: 'tiny', 'base', 'small', 'medium', 'large'.
        """
        print("Loading Whisper model...")
        self.model = whisper.load_model(model_size)  # Load the model (options: tiny, base, small, medium, large)
        self.sampling_rate = 16000  # Whisper works best with 16kHz audio

    def record_audio(self, duration: int = 8):
        """
        Records audio from the microphone.

        Args:
            duration (int): Duration of recording in seconds.

        Returns:
            np.ndarray: Recorded audio as a NumPy array.
        """
        print("Recording...")
        audio = sd.rec(int(duration * self.sampling_rate), samplerate=self.sampling_rate, channels=1, dtype=np.float32)
        sd.wait()  # Wait for recording to complete
        print("Recording complete.")
        return audio.flatten()

    def transcribe_audio(self, audio: np.ndarray) -> str:
        """
        Transcribes the given audio using Whisper.

        Args:
            audio (np.ndarray): The recorded audio.

        Returns:
            str: Transcribed text.
        """
        print("Transcribing...")
        transcription = self.model.transcribe(audio)
        return transcription["text"].strip()

    def start_listening(self, duration=5):
        """
        Continuously records and transcribes speech.

        Args:
            duration (int): Duration of each recording cycle in seconds.
        """
        print("Listening for speech. Press Ctrl+C to stop.")
        try:
            while True:
                audio = self.record_audio(duration)
                text = self.transcribe_audio(audio)
                print(f"Transcription: {text}")
        except KeyboardInterrupt:
            print("\nStopping listener.")

# # Usage Example:
# listener = WhisperListener(model_size="tiny")  # Load the "base" model
# listener.start_listening(duration=10)  # Record & transcribe every 5 seconds
