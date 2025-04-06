# Build4Good 2025: AI-Powered Patient Intake System
![image](https://github.com/user-attachments/assets/34439661-ae84-4053-b4a7-0297a0258497)

## Project Overview

This project, developed for the Build4Good 2025 Hackathon, aims to streamline the patient intake process in hospitals by leveraging an AI-powered voice bot. It provides a conversational interface for patients arriving to describe their health concerns. The AI bot conducts a structured question-and-answer session, maintains a history of the conversation, and generates a concise summary. This summary, along with the patient's information and visit date, is then automatically added to a Notion database accessible by the doctor.

**Key Features:**

![image](https://github.com/user-attachments/assets/aad24035-ec6e-47dd-a075-ffb5e89c5b7a)

* **Voice-Based Interaction:** Natural language voice input for easy patient interaction.
* **Groq LLM Integration:** Real-time, high-performance language processing using Groq's infrastructure (Access to LLama 3.3, Qwen 2.5, etc).
* **OpenCV Face Detection:** Initial patient identification via face detection.
* **AWS S3 Image Storage:** Secure storage of patient images.
* **Structured Q\&A:** Guides patients through relevant questions to gather essential information.
* **Conversation History & Summarization:** Maintains a detailed record and generates concise summaries.
* **Notion Integration:** Automatically adds patient data and summaries to a doctor's Notion database.
* **Deepgram AI Voice Output:** Converts bot responses into human-like voice.
* **Streamlit UI:** User-friendly web interface for interaction.

## Use Case

Hospitals often face challenges managing walk-in patients, leading to long wait times and potential delays in care. This AI voice bot addresses this by:

* **Reducing Wait Times:** Patients can quickly provide their information and concerns, allowing staff to prioritize cases more efficiently.
* **Improving Data Accuracy:** The structured Q\&A ensures consistent and comprehensive data collection.
* **Enhancing Doctor Preparedness:** Doctors can review patient summaries in Notion before seeing the patient, improving their understanding of the case.
* **Proof of Concept (POC):** This project serves as a POC, demonstrating the potential of AI in streamlining patient intake.

## Technology Stack

| Technology         | Purpose                                     |
|--------------------|---------------------------------------------|
| Python             | Core programming language                   |
| Groq               | High-speed LLM inference and response generation |
| OpenCV             | Face detection and image processing        |
| AWS S3             | Secure storage of patient images            |
| Deepgram AI        | LLM response to human-like voice conversion |
| Streamlit          | Interactive user interface creation         |
| Notion API         | Notion database integration                 |

## Setup and Installation

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/reddheeraj/Responder.git
    cd Responder
    ```

2.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure APIs:**
    * Update `config.py` with your AWS S3 bucket name and credentials, GROQ API KEY, NOTION API KEY & Page ID, and DEEPGRAM API KEY.

4.  **Run the Application:**

    ```bash
    streamlit run app.py
    ```
