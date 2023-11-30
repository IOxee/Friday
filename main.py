import speech_recognition as sr
from gtts import gTTS
import os
import pygame
import requests

conversation_history = []

def generate_jarvis_style_prompt(user_input):
    global conversation_history
    # Agregar la entrada actual al historial
    conversation_history.append(f"Usuario: {user_input}")
    # Limitar el historial a las últimas N entradas para evitar que sea demasiado largo
    if len(conversation_history) > 5:
        conversation_history = conversation_history[-5:]
    
    # Incluir el estilo de Jarvis en el prompt
    prompt = (
        "Eres un asistente de inteligencia artificial avanzado con una capacidad "
        "de razonamiento excepcional, estilo elegante y un toque de humor. "
        "Tu propósito es asistir, proporcionar información y, en ocasiones, "
        "ofrecer un comentario ingenioso o una observación aguda. "
        "Mantienes siempre un tono respetuoso y profesional. "
        "Ahora, respondiendo en este estilo, afrontas la siguiente consulta:\n\n"
    )

    additional_prompt = (
        "\nEs importante proporcionar una respuesta completa y detallada a la consulta. "
        "Si se trata de una receta, incluir todos los ingredientes y pasos detallados es esencial. "
        "Si es una pregunta general, proporcionar información exhaustiva y relevante es clave.\n\n"
    )
    prompt_history = prompt + "\n".join(conversation_history) + additional_prompt + "Jarvis:"
    return prompt_history

def call_huggingface_api(user_input, api_key, model="bigscience/bloom"):
    prompt = generate_jarvis_style_prompt(user_input)
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": prompt,
        "options": {"use_cache": False, "return_full_text": True, "max_legnth": 20000},
        "model": model
    }
    response = requests.post(f"https://api-inference.huggingface.co/models/{model}", headers=headers, json=payload)
    if response.status_code == 200:
        generated_text = response.json()[0]['generated_text']
        # Procesar la respuesta
        response_text = generated_text[len(prompt):].strip()
        # Agregar la respuesta al historial
        conversation_history.append(f"Jarvis: {response_text}")
        return response_text
    else:
        return "Error al generar la respuesta."

API_KEY = "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"

def listen_speech(recognizer, microphone):
    with microphone as source:
        print("Escuchando...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language="es")
            print("Dijiste: " + text)
            return text
        except sr.UnknownValueError:
            print("No entendí lo que dijiste")
            return None

def generate_response(text):
    responses = generator(text, max_length=50, num_return_sequences=1)
    return responses[0]['generated_text']

def speak(text):
    if not text.strip():
        print("No hay texto para hablar.")
        return
    
    tts = gTTS(text=text, lang='es')  # Asegúrate de usar el idioma correcto aquí
    filename = "response.mp3"
    tts.save(filename)
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy(): 
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()  # Descargar la música para liberar el archivo
    os.remove(filename)  # Ahora podemos eliminar el archivo de forma segura

# Ciclo principal
recognizer = sr.Recognizer()
microphone = sr.Microphone()
pygame.mixer.init()

while True:
    text = listen_speech(recognizer, microphone)
    if text:
        response = call_huggingface_api(text, API_KEY)
        print("Respuesta: ", response)
        if response:
            speak(response)
