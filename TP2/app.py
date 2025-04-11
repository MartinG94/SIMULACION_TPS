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

from TP2.generadorNumeros import *

class GenerarNumerosAleatorios(QMainWindow):
    # Constructor
    def __init__(self):
        super().__init__()
        uic.loadUi("interfazR.ui", self)
        self.init_ui()
        self.generated_data = None

        self.centralwidget.layout().setStretch(0, 3)  # left_panel: 30%
        self.centralwidget.layout().setStretch(1, 7)  # right_panel: 70%

        # Configurar el gráfico
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)

        # Buscar el QWidget para el gráfico
        self.right_layout_widget = self.findChild(QWidget, "right_layout")
        layout = QVBoxLayout(self.right_layout_widget)
        layout.addWidget(self.canvas)

        self.update_parameters()

    # Configuración de la interfaz
    def init_ui(self):
        # Conectar el cambio del combo box a la actualización de parámetros
        self.dist_combo.currentIndexChanged.connect(self.update_parameters)

        # Conectar el botón de simulación
        self.sim_btn.clicked.connect(self.ejecutar_simulacion)

        # Botón cerrar (se mantiene igual)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet("""
            QPushButton {background-color: #9b1c31; color: white; padding: 8px; border-radius: 4px; margin-top: 15px;}
            QPushButton:hover {background-color: #7a1426;}
        """)

    # Función que ejecuta toda la simulación de forma secuencial
    def ejecutar_simulacion(self):
        # 1. Generar datos
        try:
            dist = self.dist_combo.currentText()
            size = self.size_input.value()

            if dist == "Uniforme [a, b]":
                a = float(self.param1_input.text())
                b = float(self.param2_input.text())
                if b <= a:
                    raise ValueError("b debe ser mayor que a")
                random_list = [generar_uniforme(a, b) for _ in range(size)]
                self.generated_data = np.array(random_list)

            elif dist == "Exponencial":
                lambd = float(self.param1_input.text())
                if lambd <= 0:
                    raise ValueError("λ debe ser mayor que 0")
                random_list = [generar_exponencial(lambd) for _ in range(size)]
                self.generated_data = np.array(random_list)

            elif dist == "Normal":
                mu = float(self.param1_input.text())
                sigma = float(self.param2_input.text())
                if sigma <= 0:
                    raise ValueError("σ debe ser mayor que 0")
                random_list = []
                iterations = (size + 1) // 2  # Redondeo hacia arriba
                for _ in range(iterations):
                    z1, z2 = generar_normal_bm(mu, sigma)
                    random_list.append(z1)
                    if len(random_list) < size:
                        random_list.append(z2)
                self.generated_data = np.array(random_list[:size])

            # Si la generación fue exitosa, informar al usuario
            QMessageBox.information(self, "Éxito", f"Datos generados correctamente (n={size})")

        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Error en los parámetros: {str(e)}")
            self.generated_data = None
            return  # Se interrumpe la simulación si hay error

        # 2. Mostrar datos (se muestran solo los primeros 100 valores)
        try:
            display_data = self.generated_data[:100]
            self.data_display.setPlainText("\n".join(map(str, display_data)))
            if len(self.generated_data) > 100:
                self.data_display.append("\n... (mostrando solo los primeros 100 valores)")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al mostrar los datos:\n{str(e)}")
            return

        # 3. Crear histograma y tabla de frecuencias utilizando los mismos intervalos
        try:
            num_bins = int(self.bins_combo.currentText())
            data = self.generated_data

            # Calcular el valor mínimo y máximo para determinar los intervalos
            data_min = data.min()
            data_max = data.max()
            # Crear bin_edges de forma uniforme
            bin_edges = np.linspace(data_min, data_max, num_bins + 1)

            self.ax.clear()  # Limpiar gráfico anterior

            # Generar histograma usando los intervalos calculados
            n, _, patches = self.ax.hist(
                data,
                bins=bin_edges,
                edgecolor='black',
                alpha=0.7,
                density=False,
                align='mid',
                color='#4682B4'
            )

            self.ax.set_title(
                f'Histograma - {self.dist_combo.currentText()}\n(n={len(data):,}, bins={num_bins})',
                fontsize=10, pad=12
            )
            self.ax.set_xlabel('Valores', fontsize=9)
            self.ax.set_ylabel('Frecuencia', fontsize=9)
            self.ax.grid(True, alpha=0.3)
            max_freq = max(n) if len(n) > 0 else 1
            self.ax.set_ylim(0, max_freq * 1.2)
            self.figure.tight_layout()
            self.ax.set_xticks(bin_edges)
            self.ax.xaxis.set_tick_params(rotation=45, labelsize=8)

            # Etiquetas de frecuencia en cada barra
            for freq, patch in zip(n, patches):
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

            # Crear tabla de frecuencias con los mismos intervalos
            freq_table_str = "Intervalo\t\tFrecuencia\n" + "-" * 50 + "\n"
            for i in range(len(n)):
                left = bin_edges[i]
                right = bin_edges[i + 1]
                # La convención aquí es: [left, right) para todos, salvo que se decida incluir el último punto
                interval_str = f"[{left:.4f}, {right:.4f})"
                # Para el último intervalo, si se desea incluir el máximo, se puede ajustar:
                if i == len(n) - 1:
                    interval_str = f"[{left:.4f}, {right:.4f}]"
                freq_table_str += f"{interval_str}\t{int(n[i])}\n"

            # Mostrar la tabla de frecuencias en la misma zona de datos
            self.data_display.setPlainText(freq_table_str)
            self.figure.subplots_adjust(bottom=0.15)
            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al crear el histograma:\n{str(e)}")

    # Para actualizar los parámetros según la distribución seleccionada
    def update_parameters(self):
        dist = self.dist_combo.currentText()
        if dist == "Uniforme [a, b]":
            self.param1_label.setText("Parámetro a:")
            self.param1_input.setText("0")
            self.param2_label.setText("Parámetro b:")
            self.param2_input.setText("1")
            self.param2_label.show()
            self.param2_input.show()

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
