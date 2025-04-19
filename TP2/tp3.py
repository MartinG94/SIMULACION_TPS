import tkinter as tk
from tkinter import ttk
import random


class BowlingSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Bowling")

        # Variables de entrada
        self.probabilidades_primera_bola = [17, 10, 15, 18, 40]
        self.probabilidades_segunda_bola = {
            6: [10, 20, 30, 30, 10],
            7: [2, 10, 45, 43],
            8: [4, 20, 76],
            9: [6, 94]
        }
        self.puntaje_strike = tk.IntVar(value=20)
        self.puntaje_spare = tk.IntVar(value=15)
        self.rondas = tk.IntVar(value=10)
        self.puntaje_objetivo = tk.IntVar(value=120)
        self.iteraciones = tk.IntVar(value=100000)
        self.mostrar_iteraciones = tk.IntVar(value=10)
        self.hora_inicio = tk.IntVar(value=1)

        # Crear interfaz
        self.create_widgets()

        # Centrar la ventana
        self.center_window()

    def center_window(self):
        """Centrar la ventana en la pantalla."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        # Sección de parámetros
        frame_params = ttk.LabelFrame(self.root, text="Parámetros")
        frame_params.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(frame_params, text="Puntaje Strike:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame_params, textvariable=self.puntaje_strike).grid(row=0, column=1)

        ttk.Label(frame_params, text="Puntaje Spare:").grid(row=1, column=0, sticky="w")
        ttk.Entry(frame_params, textvariable=self.puntaje_spare).grid(row=1, column=1)

        ttk.Label(frame_params, text="Rondas:").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame_params, textvariable=self.rondas).grid(row=2, column=1)

        ttk.Label(frame_params, text="Puntaje Objetivo:").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame_params, textvariable=self.puntaje_objetivo).grid(row=3, column=1)

        ttk.Label(frame_params, text="Iteraciones:").grid(row=4, column=0, sticky="w")
        ttk.Entry(frame_params, textvariable=self.iteraciones).grid(row=4, column=1)

        ttk.Label(frame_params, text="Mostrar Iteraciones:").grid(row=5, column=0, sticky="w")
        ttk.Entry(frame_params, textvariable=self.mostrar_iteraciones).grid(row=5, column=1)

        ttk.Label(frame_params, text="Hora Inicio:").grid(row=6, column=0, sticky="w")
        ttk.Entry(frame_params, textvariable=self.hora_inicio).grid(row=6, column=1)

        # Botones
        ttk.Button(self.root, text="Iniciar Simulación", command=self.run_simulation).grid(row=1, column=0, pady=10)
        ttk.Button(self.root, text="Salir", command=self.root.destroy).grid(row=2, column=0, pady=10)

        # Sección de resultados
        self.result_frame = ttk.LabelFrame(self.root, text="Resultados")
        self.result_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky="nsew")

        self.tree = ttk.Treeview(self.result_frame, columns=("Col1", "Col2", "Col3", "Col4"), show="headings")
        self.tree.heading("Col1", text="Ronda")
        self.tree.heading("Col2", text="Puntaje Total")
        self.tree.heading("Col3", text="Pinos Tirados")
        self.tree.heading("Col4", text="Probabilidad")
        self.tree.pack(fill="both", expand=True)

        # Estilo para colorear filas
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.map("Treeview", background=[("selected", "blue")], foreground=[("selected", "white")])
        self.tree.tag_configure("below_target", background="red", foreground="white")

    def run_simulation(self):
        # Limpiar resultados previos
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Contador de éxitos
        exitos = 0

        # Simular iteraciones
        for i in range(self.iteraciones.get()):
            puntaje_total = 0
            pinos_tirados = 0
            for _ in range(self.rondas.get()):
                puntaje_ronda, pinos = self.simular_ronda()
                puntaje_total += puntaje_ronda
                pinos_tirados += pinos

            # Verificar si se supera el puntaje objetivo
            if puntaje_total >= self.puntaje_objetivo.get():
                exitos += 1

            # Mostrar las primeras N iteraciones en la tabla
            if i < self.mostrar_iteraciones.get():
                tag = "below_target" if puntaje_total < self.puntaje_objetivo.get() else ""
                self.tree.insert(
                    "", "end", values=(i + 1, puntaje_total, pinos_tirados, "-"), tags=(tag,)
                )

        # Calcular probabilidad final
        probabilidad = (exitos / self.iteraciones.get()) * 100

        # Mostrar probabilidad en la tabla
        self.tree.insert(
            "", "end", values=("Probabilidad", "-", "-", f"{probabilidad:.2f}%")
        )

    def simular_ronda(self):
        # Simular una ronda de bowling
        primera_bola = random.choices([6, 7, 8, 9, 10], weights=self.probabilidades_primera_bola, k=1)[0]
        if primera_bola == 10:
            return self.puntaje_strike.get(), 10

        segunda_bola = random.choices(
            range(11 - primera_bola),  # Ajustar para que las probabilidades sean coherentes
            weights=self.probabilidades_segunda_bola[primera_bola],
            k=1
        )[0]
        total_pinos = primera_bola + segunda_bola
        if total_pinos == 10:
            return self.puntaje_spare.get(), total_pinos
        return total_pinos, total_pinos


if __name__ == "__main__":
    root = tk.Tk()
    app = BowlingSimulatorApp(root)
    root.mainloop()