import tkinter as tk
from tkinter import ttk, messagebox

class ConfiguracionVentana(tk.Toplevel):
    def __init__(self, master, config_actual, callback_guardar):
        super().__init__(master)
        self.title("Configuración de Parámetros")
        self.config = config_actual
        self.callback_guardar = callback_guardar
        self.entries = {}

        self._crear_interfaz()

    def _crear_interfaz(self):
        # STRIKE y SPARE
        frame_puntos = ttk.LabelFrame(self, text="Puntos por Strike y Spare")
        frame_puntos.pack(fill="x", padx=10, pady=5)
        self.entries["strike"] = self._crear_entry_labeled(frame_puntos, "Strike (1 solo tiro)", self.config["puntos"]["strike"])
        self.entries["spare"] = self._crear_entry_labeled(frame_puntos, "Spare (2 tiros)", self.config["puntos"]["spare"])

        # Primera bola
        frame_tiro1 = ttk.LabelFrame(self, text="Probabilidades de la Primera Bola (suman 100)")
        frame_tiro1.pack(fill="x", padx=10, pady=5)
        self.entries["probs_tiro1"] = []
        for pino, prob in self.config["probs_tiro1"]:
            entry = self._crear_entry_labeled(frame_tiro1, f"Pinos: {pino}", prob)
            self.entries["probs_tiro1"].append((pino, entry))

        # Segunda bola
        frame_tiro2 = ttk.LabelFrame(self, text="Probabilidades de la Segunda Bola por valor del primer tiro (suman 100)")
        frame_tiro2.pack(fill="both", expand=True, padx=10, pady=5)
        self.entries["probs_tiro2"] = {}
        for pinos1, lista in self.config["probs_tiro2"].items():
            subframe = ttk.LabelFrame(frame_tiro2, text=f"Si 1º tiro fue {pinos1}")
            subframe.pack(fill="x", padx=5, pady=2)
            self.entries["probs_tiro2"][pinos1] = []
            for pinos2, prob in lista:
                entry = self._crear_entry_labeled(subframe, f"Pinos: {pinos2}", prob)
                self.entries["probs_tiro2"][pinos1].append((pinos2, entry))

        # Botón Guardar
        ttk.Button(self, text="Guardar", command=self.guardar).pack(pady=10)

    def _crear_entry_labeled(self, parent, label_text, valor_default):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=2)
        ttk.Label(frame, text=label_text, width=25).pack(side="left")
        entry = ttk.Entry(frame, width=10)
        entry.insert(0, str(valor_default))
        entry.pack(side="left")
        return entry

    def guardar(self):
        try:
            puntos = {
                "strike": int(self.entries["strike"].get()),
                "spare": int(self.entries["spare"].get())
            }

            probs_tiro1 = []
            for pino, entry in self.entries["probs_tiro1"]:
                prob = float(entry.get())
                probs_tiro1.append((pino, prob))

            probs_tiro2 = {}
            for pinos1, pares in self.entries["probs_tiro2"].items():
                lista = []
                for pinos2, entry in pares:
                    prob = float(entry.get())
                    lista.append((pinos2, prob))
                probs_tiro2[pinos1] = lista

            # Validar suma de probabilidades
            if abs(sum(prob for _, prob in probs_tiro1) - 100) > 0.01:
                raise ValueError("Las probabilidades de la primera bola deben sumar 100.")

            for key, lista in probs_tiro2.items():
                total = sum(prob for _, prob in lista)
                if abs(total - 100) > 0.01:
                    raise ValueError(f"Las probabilidades de la segunda bola para {key} deben sumar 100.")

            nueva_config = {
                "puntos": puntos,
                "probs_tiro1": probs_tiro1,
                "probs_tiro2": probs_tiro2
            }

            self.callback_guardar(nueva_config)
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))