import speech_recognition as sr

# Inicializar el reconocimiento
recognizer = sr.Recognizer()

def callback(recognizer, audio):
    try:
        # Usar el reconocimiento de Google (podrías cambiarlo por otro reconocedor)
        text = recognizer.recognize_google(audio, language='es-ES')
        print(f"Escuché: {text}")
        
        # Si se reconoce la palabra "detener", detener la escucha en segundo plano
        if text.lower() == "detener":
            stop_listening(wait_for_stop=False)
            print("Escucha detenida.")
            
    except sr.UnknownValueError:
        print("No entendí el audio")
    except sr.RequestError as e:
        print(f"No se pudo solicitar resultados; {e}")

# Configurar el micrófono para escuchar en tiempo real
mic = sr.Microphone()

# Escuchar en tiempo real y reconocer en segundo plano
print("Escuchando... Di 'detener' para detener la escucha.")
stop_listening = recognizer.listen_in_background(mic, callback)

# Mantener el programa corriendo
print("Presiona Ctrl+C para detener.")
try:
    while True:
        pass
except KeyboardInterrupt:
    stop_listening(wait_for_stop=True)
    print("Programa detenido.")
