import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk

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

        self.settings_button = tk.Button(self.main_frame, image=self.settings_photo, command=self.settings, bd=0)
        self.settings_button.place(relx=1.0, x=-10, y=10, anchor="ne")

    def start(self):
        messagebox.showinfo("Iniciar", "Iniciando...")

    def stop(self):
        messagebox.showinfo("Detener", "Deteniendo...")

    def settings(self):
        messagebox.showinfo("Configuración", "Abriendo configuración...")

if __name__ == "__main__":
    root = tk.Tk()
    app = HumanAIApp(root)
    root.mainloop()
