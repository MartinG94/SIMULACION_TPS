from generadorNumeros import random

class SimuladorBowling:
    def __init__(self, probs_tiro1, probs_tiro2, puntos, rondas):
        self.probs_tiro1 = probs_tiro1
        self.probs_tiro2 = probs_tiro2
        self.puntos = puntos
        self.rondas = rondas

    def obtener_pinos(self, distrib):
        rnd = random()
        acumulado = 0
        for valor, prob in distrib:
            acumulado += prob / 100
            if rnd <= acumulado:
                return valor, rnd
        return distrib[-1][0], rnd

    def simular(self, iteraciones, objetivo):
        tabla = []
        contador_supera = 0

        for i in range(1, iteraciones + 1):
            total_puntos = 0
            detalle = []

            for _ in range(self.rondas):
                pinos1, rnd1 = self.obtener_pinos(self.probs_tiro1)
                if pinos1 == 10:
                    total_puntos += self.puntos['strike']
                    rnd1 = round(rnd1,4)
                    detalle.append((rnd1, pinos1, '-', '-', self.puntos['strike'], total_puntos))
                else:
                    segunda_distrib = self.probs_tiro2.get(pinos1, [])
                    pinos2, rnd2 = self.obtener_pinos(segunda_distrib)
                    total = pinos1 + pinos2
                    if total == 10:
                        puntos = self.puntos['spare']
                    else:
                        puntos = total
                    total_puntos += puntos
                    rnd1 = round(rnd1,4)
                    rnd2 = round(rnd2,4)
                    detalle.append((rnd1, pinos1, rnd2, pinos2, puntos, total_puntos))

            # Verificar si supera el objetivo y actualizar contador
            if total_puntos > objetivo:
                contador_supera += 1

            tabla.append({
                'iteracion': i,
                'puntos_totales': total_puntos,
                'detalle': detalle,
                'supera_objetivo': contador_supera  # Contador acumulado
            })

        return tabla
        
    def obtener_probabilidad(self, tabla, iteraciones):
        """
        Calcula la probabilidad de superar el objetivo basado en los resultados
        de la simulación.
        """
        if not tabla or iteraciones <= 0:
            return 0
            
        # El último registro tiene el contador final de éxitos
        exitos = tabla[-1]['supera_objetivo']
        probabilidad = (exitos / iteraciones) * 100
        return probabilidad