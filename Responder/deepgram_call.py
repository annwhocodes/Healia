import os
import re
# from dotenv import load_dotenv 
from config import DEEPGRAM_KEY  
from typing import List, Optional
from deepgram import DeepgramClient, SpeakOptions
# load_dotenv()

def segmentTextBySentence(text:str) -> List[str]:
    """
    Splits the given text into a list of sentences.

    Args:
        text (str): The input text to segment.

    Returns:
        List[str]: A list of sentences.
    """
    return re.findall(r"[^.!?]+[.!?]", text)

def synthesize_audio(prompt:str, filename:str) -> Optional[dict]:
    """
    Converts the given text prompt into speech and saves it as an audio file.

    Args:
        prompt (str): The text to synthesize.
        filename (str): The output file path.

    Returns:
        Optional[dict]: API response if successful, None otherwise.
    """
    try:
        
        deepgram = DeepgramClient(DEEPGRAM_KEY)
        options = SpeakOptions(
            model="aura-asteria-en",
        )
        SPEAK_OPTIONS = {"text": prompt}

        response = deepgram.speak.rest.v("1").save(filename, SPEAK_OPTIONS, options)
        # print(response.to_json(indent=4))
        return response
    
    except Exception as e:
        print(f"Error in audio synthesis: {e}")
        print(e)
    
