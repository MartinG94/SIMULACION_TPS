import random
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import re

parametros = {
    "primera_bola": {6: 17, 7: 10, 8: 15, 9: 18, 10: 40},
    "segunda_bola": {
        6: {0: 10, 1: 20, 2: 30, 3: 30, 4: 10},
        7: {0: 2, 1: 10, 2: 45, 3: 43},
        8: {0: 4, 1: 20, 2: 76},
        9: {0: 6, 1: 94},
    },
    "puntos": {"strike": 20, "spare": 15, "normal": "suma"},
    "rondas": 10
}

# DataFrame completo para todas las simulaciones
resultado_df_completo = pd.DataFrame()
# DataFrame para las filas seleccionadas a mostrar
resultado_df_mostrado = pd.DataFrame()

def elegir_con_probabilidades(diccionario):
    valores = list(diccionario.keys())
    probabilidades = list(diccionario.values())
    return random.choices(valores, weights=probabilidades, k=1)[0]

def simular_partida():
    puntaje_total = 0
    for _ in range(parametros["rondas"]):
        primera = elegir_con_probabilidades(parametros["primera_bola"])
        if primera == 10:
            puntaje_total += parametros["puntos"]["strike"]
        else:
            segunda = elegir_con_probabilidades(parametros["segunda_bola"][primera])
            total = primera + segunda
            if total == 10:
                puntaje_total += parametros["puntos"]["spare"]
            else:
                puntaje_total += total if parametros["puntos"]["normal"] == "suma" else parametros["puntos"]["normal"]
    return puntaje_total

def validar_numero_positivo(valor, campo="Este campo"):
    """Validar que el valor sea un número entero positivo"""
    try:
        num = int(valor)
        if num <= 0:
            return False, f"{campo} debe ser un número positivo."
        return True, num
    except ValueError:
        return False, f"{campo} debe ser un número entero válido."

def validar_numero_flotante_positivo(valor, campo="Este campo"):
    """Validar que el valor sea un número flotante positivo"""
    try:
        num = float(valor)
        if num <= 0:
            return False, f"{campo} debe ser un número positivo."
        return True, num
    except ValueError:
        return False, f"{campo} debe ser un número válido."

def validar_campos_simulacion():
    """Validar todos los campos de la simulación"""
    # Validar N (partidas)
    valido, n = validar_numero_positivo(entry_n.get(), "N (partidas)")
    if not valido:
        return False, n
    
    # Validar umbral
    valido, umbral = validar_numero_positivo(entry_umbral.get(), "Umbral")
    if not valido:
        return False, umbral
    
    # Validar desde fila
    valido, desde = validar_numero_positivo(entry_desde.get(), "Desde fila")
    if not valido:
        return False, desde
    if desde > n:
        return False, "La fila de inicio no puede ser mayor que N."
    
    # Validar iteraciones a mostrar
    valido, iteraciones = validar_numero_positivo(entry_iteraciones.get(), "Iteraciones a mostrar")
    if not valido:
        return False, iteraciones
    if desde + iteraciones - 1 > n and n > 0:
        # No es un error crítico, se ajustará automáticamente
        pass
    
    return True, {"n": n, "umbral": umbral, "desde": desde, "iteraciones": iteraciones}

def abrir_configuracion():
    ventana_config = tk.Toplevel()
    ventana_config.title("Configuración de Parámetros")

    # Hacer que la ventana sea modal (bloquea la ventana principal)
    ventana_config.transient(ventana)
    ventana_config.grab_set()

    tk.Label(ventana_config, text="Probabilidades primera bola (6 a 10):").pack()
    frame_primera = tk.Frame(ventana_config)
    frame_primera.pack()
    entradas_primera = {}
    for val in range(6, 11):
        tk.Label(frame_primera, text=f"{val}:").grid(row=0, column=val-6)
        ent = tk.Entry(frame_primera, width=5)
        ent.insert(0, str(parametros["primera_bola"][val]))
        ent.grid(row=1, column=val-6)
        entradas_primera[val] = ent

    tk.Label(ventana_config, text="Probabilidades segunda bola (según primera bola):").pack()
    entradas_segunda = {}
    for idx, primero in enumerate(range(6, 10)):
        tk.Label(ventana_config, text=f"Primera bola = {primero}").pack()
        frame = tk.Frame(ventana_config)
        frame.pack()
        entradas_segunda[primero] = {}
        for j, seg in enumerate(parametros["segunda_bola"][primero].keys()):
            tk.Label(frame, text=f"{seg}:").grid(row=0, column=j)
            ent = tk.Entry(frame, width=5)
            ent.insert(0, str(parametros["segunda_bola"][primero][seg]))
            ent.grid(row=1, column=j)
            entradas_segunda[primero][seg] = ent

    tk.Label(ventana_config, text="Puntos:").pack()
    frame_puntos = tk.Frame(ventana_config)
    frame_puntos.pack()
    tk.Label(frame_puntos, text="Strike:").grid(row=0, column=0)
    strike_entry = tk.Entry(frame_puntos, width=5)
    strike_entry.insert(0, str(parametros["puntos"]["strike"]))
    strike_entry.grid(row=0, column=1)

    tk.Label(frame_puntos, text="Spare:").grid(row=0, column=2)
    spare_entry = tk.Entry(frame_puntos, width=5)
    spare_entry.insert(0, str(parametros["puntos"]["spare"]))
    spare_entry.grid(row=0, column=3)

    tk.Label(frame_puntos, text="Normal (número o 'suma'):").grid(row=0, column=4)
    normal_entry = tk.Entry(frame_puntos, width=8)
    normal_entry.insert(0, str(parametros["puntos"]["normal"]))
    normal_entry.grid(row=0, column=5)

    tk.Label(frame_puntos, text="Rondas:").grid(row=0, column=6)
    rondas_entry = tk.Entry(frame_puntos, width=5)
    rondas_entry.insert(0, str(parametros["rondas"]))
    rondas_entry.grid(row=0, column=7)

    def validar_probabilidades():
        """Validar que las probabilidades sumen 100%"""
        # Validar primera bola
        suma_primera = 0
        for val in entradas_primera:
            valido, num = validar_numero_flotante_positivo(entradas_primera[val].get(), f"Probabilidad de {val}")
            if not valido:
                return False, num
            suma_primera += num
        
        if not (99.5 <= suma_primera <= 100.5):  # Permitir un pequeño margen de error
            return False, f"Las probabilidades de la primera bola deben sumar 100% (actualmente suman {suma_primera}%)"
        
        # Validar segunda bola para cada posible primera bola
        for primero in entradas_segunda:
            suma_segunda = 0
            for seg in entradas_segunda[primero]:
                valido, num = validar_numero_flotante_positivo(entradas_segunda[primero][seg].get(), 
                                                            f"Probabilidad de {seg} después de {primero}")
                if not valido:
                    return False, num
                suma_segunda += num
            
            if not (99.5 <= suma_segunda <= 100.5):  # Permitir un pequeño margen de error
                return False, f"Las probabilidades de la segunda bola después de {primero} deben sumar 100% (actualmente suman {suma_segunda}%)"
        
        # Validar puntos
        valido, _ = validar_numero_positivo(strike_entry.get(), "Puntos por strike")
        if not valido:
            return False, _
            
        valido, _ = validar_numero_positivo(spare_entry.get(), "Puntos por spare")
        if not valido:
            return False, _
            
        normal = normal_entry.get()
        if normal != "suma" and not normal.isdigit():
            return False, "Puntos normales debe ser 'suma' o un número entero positivo"
            
        valido, _ = validar_numero_positivo(rondas_entry.get(), "Número de rondas")
        if not valido:
            return False, _
            
        return True, "OK"

    def guardar_config():
        valido, mensaje = validar_probabilidades()
        if not valido:
            messagebox.showerror("Error", mensaje)
            return
            
        try:
            for val in entradas_primera:
                parametros["primera_bola"][val] = float(entradas_primera[val].get())
            for primero in entradas_segunda:
                for seg in entradas_segunda[primero]:
                    parametros["segunda_bola"][primero][seg] = float(entradas_segunda[primero][seg].get())
            parametros["puntos"]["strike"] = int(strike_entry.get())
            parametros["puntos"]["spare"] = int(spare_entry.get())
            normal = normal_entry.get()
            parametros["puntos"]["normal"] = int(normal) if normal.isdigit() else normal
            parametros["rondas"] = int(rondas_entry.get())
            messagebox.showinfo("OK", "Parámetros guardados correctamente.")
            ventana_config.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(ventana_config, text="Validar", command=lambda: messagebox.showinfo("Validación", 
                                                                              "OK" if validar_probabilidades()[0] else validar_probabilidades()[1]), 
           bg="#FFA500", fg="white").pack(pady=5)
    tk.Button(ventana_config, text="Guardar", command=guardar_config, bg="#4CAF50", fg="white").pack(pady=5)
    tk.Button(ventana_config, text="Cancelar", command=ventana_config.destroy, bg="#f44336", fg="white").pack(pady=5)

def simular():
    global resultado_df_completo, resultado_df_mostrado
    
    # Validar los campos de entrada
    valido, resultado = validar_campos_simulacion()
    if not valido:
        messagebox.showerror("Error de validación", resultado)
        return
        
    N = resultado["n"]
    umbral = resultado["umbral"]
    desde = resultado["desde"]
    iteraciones = resultado["iteraciones"]
    
    try:
        # Actualizar barra de estado
        status_bar.config(text="Simulando... Por favor espere.")
        ventana.update_idletasks()  # Actualizar la interfaz
        
        supera_umbral = 0
        vector_estado_completo = []

        for i in range(1, N + 1):
            puntaje = simular_partida()
            supera = puntaje > umbral
            if supera:
                supera_umbral += 1

            # Guardar todas las simulaciones
            vector_estado_completo.append({
                'Iteración': i,
                'Puntaje': puntaje,
                'Supera umbral': supera
            })
            
            # Actualizar la barra de estado cada 1000 iteraciones
            if i % 1000 == 0 or i == N:
                status_bar.config(text=f"Simulando... {i}/{N} iteraciones completadas.")
                ventana.update_idletasks()

        # Guardar el dataset completo
        resultado_df_completo = pd.DataFrame(vector_estado_completo)
        
        # Ajustar "desde" si es necesario
        desde = min(max(1, desde), N)
        
        # Seleccionar solo las filas a mostrar
        filas_a_mostrar = list(range(desde-1, min(desde+iteraciones-1, N)))
        if N-1 not in filas_a_mostrar and N > 0:  # Añadir la última fila si no está
            filas_a_mostrar.append(N-1)
        
        resultado_df_mostrado = resultado_df_completo.iloc[filas_a_mostrar].copy()

        # Calcular probabilidad
        probabilidad = supera_umbral / N if N > 0 else 0

        # Actualizar la tabla
        for row in tree.get_children():
            tree.delete(row)

        for _, row in resultado_df_mostrado.iterrows():
            tree.insert("", "end", values=(row['Iteración'], row['Puntaje'], row['Supera umbral']))
            
        # Agregar la fila de probabilidad al final
        tree.insert("", "end", values=("", "", ""))
        tree.insert("", "end", values=("Resultados:", "", ""))
        tree.insert("", "end", values=(f"Prob. de superar {umbral} puntos:", f"{probabilidad:.4f}", f"{supera_umbral}/{N}"))

        # Etiqueta explícita en la interfaz que muestra la iteración actual
        lbl_iteracion.config(text=f"Última iteración completada: {N}")
        
        # Actualizar estado
        status_bar.config(text=f"Simulación completada. {N} iteraciones. Probabilidad: {probabilidad:.4f}")
        
        messagebox.showinfo("Resultado", f"Probabilidad de superar {umbral} puntos: {probabilidad:.4f} ({supera_umbral}/{N})")

    except Exception as e:
        status_bar.config(text="Error en la simulación.")
        messagebox.showerror("Error", str(e))

def exportar_excel():
    global resultado_df_completo
    if resultado_df_completo.empty:
        messagebox.showwarning("Advertencia", "Primero ejecutá una simulación.")
        return
        
    archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if archivo:
        try:
            status_bar.config(text="Exportando a Excel... Por favor espere.")
            ventana.update_idletasks()
            
            # Crear un DataFrame para el resumen
            N = len(resultado_df_completo)
            umbral = int(entry_umbral.get())
            supera_umbral = sum(resultado_df_completo['Supera umbral'])
            probabilidad = supera_umbral / N if N > 0 else 0
            
            # Agregar un resumen al final
            df_resumen = pd.DataFrame([
                {"Iteración": "", "Puntaje": "", "Supera umbral": ""},
                {"Iteración": "Resultados:", "Puntaje": "", "Supera umbral": ""},
                {"Iteración": f"Prob. de superar {umbral} puntos:", "Puntaje": f"{probabilidad:.4f}", "Supera umbral": f"{supera_umbral}/{N}"}
            ])
            
            # Concatenar el DataFrame original con el resumen
            resultado_final = pd.concat([resultado_df_completo, df_resumen], ignore_index=True)
            
            # Exportar a Excel
            resultado_final.to_excel(archivo, index=False)
            
            status_bar.config(text=f"Archivo exportado exitosamente: {archivo}")
            messagebox.showinfo("Exportado", f"Archivo guardado en: {archivo}")
        except Exception as e:
            status_bar.config(text="Error al exportar.")
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

# Función para validar entrada numérica en tiempo real
def validar_solo_numeros(P):
    if P == "" or re.match(r'^\d+$', P):
        return True
    return False

# Función para aplicar validación a un campo de entrada
def configurar_validacion_numeros(entry):
    vcmd = (entry.register(validar_solo_numeros), '%P')
    entry.config(validate='key', validatecommand=vcmd)

# Interfaz principal
ventana = tk.Tk()
ventana.title("Simulador de Bowling - Montecarlo")
ventana.geometry("800x700")

# Frame principal para organizar mejor los elementos
main_frame = tk.Frame(ventana, padx=10, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# Frame para parámetros
param_frame = tk.Frame(main_frame)
param_frame.pack(fill=tk.X, pady=5)

tk.Label(param_frame, text="N (partidas):").grid(row=0, column=0, sticky='e', padx=5, pady=5)
entry_n = tk.Entry(param_frame)
entry_n.grid(row=0, column=1, padx=5, pady=5)
entry_n.insert(0, "1000")  # Valor predeterminado
configurar_validacion_numeros(entry_n)

tk.Label(param_frame, text="Umbral:").grid(row=0, column=2, sticky='e', padx=5, pady=5)
entry_umbral = tk.Entry(param_frame)
entry_umbral.grid(row=0, column=3, padx=5, pady=5)
entry_umbral.insert(0, "150")  # Valor predeterminado
configurar_validacion_numeros(entry_umbral)

tk.Label(param_frame, text="Desde fila:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
entry_desde = tk.Entry(param_frame)
entry_desde.grid(row=1, column=1, padx=5, pady=5)
entry_desde.insert(0, "1")  # Valor predeterminado
configurar_validacion_numeros(entry_desde)

tk.Label(param_frame, text="Iteraciones a mostrar:").grid(row=1, column=2, sticky='e', padx=5, pady=5)
entry_iteraciones = tk.Entry(param_frame)
entry_iteraciones.grid(row=1, column=3, padx=5, pady=5)
entry_iteraciones.insert(0, "20")  # Valor predeterminado
configurar_validacion_numeros(entry_iteraciones)

# Frame para botones
button_frame = tk.Frame(main_frame)
button_frame.pack(fill=tk.X, pady=10)

btn_configurar = tk.Button(button_frame, text="⚙️ Configurar parámetros", command=abrir_configuracion, bg="orange")
btn_configurar.pack(side=tk.LEFT, padx=5)

btn_simular = tk.Button(button_frame, text="▶ Simular", command=simular, bg="#4CAF50", fg="white")
btn_simular.pack(side=tk.LEFT, padx=5)

btn_exportar = tk.Button(button_frame, text="📁 Exportar a Excel", command=exportar_excel, bg="#2196F3", fg="white")
btn_exportar.pack(side=tk.LEFT, padx=5)

# Etiqueta para mostrar iteración actual
lbl_iteracion = tk.Label(main_frame, text="Iteración actual: -", font=("Arial", 10, "bold"))
lbl_iteracion.pack(anchor=tk.W, pady=5)

# Frame para la tabla y scrollbar
tree_frame = tk.Frame(main_frame)
tree_frame.pack(fill=tk.BOTH, expand=True)

cols = ("Iteración", "Puntaje", "Supera umbral")
tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, anchor='center')

tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)
vsb.pack(side=tk.RIGHT, fill=tk.Y)

def on_treeview_click(event):
    item = tree.identify_row(event.y)
    if item:
        tree.selection_set(item)

tree.bind("<Button-1>", on_treeview_click)

# Etiqueta de estado al pie de la ventana
status_bar = tk.Label(ventana, text="Listo para simular", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

ventana.mainloop()