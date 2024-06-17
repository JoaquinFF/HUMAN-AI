import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class HumanAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Human AI")
        
        self.root.withdraw()  # Ocultar la ventana principal durante la animación

        self.create_startup_animation()
    
    def create_startup_animation(self):
        self.animation_window = tk.Toplevel(self.root)
        self.animation_window.overrideredirect(True)
        self.animation_window.geometry("600x400+350+200")

        self.label = tk.Label(self.animation_window, text="Human AI", font=("Helvetica", 32))
        self.label.pack(expand=True)

        # Simple animation: fade in effect
        self.alpha = 0.0
        self.animation_window.attributes('-alpha', self.alpha)
        self.fade_in()

    def fade_in(self):
        self.alpha += 0.01
        if self.alpha <= 1.0:
            self.animation_window.attributes('-alpha', self.alpha)
            self.root.after(10, self.fade_in)
        else:
            self.root.after(500, self.end_animation)  # Esperar un poco antes de terminar la animación

    def end_animation(self):
        self.animation_window.destroy()
        self.root.deiconify()  # Mostrar la ventana principal
        self.create_main_screen()

    def create_main_screen(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.start_button = ttk.Button(self.main_frame, text="Iniciar", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.stop_button = ttk.Button(self.main_frame, text="Detener", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.settings_button = tk.Button(self.main_frame, text="⚙️", command=self.settings, font=("Helvetica", 16))
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
    root.geometry("600x400+350+200")
    root.mainloop()
