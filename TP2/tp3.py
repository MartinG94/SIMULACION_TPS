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

        # Botones debajo de los parámetros
        ttk.Button(self.root, text="Iniciar Simulación", command=self.run_simulation).grid(row=1, column=0, pady=10,
                                                                                           sticky="ew")
        ttk.Button(self.root, text="Salir", command=self.root.destroy).grid(row=2, column=0, pady=10, sticky="ew")

        # Sección de resultados a la derecha
        self.result_frame = ttk.LabelFrame(self.root, text="Resultados")
        self.result_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky="nsew")

        self.canvas = tk.Canvas(self.result_frame)
        self.scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Vincular el evento de la rueda del mouse al Canvas
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(self, event):
        # Desplazar el Canvas con la rueda del mouse
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def run_simulation(self):
        # Lógica de simulación
        resultados = self.simular_bowling()

        # Contar iteraciones que superan el puntaje objetivo
        iteraciones_exitosas = sum(1 for resultado in resultados if resultado > self.puntaje_objetivo.get())
        probabilidad = (iteraciones_exitosas / self.mostrar_iteraciones.get()) * 100

        # Limpiar resultados previos
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Mostrar solo las últimas N iteraciones
        n = self.iteraciones.get()  # Número de iteraciones definido por el usuario
        ultimos_resultados = resultados[-n:]

        ttk.Label(self.scrollable_frame, text="Resultados de la Simulación:").grid(row=0, column=0, sticky="w")
        for i, resultado in enumerate(resultados):
            color = "red" if resultado < self.puntaje_objetivo.get() else "black"
            ttk.Label(self.scrollable_frame, text=f"Iteración {i + 1}: {resultado}", foreground=color).grid(row=i + 1,column=0,sticky="w")

        # Mostrar probabilidad
        ttk.Label(self.scrollable_frame, text=f"Probabilidad de superar el puntaje objetivo: {probabilidad:.2f}%",foreground="blue").grid(row=len(resultados) + 1, column=0, sticky="w")

    def simular_bowling(self):
        # Implementar la lógica de simulación aquí
        resultados = []
        for _ in range(self.mostrar_iteraciones.get()):
            puntaje_total = 0
            for _ in range(self.rondas.get()):
                puntaje_total += self.simular_ronda()
            resultados.append(puntaje_total)
        return resultados

    def simular_ronda(self):
        # Simular una ronda de bowling
        primera_bola = random.choices([6, 7, 8, 9, 10], weights=self.probabilidades_primera_bola, k=1)[0]
        if primera_bola == 10:
            return self.puntaje_strike.get()

        segunda_bola = random.choices(
            range(len(self.probabilidades_segunda_bola[primera_bola])),
            weights=self.probabilidades_segunda_bola[primera_bola],
            k=1
        )[0]
        total_pinos = primera_bola + segunda_bola
        if total_pinos == 10:
            return self.puntaje_spare.get()
        return total_pinos


if __name__ == "__main__":
    root = tk.Tk()
    app = BowlingSimulatorApp(root)

    # Centrar la ventana en la pantalla
    root.update_idletasks()  # Asegurarse de que la geometría esté actualizada
    ancho_ventana = root.winfo_width()
    alto_ventana = root.winfo_height()
    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()

    pos_x = (ancho_pantalla // 2) - (ancho_ventana // 2)
    pos_y = (alto_pantalla // 2) - (alto_ventana // 2)
    root.geometry(f"+{pos_x}+{pos_y}")

    root.mainloop()