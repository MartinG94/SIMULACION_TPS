# menu_inicial.py
import sys
import subprocess
from PyQt5 import QtWidgets, uic

class MenuInicial(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("menu_inicial.ui", self)

        # Botones
        self.btn_abrir_tp = self.findChild(QtWidgets.QPushButton, "btn_abrir_tp")
        self.exit_btn = self.findChild(QtWidgets.QPushButton, "exit_btn")

        # Verificar que los botones existan
        if self.btn_abrir_tp is None:
            raise AttributeError("No se encontró un botón con el nombre 'btn_abrir_tp' en el archivo menu_inicial.ui.")
        if self.exit_btn is None:
            raise AttributeError("No se encontró un botón con el nombre 'exit_btn' en el archivo menu_inicial.ui.")

        # Conectar eventos
        self.btn_abrir_tp.clicked.connect(self.abrir_tp)
        self.exit_btn.clicked.connect(self.salir)

    def abrir_tp(self):
        # Ejecuta app.py y cierra la ventana actual
        self.close()
        subprocess.Popen(["python", "app.py"]).wait()  # Espera a que app.py termine
        self.show()  # Reabre el menú inicial después de cerrar app.py

    def salir(self):
        # Cierra la ventana y termina la aplicación
        QtWidgets.QApplication.quit()

if __name__ == "__main__":
    while True:  # Bucle para reiniciar el menú inicial después de cerrar app.py
        app = QtWidgets.QApplication(sys.argv)
        ventana = MenuInicial()
        ventana.show()
        app.exec_()
        break  # Salir del bucle si se presiona el botón de salir