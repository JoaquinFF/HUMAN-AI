import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import pyaudio
import cv2
import subprocess

class HumanAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Human AI")
        self.root.geometry("600x400+350+200")
        self.root.withdraw()  # Ocultar la ventana principal al inicio
        
        self.create_startup_animation()
    
    def create_startup_animation(self):
        self.animation_window = tk.Toplevel(self.root)
        self.animation_window.overrideredirect(True)
        self.animation_window.geometry("600x400+350+200")
        self.animation_window.attributes('-alpha', 0.0)  # Iniciar con opacidad 0

        self.title_label = tk.Label(self.animation_window, text="Human AI", font=("Helvetica", 32))
        self.title_label.place(relx=0.5, rely=0.5, anchor='center')

        self.alpha = 0.0
        self.fade_in()

    def fade_in(self):
        self.alpha += 0.01
        if self.alpha <= 1.0:
            self.animation_window.attributes('-alpha', self.alpha)
            self.animation_window.after(10, self.fade_in)
        else:
            self.animation_window.after(500, self.end_animation)

    def end_animation(self):
        self.animation_window.destroy()
        self.root.deiconify()  # Mostrar la ventana principal
        self.create_main_screen()

    def create_main_screen(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.BOTTOM, pady=20)

        self.start_button = ttk.Button(self.button_frame, text="Iniciar", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=20)

        self.stop_button = ttk.Button(self.button_frame, text="Detener", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, padx=20)

        # Cargar la imagen del ícono de configuración
        self.settings_image = Image.open("setting.png")
        self.settings_image = self.settings_image.resize((24, 24), Image.LANCZOS)
        self.settings_photo = ImageTk.PhotoImage(self.settings_image)

        self.settings_button = tk.Button(self.main_frame, image=self.settings_photo, command=self.open_settings, bd=0)
        self.settings_button.place(relx=1.0, x=-10, y=10, anchor="ne")

    def start(self):
        messagebox.showinfo("Iniciar", "Iniciando...")

    def stop(self):
        messagebox.showinfo("Detener", "Deteniendo...")

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configuración")
        settings_window.geometry("400x300+450+250")

        # Obtener dispositivos de audio
        audio_devices = self.get_audio_devices()
        if not audio_devices:
            audio_devices = ["No se encontraron dispositivos de audio"]

        audio_label = tk.Label(settings_window, text="Seleccionar dispositivo de audio:")
        audio_label.pack(pady=10)

        self.selected_audio_device = tk.StringVar(settings_window)
        self.selected_audio_device.set(audio_devices[0])  # Opción por defecto
        audio_dropdown = tk.OptionMenu(settings_window, self.selected_audio_device, *audio_devices)
        audio_dropdown.pack(pady=10)

        # Obtener cámaras
        camera_devices = self.get_camera_devices()
        if not camera_devices:
            camera_devices = ["No se encontraron cámaras"]

        camera_label = tk.Label(settings_window, text="Seleccionar cámara:")
        camera_label.pack(pady=10)

        self.selected_camera_device = tk.StringVar(settings_window)
        self.selected_camera_device.set(camera_devices[0])  # Opción por defecto
        camera_dropdown = tk.OptionMenu(settings_window, self.selected_camera_device, *camera_devices)
        camera_dropdown.pack(pady=10)

        test_button = ttk.Button(settings_window, text="Testear", command=self.test_devices)
        test_button.pack(pady=20)

    def get_audio_devices(self):
        audio = pyaudio.PyAudio()
        devices = []
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info.get('maxInputChannels') > 0 and device_info.get('hostApi') == 0:
                devices.append(device_info.get('name'))
        audio.terminate()
        return devices

    def get_camera_devices(self):
        devices = []
        try:
            i = 0
            while True:
                cap = cv2.VideoCapture(i, cv2.CAP_ANY)
                if cap.isOpened():
                    # Obtener el nombre de la cámara si es posible
                    camera_name = f"Cámara {i}"  # Nombre genérico si no se puede obtener
                    devices.append(camera_name)
                    cap.release()
                    i += 1
                else:
                    break  # Dejar de intentar abrir cámaras si no se puede abrir más
        except Exception as e:
            print(f"Error al detectar cámaras: {str(e)}")

        if not devices:
            devices = ["No se encontraron cámaras"]  # Mensaje si no se detectan cámaras

        return devices

    def test_devices(self):
        audio_device = self.selected_audio_device.get()
        camera_device = self.selected_camera_device.get()

        messagebox.showinfo("Test de Dispositivos", f"Probando audio: {audio_device}\nProbando cámara: {camera_device}")

        # Ejecutar interfazPrueba.py como un proceso separado y pasar los dispositivos como argumentos
        subprocess.Popen(['python', 'interfazPrueba.py', '--audio', audio_device, '--camera', camera_device])


if __name__ == "__main__":
    root = tk.Tk()
    app = HumanAIApp(root)
    root.mainloop()
