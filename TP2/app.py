import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QLineEdit, QPushButton, QSpinBox,
                             QTextEdit, QMessageBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class RandomNumberGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Variables Aleatorias")
        self.setGeometry(100, 100, 900, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.init_ui()
        self.generated_data = None

        self.update_parameters()

    def init_ui(self):
        # Left panel - Input parameters
        self.left_panel = QGroupBox("Parámetros de Entrada")
        left_main_layout = QVBoxLayout()  # Layout principal vertical
        self.left_layout = QFormLayout()   # Layout de formulario

        # Distribution selection
        self.dist_label = QLabel("Distribución:")
        self.dist_combo = QComboBox()
        self.dist_combo.addItems(["Uniforme [a, b]", "Exponencial", "Normal"])
        self.dist_combo.currentIndexChanged.connect(self.update_parameters)
        self.left_layout.addRow(self.dist_label, self.dist_combo)

        # Sample size
        self.size_label = QLabel("Tamaño de muestra (≤1,000,000):")
        self.size_input = QSpinBox()
        self.size_input.setRange(1, 1000000)
        self.size_input.setValue(1000)
        self.left_layout.addRow(self.size_label, self.size_input)

        # Parameters (will be updated based on distribution)
        self.param1_label = QLabel("Parámetro a:")
        self.param1_input = QLineEdit("0")
        self.left_layout.addRow(self.param1_label, self.param1_input)

        self.param2_label = QLabel("Parámetro b:")
        self.param2_input = QLineEdit("1")
        self.left_layout.addRow(self.param2_label, self.param2_input)

        # Hide param2 initially (only shown for uniform distribution)
        self.param2_label.hide()
        self.param2_input.hide()

        # Number of bins
        self.bins_label = QLabel("Número de intervalos:")
        self.bins_combo = QComboBox()
        self.bins_combo.addItems(["10", "15", "20", "30"])
        self.left_layout.addRow(self.bins_label, self.bins_combo)

        # Generate button
        self.generate_btn = QPushButton("Generar Datos")
        self.generate_btn.clicked.connect(self.generate_data)
        self.left_layout.addRow(self.generate_btn)

        # Show data button
        self.show_data_btn = QPushButton("Mostrar Datos")
        self.show_data_btn.clicked.connect(self.show_data)
        self.left_layout.addRow(self.show_data_btn)

        # Create histogram button
        self.hist_btn = QPushButton("Crear Histograma")
        self.hist_btn.clicked.connect(self.create_histogram)
        self.hist_btn.setEnabled(False)
        self.left_layout.addRow(self.hist_btn)

        # Botón para cerrar el programa
        close_btn = QPushButton("Cerrar Programa")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 8px;
                border-radius: 4px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)

        # Agregar elementos al layout principal
        left_main_layout.addLayout(self.left_layout)
        left_main_layout.addStretch(1)  # Espaciador para empujar el botón hacia abajo
        left_main_layout.addWidget(close_btn)

        self.left_panel.setLayout(left_main_layout)

        # Right panel - Output
        self.right_panel = QGroupBox("Resultados")
        self.right_layout = QVBoxLayout()

        # Figure for histogram
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.right_layout.addWidget(self.canvas)

        # Data display
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)
        self.right_layout.addWidget(self.data_display)

        self.right_panel.setLayout(self.right_layout)

        # Add panels to main layout
        self.main_layout.addWidget(self.left_panel, 1)
        self.main_layout.addWidget(self.right_panel, 2)

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

    def generate_data(self):
        try:
            size = self.size_input.value()
            dist = self.dist_combo.currentText()

            if dist == "Uniforme [a, b]":
                a = float(self.param1_input.text())
                b = float(self.param2_input.text())
                if b <= a:
                    raise ValueError("b debe ser mayor que a")
                self.generated_data = np.random.uniform(a, b, size)

            elif dist == "Exponencial":
                lambd = float(self.param1_input.text())
                if lambd <= 0:
                    raise ValueError("λ debe ser mayor que 0")
                self.generated_data = np.random.exponential(1 / lambd, size)

            elif dist == "Normal":
                mu = float(self.param1_input.text())
                sigma = float(self.param2_input.text())
                if sigma <= 0:
                    raise ValueError("σ debe ser mayor que 0")
                self.generated_data = np.random.normal(mu, sigma, size)

            # Round to 4 decimal places
            self.generated_data = np.round(self.generated_data, 4)

            QMessageBox.information(self, "Éxito", f"Datos generados correctamente (n={size})")
            self.hist_btn.setEnabled(True)

        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Error en los parámetros: {str(e)}")
            self.generated_data = None
            self.hist_btn.setEnabled(False)

    def show_data(self):
        if self.generated_data is not None:
            # Show first 100 values to avoid freezing the GUI
            display_data = self.generated_data[:100]
            self.data_display.setPlainText("\n".join(map(str, display_data)))
            if len(self.generated_data) > 100:
                self.data_display.append("\n... (mostrando solo los primeros 100 valores)")
        else:
            QMessageBox.warning(self, "Advertencia", "No hay datos generados. Genere datos primero.")

    def create_histogram(self):
        if self.generated_data is None:
            QMessageBox.warning(self, "Advertencia", "No hay datos generados. Genere datos primero.")
            return

        try:
            # Obtener parámetros
            num_bins = int(self.bins_combo.currentText())
            data = self.generated_data

            # Limpiar gráfico anterior
            self.ax.clear()

            # Crear histograma con bins automáticos pero consistentes
            n, bin_edges, patches = self.ax.hist(
                data,
                bins=num_bins,
                edgecolor='black',
                alpha=0.7,
                density=False,
                align='mid'
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

            # Añadir etiquetas de frecuencia solo si hay espacio
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

            # Generar tabla de frecuencias optimizada
            freq_table = pd.cut(data, bins=bin_edges, include_lowest=True).value_counts().sort_index()
            freq_table_str = "Intervalo\t\tFrecuencia\n" + "-" * 50 + "\n"

            for interval, count in freq_table.items():
                freq_table_str += f"[{interval.left:.4f} - {interval.right:.4f}]\t{count}\n"

            # Actualizar visualización
            self.data_display.setPlainText(freq_table_str)
            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error crítico:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RandomNumberGenerator()
    window.show()
    sys.exit(app.exec_())