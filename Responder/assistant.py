import os
import cv2
import time
import numpy as np
import soundfile as sf
import streamlit as st
import sounddevice as sd
from Notion import NotionDB
from datetime import datetime
from typing import Optional, Dict
from langchain_groq import ChatGroq
from Listener import WhisperListener
from face_recog import FaceIdentifier
from config import GROQ_KEY, AUDIO_DIR,DB_NAME
from deepgram_call import synthesize_audio
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory

class FirstResponderAssistant:
    """
    A hospital responder system that:
    1. Detects patient identity through face recognition.
    2. Collects patient symptoms via natural conversation using LLM.
    3. Assigns the patient to the appropriate doctor based on symptoms.
    """
    def __init__(self) -> None:
        # Initialize components
        self.face_identifier = FaceIdentifier()
        self.listener = WhisperListener(model_size="base")
        self.llm = self._setup_llm()
        self.memory = ConversationBufferWindowMemory(k=5)
        self.current_patient: Optional[str] = None
        
        # Audio settings
        self.sampling_rate = 16000
        self.audio_duration = 5  # seconds
        
        # Initialize prompts
        self.system_prompt = """You are a professional first responder assisting in an emergency situation. 
        Your responses should be calm, clear, and focused on gathering critical information. 
        Ask one question at a time. 
        Prioritize assessing:
        - The patient's symptoms
        - Medical history (if available)
        - Emergency needs
        Keep responses brief and to the point.
        
        Important Points to remember:
        1. Refer to previous questions asked. DO NOT ask the same question again.
        2. Adapt questions based on the patient's responses.
        3. If the patient’s response is unclear, ask them to repeat or clarify.
        4. If you’ve gathered enough information, close the conversation politely and hand over to the appropriate doctor.
        """

        self.prompt_template = PromptTemplate(
            input_variables=["history", "input", "patient_name", "question_count"],
            template=self.system_prompt + """
            Current conversation:
            {history}
            Patient: {input}
            Important: You have {question_count} questions left. Please ask the most important ones to maximize information.
            Responder:"""
        )

    def _setup_llm(self) -> ChatGroq:
        """Sets up the LLM model for generating responses."""
        return ChatGroq(
            temperature=0.3,
            groq_api_key=GROQ_KEY,
            model_name="llama-3.3-70b-versatile"
        )
    
    def _delete_file(self, file_path: str) -> None:
        """Deletes a file if it exists."""
        if os.path.exists(file_path):
            os.remove(file_path)
            
    def _play_audio(self, filename: str) -> None:
        """Plays an audio file."""
        try:
            data, fs = sf.read(filename)
            sd.play(data, fs)
            sd.wait()
        except Exception as e:
            print(f"Error playing audio: {e}")

    def _get_llm_response(self, user_input: str, question_count: int) -> str:
        """
        Generates a response from the LLM model based on the conversation history.
        
        Args:
            user_input (str): The patient's input.
            question_count (int): Number of remaining questions.
        
        Returns:
            str: Generated LLM response.
        """
        history = self.memory.load_memory_variables({}).get("history", "")
        formatted_prompt = self.prompt_template.format(
            history=history,
            input=user_input,
            patient_name=self.current_patient or "Patient",
            question_count=question_count
        )
        response = self.llm.invoke(formatted_prompt)
        return response.content

    def summarize(self) -> Optional[str]:
        """
            Summarizes the given chat history to provide key information for a doctor.

            Args:
                chat (Dict[str, str]): A dictionary containing the chat history with key 'history'.

            Returns:
                Optional[str]: A summarized version of the chat, or None if an error occurs.
            """
    
        try:
            chat_history = self.memory.load_memory_variables({}).get("history", None)
            if not chat_history:
                print("No chat history available for summarization.")
                return None

            prompt = (
                "Summarize the following patient-agent conversation, highlighting key things:\n\n"
                f"{chat_history}\n\n"
                "Summary:"
            )
            response = self.llm.invoke(prompt)
            return response.content.strip()
        
        except Exception as e:
            print(f"Error summarizing chat: {e}")
            return None

    def start_assistance_flow(self) -> None:
        """
        Main loop for assisting the patient:
        - Detects face and identifies patient.
        - Collects symptoms and medical details.
        - Generates and plays LLM-generated responses.
        """
        print("Starting first responder assistant...")
        chat = ""
        try:
            self.current_patient = self.face_identifier.run_recognition()
            # print(f"Detected patient: {self.current_patient}")
            messages = st.container(height=300)
            messages.chat_message("Responder").write(f"Detected patient: {self.current_patient}")
            
            # Start the conversation
            print("Starting conversation...")
            question_count = 7
            response = f"Hi {self.current_patient}!, How can I help you today?"

            while question_count > 0:
                # Generate and play audio
                chat += "Responder: " + response + "\n"
                audio_file = os.path.join(AUDIO_DIR, f"response_{int(time.time())}.wav")
                synthesize_audio(response, audio_file)
                print(f"Responder: {response}")
                messages.chat_message("Responder").write(f"Responder: {response}")
                self._play_audio(audio_file)
                self._delete_file(audio_file)

                if "Thank you for your time" in response:
                    break

                # Listen for patient's response
                print("Listening...")
                audio = self.listener.record_audio(self.audio_duration)
                user_input = self.listener.transcribe_audio(audio).strip()
                chat += "Patient: " + user_input + "\n"
                print(f"Patient: {user_input}")
                messages.chat_message("Patient").write(f"Patient: {user_input}")

                if "quit" in user_input.lower():
                    print("Conversation terminated by patient.")
                    break

                # Save to memory and generate next question
                self.memory.save_context(
                    {"output": response},
                    {"input": user_input}
                )
                question_count -= 1
                response = self._get_llm_response(user_input, question_count)
                # print(f"Responder: {response}")
            
            audio_file = os.path.join(AUDIO_DIR, f"final_response.wav")
            if os.path.exists(audio_file):
                self._play_audio(audio_file)
            else:
                synthesize_audio("Thank you for your time, I will report your symptoms to the doctor.", audio_file)
                self._play_audio(audio_file)
            
            print("Session complete. Handoff to doctor.")
            
        finally:
            summary = self.summarize()
            if summary:
                notion_obj = NotionDB(DB_NAME)
                notion_obj.add_entry(
                    name=self.current_patient,
                    description=summary, 
                    date = datetime.now().strftime("%Y-%m-%d")
                )
            
            cv2.destroyAllWindows()