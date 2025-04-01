import sys
from PyQt5 import uic  # Importar uic
import numpy as np
import random 
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QComboBox, QLineEdit, QPushButton, QSpinBox,
                            QTextEdit, QMessageBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt

class GenerarNumerosAleatorios(QMainWindow):
    # Constructor
    def __init__(self):
        super().__init__()
        uic.loadUi("interfazR.ui", self)  # Carga el diseño desde el archivo .ui
        self.init_ui()
        self.generated_data = None
                
        # Para el histograma
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)

        # Buscar el QWidget en tu archivo .ui donde se debe mostrar el gráfico
        self.right_layout_widget = self.findChild(QWidget, "right_layout")
        
        # Asegurarse de que el layout de right_layout_widget esté vacío o adecuado
        # Añadir el FigureCanvas (el gráfico) dentro del QWidget correspondiente
        layout = QVBoxLayout(self.right_layout_widget)
        layout.addWidget(self.canvas)

        self.update_parameters()

    # Interacción con la interfaz
    def init_ui(self):
        # Conectar el cambio del combo box a la actualización de parámetros
        self.dist_combo.currentIndexChanged.connect(self.update_parameters)

        # Botón generar
        self.generate_btn.clicked.connect(self.generate_data)

        # Botón mostrar Datos
        self.show_data_btn.clicked.connect(self.show_data)
        self.show_data_btn.setEnabled(False)

        # Botón Crear Histograma
        self.hist_btn.clicked.connect(self.create_histogram)
        self.hist_btn.setEnabled(False)

        # Botón cerrar
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet("""
            QPushButton {background-color: #9b1c31; color: white; padding: 8px; border-radius: 4px; margin-top: 15px;}
            QPushButton:hover {background-color: #7a1426;}
        """)
    # Botón genearDatos
    def generate_data(self):
        try:
            # Tomar los valores de la Distribucion y tamaño de la muestra
            dist = self.dist_combo.currentText()
            size = self.size_input.value()

            # Generar Uniforme
            if dist == "Uniforme [a, b]":
                a = float(self.param1_input.text())
                b = float(self.param2_input.text())
                if b <= a:
                    raise ValueError("b debe ser mayor que a")
                #Generación uniforme corregida
                random_list = [random.uniform(a, b) for _ in range(size)]
                self.generated_data = np.array(random_list)


            # Generar Exponencial
            elif dist == "Exponencial":
                lambd = float(self.param1_input.text())
                if lambd <= 0:
                    raise ValueError("λ debe ser mayor que 0")
                self.generated_data = np.random.exponential(1 / lambd, size)

            # Generar Normal
            elif dist == "Normal":
                mu = float(self.param1_input.text())
                sigma = float(self.param2_input.text())
                if sigma <= 0:
                    raise ValueError("σ debe ser mayor que 0")
                self.generated_data = np.random.normal(mu, sigma, size)

            #Redondeamos valores a 4 decimales
            self.generated_data = np.round(self.generated_data, 4)

            QMessageBox.information(self, "Éxito", f"Datos generados correctamente (n={size})")
            self.hist_btn.setEnabled(True)
            self.show_data_btn.setEnabled(True)

        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Error en los parámetros: {str(e)}")
            # Vaciamos datos e inhabilitamos los demas botones
            self.generated_data = None
            self.hist_btn.setEnabled(False)
            self.show_data_btn.setEnabled(False)
        
    #Botón MostrarDatos
    def show_data(self):
        # Show first 100 values to avoid freezing the GUI
        display_data = self.generated_data[:100]
        self.data_display.setPlainText("\n".join(map(str, display_data)))
        if len(self.generated_data) > 100:
                self.data_display.append("\n... (mostrando solo los primeros 100 valores)")

    def create_histogram(self):
        
        try:
            # Obtener parámetros
            num_bins = int(self.bins_combo.currentText())
            data = self.generated_data

            # Limpiar gráfico anterior
            self.ax.clear()

            # Crear histograma
            n, bin_edges, patches = self.ax.hist(
                data,
                bins=num_bins,
                edgecolor='black',
                alpha=0.7,
                density=False,
                align='mid',
                color='#4682B4'
            )
            # Configuración del gráfico
            self.ax.set_title(
                f'Histograma - {self.dist_combo.currentText()}\n(n={len(data):,}, bins={num_bins})',
                fontsize=10, pad=12
            )
            self.ax.set_xlabel('Valores', fontsize=9)
            self.ax.set_ylabel('Frecuencia', fontsize=9)
            self.ax.grid(True, alpha=0.3)

            # Ajustar límites y espacios
            max_freq = max(n) if len(n) > 0 else 1
            self.ax.set_ylim(0, max_freq * 1.2)
            self.figure.tight_layout()

            # Formatear etiquetas del eje X
            bin_width = bin_edges[1] - bin_edges[0]
            self.ax.set_xticks(bin_edges)
            self.ax.xaxis.set_tick_params(rotation=45, labelsize=8)

            # Añadir etiquetas de frecuencia
            for i, (freq, patch) in enumerate(zip(n, patches)):
                if freq > 0:
                    x_center = patch.get_x() + patch.get_width() / 2
                    y_pos = freq + (0.02 * max_freq)
                    self.ax.text(
                        x_center,
                        y_pos,
                        f"{int(freq)}",
                        ha='center',
                        va='bottom',
                        fontsize=7,
                        rotation=90 if num_bins > 20 else 0
                    )

            # Redondear y asegurar que el primer bin empieza en 0
            bin_edges[0] = 0
            # Crear intervalos personalizados con pandas.IntervalIndex
            interval_index = pd.IntervalIndex.from_breaks(bin_edges, closed='right')  
            # Generar tabla de frecuencias manualmente sin que `pd.cut` ajuste los límites
            freq_table = pd.Series(pd.cut(data, bins=interval_index)).value_counts().sort_index()
            freq_table_str = "Intervalo\t\tFrecuencia\n" + "-" * 50 + "\n"

            for interval, count in freq_table.items():
                left = interval.left 
                right = interval.right
                freq_table_str += f"[{interval.left:.4f} - {interval.right:.4f}]\t{count}\n"

            # Actualizar visualización
            self.data_display.setPlainText(freq_table_str)
            self.figure.subplots_adjust(bottom=0.15) 
            # Redibujar el canvas con los nuevos datos
            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error crítico:\n{str(e)}")
    
    # Para actualizar los parametros en tiempo de ejecución
    def update_parameters(self):
        # Se lee la distribucion elejida
        dist = self.dist_combo.currentText()

        if dist == "Uniforme [a, b]":
            self.param1_label.setText("Parámetro a:")
            self.param1_input.setText("0")
            self.param2_label.setText("Parámetro b:")
            self.param2_input.setText("1")

        elif dist == "Exponencial":
            self.param1_label.setText("Parámetro λ (lambda):")
            self.param1_input.setText("1")
            self.param2_label.hide()
            self.param2_input.hide()

        elif dist == "Normal":
            self.param1_label.setText("Media (μ):")
            self.param1_input.setText("0")
            self.param2_label.setText("Desviación estándar (σ):")
            self.param2_input.setText("1")
            self.param2_label.show()
            self.param2_input.show()

# Función principal
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GenerarNumerosAleatorios()  
    window.show()
    sys.exit(app.exec_())