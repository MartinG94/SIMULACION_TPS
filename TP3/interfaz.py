import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from simulador import SimuladorBowling
from utils import exportar_a_excel
from configuracion import ConfiguracionVentana

class BowlingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación Montecarlo - Bowling")
        self.root.geometry("900x650")

        self.parametros_config = {
                                    "probs_tiro1": [(6, 17), (7, 10), (8, 15), (9, 18), (10, 40)],
                                    "probs_tiro2": {
                                                    6: [(0,10),(1,20),(2,30),(3,30),(4,10)],
                                                    7: [(0,2),(1,10),(2,45),(3,43)],
                                                    8: [(0,4),(1,20),(2,76)],
                                                    9: [(0,6),(1,94)]
                                                    },
                                    "puntos": {"strike": 20, "spare": 15}
        }

        self.param_frame = ttk.LabelFrame(root, text="Parámetros de Simulación")
        self.param_frame.pack(fill="x", padx=10, pady=5)

        self.panel_principal = ttk.PanedWindow(root, orient=tk.VERTICAL)
        self.panel_principal.pack(fill="both", expand=True, padx=10, pady=5)

        self._crear_campos_parametros()
        self._crear_tabla_resultados()
        self._crear_panel_resultados()
        self.resultados = []
        
        # Variables para almacenar parámetros de simulación actual
        self.parametros_actuales = {}

        self.panel_principal.sashpos(0, 200)

    def _crear_campos_parametros(self):
        campos = [
            ("Rondas", "10"),
            ("Iteraciones", "100"),
            ("Desde Iteración", "1"),
            ("Cantidad a Mostrar", "10"),
            ("Objetivo de Puntos", "120")
        ]
        self.entries = {}
        for i, (label, default) in enumerate(campos):
            ttk.Label(self.param_frame, text=label).grid(row=0, column=i*2, padx=5, pady=5)
            entry = ttk.Entry(self.param_frame)
            entry.insert(0, default)
            entry.grid(row=0, column=i*2+1, padx=5, pady=5)
            self.entries[label] = entry

        ttk.Button(self.param_frame, text="Simular", command=self.simular).grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(self.param_frame, text="Exportar a Excel", command=self.exportar).grid(row=1, column=2, columnspan=2, pady=10)
        ttk.Button(self.param_frame, text="Configurar Parámetros", command=self.abrir_configuracion).grid(row=1, column=4, columnspan=2, pady=10)


    def _crear_tabla_resultados(self):
        frame_tabla = ttk.LabelFrame(self.panel_principal, text="Resultados de Simulación")
        self.panel_principal.add(frame_tabla, weight=40)  
        
        tabla_container = ttk.Frame(frame_tabla)
        tabla_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        scroll_y = ttk.Scrollbar(tabla_container)
        scroll_y.pack(side="right", fill="y")
        
        scroll_x = ttk.Scrollbar(tabla_container, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")
        
        self.tree = ttk.Treeview(tabla_container, 
                                columns=("Iter", "Ronda", "Rnd1", "P1", "Rnd2", "P2", "Pts", "Tot", "Supera"), 
                                show="headings", 
                                yscrollcommand=scroll_y.set,
                                xscrollcommand=scroll_x.set,
                                height=8)  
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, minwidth=60)
        
        self.tree.pack(fill="both", expand=True)

    def _crear_panel_resultados(self):
        self.resultados_frame = ttk.LabelFrame(self.panel_principal, text="Resultados Estadísticos")
        self.panel_principal.add(self.resultados_frame, weight=60)  
        
        contenido_frame = ttk.Frame(self.resultados_frame)
        contenido_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.lbl_probabilidad = ttk.Label(contenido_frame, 
                                        text="Probabilidad de superar el objetivo: N/A",
                                        font=("Arial", 13, "bold"))
        self.lbl_probabilidad.pack(pady=10, anchor="w")
        
        self.lbl_detalles = ttk.Label(contenido_frame, 
                                    text="Ejecute la simulación para ver los resultados.",
                                    font=("Arial", 11))
        self.lbl_detalles.pack(pady=5, anchor="w")
        
        ttk.Separator(contenido_frame, orient="horizontal").pack(fill="x", pady=10)
        
        ttk.Label(contenido_frame, text="Parámetros de la simulación:", 
                 font=("Arial", 11, "bold")).pack(anchor="w", pady=5)
        
        parametros_scroll_frame = ttk.Frame(contenido_frame)
        parametros_scroll_frame.pack(fill="both", expand=True, pady=5)
        
        scroll_y = ttk.Scrollbar(parametros_scroll_frame)
        scroll_y.pack(side="right", fill="y")
        
        self.txt_parametros = tk.Text(parametros_scroll_frame, font=("Arial", 10), 
                                     height=10, width=60, wrap="word", 
                                     yscrollcommand=scroll_y.set)
        self.txt_parametros.pack(fill="both", expand=True)
        scroll_y.config(command=self.txt_parametros.yview)
        self.txt_parametros.config(state="disabled")  

    def simular(self):
        self.tree.delete(*self.tree.get_children())
        try:
            rondas = int(self.entries["Rondas"].get())
            iteraciones = int(self.entries["Iteraciones"].get())
            desde = int(self.entries["Desde Iteración"].get())
            cantidad = int(self.entries["Cantidad a Mostrar"].get())
            objetivo = int(self.entries["Objetivo de Puntos"].get())
            hasta = desde + cantidad - 1

            if desde < 1 or cantidad < 1:
                raise ValueError("Los valores deben ser mayores a 0.")
            if desde > iteraciones:
                raise ValueError(f"Desde Iteración ({desde}) supera el total ({iteraciones}).")
            if hasta > iteraciones:
                hasta = iteraciones

            config = self.parametros_config
            sim = SimuladorBowling(config["probs_tiro1"], config["probs_tiro2"], config["puntos"], rondas)
            self.resultados = sim.simular(iteraciones, objetivo)
            
            # Guardar parámetros actuales
            self.parametros_actuales = {
                "rondas": rondas,
                "iteraciones": iteraciones,
                "objetivo": objetivo,
                "config": config
            }

            for fila in self.resultados[desde-1:hasta]:
                for nro_ronda, (rnd1, p1, rnd2, p2, pts, acumulado) in enumerate(fila["detalle"], start=1):
                    self.tree.insert("", "end", values=(
                        fila["iteracion"], nro_ronda,
                        round(rnd1, 4) if isinstance(rnd1, float) else rnd1,
                        p1,
                        round(rnd2, 4) if isinstance(rnd2, float) else '',
                        p2 if p2 != '-' else '',
                        pts, acumulado, fila["supera_objetivo"]
                    ))
            
            # Calcular y mostrar la probabilidad
            self._actualizar_resultados_estadisticos(objetivo, rondas, iteraciones)
            
            # Mostrar parámetros
            self._mostrar_parametros()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _actualizar_resultados_estadisticos(self, objetivo, rondas, iteraciones):
        # Obtener el último contador
        if self.resultados:
            ultimas_stats = self.resultados[-1]
            cantidad_superan = ultimas_stats["supera_objetivo"]
            probabilidad = (cantidad_superan / iteraciones) * 100
            
            # Actualizar etiquetas con los resultados
            self.lbl_probabilidad.config(
                text=f"Probabilidad de superar {objetivo} puntos en {rondas} rondas: {probabilidad:.2f}%"
            )
            
            self.lbl_detalles.config(
                text=f"De {iteraciones} simulaciones, {cantidad_superan} superaron el objetivo."
            )
        else:
            self.lbl_probabilidad.config(text="No hay datos de simulación disponibles.")
            self.lbl_detalles.config(text="Ejecute la simulación para ver los resultados.")

    def _mostrar_parametros(self):
        """Muestra los parámetros utilizados en la simulación"""
        if not self.parametros_actuales:
            return
            
        config = self.parametros_actuales["config"]
        
        # Crear texto con todos los parámetros básicos
        texto = f"""Parámetros utilizados:
• Rondas: {self.parametros_actuales['rondas']}
• Iteraciones: {self.parametros_actuales['iteraciones']}
• Objetivo: {self.parametros_actuales['objetivo']} puntos
• Puntos Strike: {config['puntos']['strike']}
• Puntos Spare: {config['puntos']['spare']}
• Probabilidades 1ª bola: {', '.join([f'{p} pinos: {prob}%' for p, prob in config['probs_tiro1']])}
"""
        
        # Agregar probabilidades de la segunda bola
        texto += "• Probabilidades 2ª bola:\n"
        for pinos1, probs in config['probs_tiro2'].items():
            texto += f"  - Si 1º tiro = {pinos1} pinos: {', '.join([f'{p} pinos: {prob}%' for p, prob in probs])}\n"
        
        # Actualizar el contenido del widget de texto
        self.txt_parametros.config(state="normal")  
        self.txt_parametros.delete(1.0, tk.END) 
        self.txt_parametros.insert(tk.END, texto) 
        self.txt_parametros.config(state="disabled")  

    def exportar(self):
        if not self.resultados:
            messagebox.showwarning("Advertencia", "Primero debe simular.")
            return
        ruta = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if ruta:
            exportar_a_excel(self.resultados, ruta, self.parametros_actuales)
            messagebox.showinfo("Éxito", "Archivo exportado correctamente.")

    def abrir_configuracion(self):
        ConfiguracionVentana(self.root, self.parametros_config, self.actualizar_config)

    def actualizar_config(self, nueva_config):
        self.parametros_config = nueva_config
        messagebox.showinfo("Configuración", "Los parámetros han sido actualizados correctamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BowlingApp(root)
    root.mainloop()