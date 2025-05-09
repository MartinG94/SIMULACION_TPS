import sys
import tkinter as tk
import pandas as pd
import openpyxl
from tkinter import filedialog
from tkinter import ttk
import random

# Clase principal que define la aplicación de simulación de bowling
# Esta clase maneja la interfaz gráfica y la lógica de la simulación
# Se utiliza tkinter para crear la interfaz gráfica
class BowlingSimulatorApp:
    def __init__(self, root):
        # Inicialización de la ventana principal
        self.root = root
        self.root.title("Simulador de Bowling")

        # Variables de entrada para la simulación
        # Probabilidades para la primera bola (valores entre 6 y 10)
        # Estos valores representan la probabilidad de derribar 6, 7, 8, 9 y 10 pinos respectivamente
        # Se suman a 100 para representar porcentajes
        self.probabilidades_primera_bola = [17, 10, 15, 18, 40]
        # Probabilidades para la segunda bola dependiendo de los pinos derribados en la primera
        # Se utilizan diccionarios para representar las probabilidades de derribar pinos
        # después de la primera bola
        self.probabilidades_segunda_bola = {
            6: [10, 20, 30, 30, 10],
            7: [2, 10, 45, 43],
            8: [4, 20, 76],
            9: [6, 94]
        }
        
        # Variables configurables por el usuario
        self.puntaje_strike = tk.IntVar(value=20) # Puntaje por strike
        self.puntaje_spare = tk.IntVar(value=15) # Puntaje por spare
        self.rondas = tk.IntVar(value=10) # Número de rondas por iteración
        self.puntaje_objetivo = tk.IntVar(value=120) # Puntaje objetivo para considerar éxito
        self.iteraciones = tk.IntVar(value=100000) # Número total de iteraciones de la simulación
        self.mostrar_iteraciones = tk.IntVar(value=10) # Número de iteraciones a mostrar en la tabla

        # Crear la interfaz gráfica
        self.create_widgets()

        # Centrar la ventana en la pantalla
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
        # Crear un marco (LabelFrame) para agrupar los parámetros
        # y configuraciones de la simulación
        frame_params = ttk.LabelFrame(self.root, text="Parámetros")
        frame_params.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Campos de entrada para los parámetros configurables
        # Se utilizan variables de tipo IntVar para almacenar los valores
        # y permitir su actualización en la interfaz gráfica
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

        # Botones para iniciar simulación, exportar resultados y salir
        # Se utilizan botones de ttk para mantener la consistencia con el estilo de tkinter
        ttk.Button(self.root, text="Iniciar Simulación", command=self.run_simulation).grid(row=1, column=0, pady=10)
        ttk.Button(self.root, text="Exportar a Excel", command=self.export_to_excel).grid(row=2, column=0, pady=10)
        ttk.Button(self.root, text="Salir", command=self.root.destroy).grid(row=3, column=0, pady=10)

        # Sección de resultados
        # Crear un marco (LabelFrame) para mostrar los resultados de la simulación
        # y la tabla de resultados
        self.result_frame = ttk.LabelFrame(self.root, text="Resultados")
        self.result_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky="nsew")

        # Tabla para mostrar los resultados de la simulación
        # Se utiliza ttk.Treeview para crear una tabla con encabezados
        # y permitir la selección de filas
        self.tree = ttk.Treeview(self.result_frame, columns=("Col0", "Col1", "Col2", "Col3", "Col4"), show="headings",
                                 selectmode="browse")
        self.tree.heading("Col0", text="N°")  # Nueva columna para numeración
        self.tree.heading("Col1", text="Iteración")
        self.tree.heading("Col2", text="Puntaje Total")
        self.tree.heading("Col3", text="Pinos Tirados")
        self.tree.heading("Col4", text="Probabilidad")
        self.tree.pack(fill="both", expand=True)

        # Estilo para la tabla (colorear filas incorrectas)
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.map("Treeview", background=[("selected", "blue")], foreground=[("selected", "white")])
        self.tree.tag_configure("below_target", background="red", foreground="white")

    def export_to_excel(self):
        # Obtener todos los datos de la grilla
        rows = []
        for item in self.tree.get_children():
            rows.append(self.tree.item(item)["values"])

        # Crear un DataFrame con los datos
        df = pd.DataFrame(rows, columns=["N°", "Iteración", "Puntaje Total", "Pinos Tirados", "Probabilidad"])

        # Guardar el archivo Excel
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False, engine='openpyxl')

    def run_simulation(self):
        # Limpiar resultados previos en la tabla
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Contador de éxitos (iteraciones que alcanzan el puntaje objetivo)
        exitos = 0

        # Total de iteraciones y cantidad de iteraciones a mostrar
        total_iteraciones = self.iteraciones.get()
        mostrar_ultimas = self.mostrar_iteraciones.get()

        # Determinar el rango de iteraciones a mostrar
        inicio_mostrar = max(0, total_iteraciones - mostrar_ultimas)

        # Simular cada iteración
        for i in range(total_iteraciones):
            puntaje_total = 0
            pinos_tirados = 0
            # Simular cada ronda dentro de la iteración
            # Se simulan las rondas según el número de rondas configurado
            # y se acumulan los puntajes y pinos derribados
            for _ in range(self.rondas.get()):
                puntaje_ronda, pinos = self.simular_ronda()
                puntaje_total += puntaje_ronda
                pinos_tirados += pinos

            # Verificar si el puntaje total supera el objetivo
            # Si el puntaje total es mayor o igual al objetivo, se cuenta como un éxito
            # Se utiliza la variable 'exitos' para llevar el conteo
            if puntaje_total >= self.puntaje_objetivo.get():
                exitos += 1

            # Mostrar solo las últimas N iteraciones en la tabla
            # Se utiliza la variable 'inicio_mostrar' para determinar el rango de iteraciones a mostrar
            # Se utiliza la variable 'tag' para marcar las filas que no alcanzan el puntaje objetivo
            if i >= inicio_mostrar:
                tag = "below_target" if puntaje_total < self.puntaje_objetivo.get() else ""
                self.tree.insert(
                    "", "end", values=(i - inicio_mostrar + 1, i + 1, puntaje_total, pinos_tirados, "-"), tags=(tag,)
                )

        # Calcular probabilidad final
        probabilidad = (exitos / total_iteraciones) * 100

        # Mostrar probabilidad en la tabla
        self.tree.insert(
            "", "end", values=("", "Probabilidad", "-", "-", f"{probabilidad:.2f}%")
        )

    def simular_ronda(self):
        # Simular una ronda de bowling
        # Elegir el número de pinos derribados en la primera bola
        # Usar random.choices para elegir un número de pinos derribados según las probabilidades
        # de la primera bola
        primera_bola = random.choices([6, 7, 8, 9, 10], weights=self.probabilidades_primera_bola, k=1)[0]
        if primera_bola == 10:
            return self.puntaje_strike.get(), 10

        # Elegir el número de pinos derribados en la segunda bola
        # Ajustar las probabilidades para la segunda bola según los pinos derribados en la primera
        # y asegurarse de que la suma no exceda 10
        segunda_bola = random.choices(
            range(11 - primera_bola),  # Ajustar para que las probabilidades sean coherentes
            weights=self.probabilidades_segunda_bola[primera_bola],
            k=1
        )[0]
        total_pinos = primera_bola + segunda_bola
        if total_pinos == 10: # Spare
            return self.puntaje_spare.get(), total_pinos
        return total_pinos, total_pinos

# Punto de entrada de la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = BowlingSimulatorApp(root)
    root.mainloop()