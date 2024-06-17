import tkinter as tk
import pyaudio
import numpy as np
from PIL import Image, ImageTk

class VoiceDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HUMAN AI")
        self.is_running = False

        self.canvas = tk.Canvas(self.root, width=400, height=400, bg='white')
        self.canvas.pack()

        # Crear un círculo azul más pequeño y de color más claro
        self.circle = self.canvas.create_oval(180, 350, 220, 390, fill='#428CFF', outline='white')
        self.canvas.tag_bind(self.circle, '<Button-1>', self.toggle_listen)

        # Crear el ícono de micrófono como un widget de Canvas
        self.microphone_icon = Image.open("mic_icon.png").resize((40, 40), Image.LANCZOS)
        self.microphone_icon = ImageTk.PhotoImage(self.microphone_icon)

        self.microphone_button = self.canvas.create_image(200, 370, image=self.microphone_icon)
        self.canvas.tag_bind(self.microphone_button, '<Button-1>', self.toggle_listen)

        # Coordenadas iniciales de la onda de audio
        self.wave = self.canvas.create_line(180, 370, 220, 370, fill='white', width=2)
        self.canvas.itemconfigure(self.wave, state='hidden')  # Ocultar la onda de audio al inicio

        self.audio_stream = None

    def toggle_listen(self, event):
        if not self.is_running:
            self.start_listen()
        else:
            self.stop_listen()
            self.canvas.itemconfigure(self.wave, state='hidden')  # Ocultar la onda de audio al detener la escucha
        self.root.update()  # Forzar la actualización de la interfaz gráfica

    def start_listen(self):
        self.is_running = True
        self.canvas.itemconfigure(self.microphone_button, state='hidden')
        self.audio_stream = self.open_mic_stream()
        self.update_wave()

    def stop_listen(self):
        self.is_running = False
        self.canvas.itemconfigure(self.microphone_button, state='normal')
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        self.audio_stream = None

    def open_mic_stream(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)
        return stream

    def update_wave(self):
        if self.is_running:
            data = self.audio_stream.read(1024, exception_on_overflow=False)
            data_np = np.frombuffer(data, dtype=np.int16)
            data_np = data_np / 32768.0  # Normalizar los datos

            # Escalar los datos para que se ajusten al tamaño del círculo
            scaled_data = data_np[::len(data_np)//200] * 80 + 370  # Toma 200 puntos y escala

            points = []
            for i, y in enumerate(scaled_data):
                x = 180 + (i * 40 / len(scaled_data))  # Ajusta x al tamaño del círculo
                points.append(x)
                points.append(y)

            # Calcula el centro vertical del círculo
            circle_center = (self.canvas.coords(self.circle)[1] + self.canvas.coords(self.circle)[3]) / 2
            
            # Desplaza la onda verticalmente para que esté en el centro del círculo
            self.canvas.coords(self.wave, *points[0:2], points[2], circle_center, *points[4:])
            self.canvas.itemconfigure(self.wave, state='normal')
            self.root.after(50, self.update_wave)
        else:
            self.canvas.itemconfigure(self.microphone_button, state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceDetectorApp(root)
    root.mainloop()
