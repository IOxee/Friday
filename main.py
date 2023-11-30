import speech_recognition as sr
from gtts import gTTS
import os
from transformers import pipeline

r = sr.Recognizer()

generator = pipeline('text-generation', model='gpt3.5')

def listen_speech():
    with sr.Microphone() as source:
        print("Escuchando...")
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            print("Dijiste: " + text)
            return text
        except sr.UnknownValueError:
            print("No entendí lo que dijiste")
            return None

def generate_response(text):
    responses = generator(text, max_length=50, num_return_sequences=1)
    return responses[0]['generated_text']

def speak(text):
    tts = gTTS(text=text, lang='es')
    tts.save("response.mp3")
    os.system("mpg321 response.mp3")

while True:
    input_text = listen_speech()
    if input_text:
        response = generate_response(input_text)
        print("Respuesta: ", response)
        speak(response)
