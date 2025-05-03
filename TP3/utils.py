import pandas as pd

def exportar_a_excel(tabla, ruta, parametros=None):
    # Datos principales de la simulación
    filas = []
    for fila in tabla:
        for ronda, (rnd1, p1, rnd2, p2, pts, acumulado, contador) in enumerate(fila['detalle'], start=1):
            filas.append({
                'Iteración': fila['iteracion'],
                'Ronda': ronda,
                'Random 1': rnd1,
                'Pinos 1': p1,
                'Random 2': rnd2 if rnd2 != '-' else '',
                'Pinos 2': p2 if p2 != '-' else '',
                'Puntos': pts,
                'Puntos Acumulados': acumulado,
                'Contador': contador
            })

    # Crear dataframe principal
    df = pd.DataFrame(filas)

    # Crear dataframe con resumen estadístico
    iteraciones_totales = len(tabla)
    if iteraciones_totales > 0:
        # Contar las iteraciones que superaron el objetivo
        objetivo_superado = sum(1 for fila in tabla if fila['supera_objetivo'])
        probabilidad = (objetivo_superado / iteraciones_totales) * 100

        resumen = pd.DataFrame([{
            'Total Iteraciones': iteraciones_totales,
            'Casos que Superan Objetivo': objetivo_superado,
            'Probabilidad (%)': round(probabilidad, 2)
        }])
    else:
        resumen = pd.DataFrame([{
            'Total Iteraciones': 0,
            'Casos que Superan Objetivo': 0,
            'Probabilidad (%)': 0
        }])

    # Guardar en un archivo Excel con los resultados estadísticos al final de la misma hoja
    with pd.ExcelWriter(ruta, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Simulación Bowling', index=False, startrow=0)

        # Agregar un espacio y luego el resumen en la misma hoja
        resumen.to_excel(writer, sheet_name='Simulación Bowling', index=False, startrow=len(df) + 3)

        # Si hay parámetros, agregarlos después del resumen
        if parametros:
            # Crear DataFrame para los parámetros básicos
            params_basicos = pd.DataFrame([{
                'Rondas': parametros['rondas'],
                'Iteraciones': parametros['iteraciones'],
                'Objetivo de Puntos': parametros['objetivo']
            }])

            # Agregar parámetros básicos
            params_basicos.to_excel(writer, sheet_name='Simulación Bowling', index=False, startrow=len(df) + 6)

            # Agregar información sobre las configuraciones de puntos
            puntos_df = pd.DataFrame([{
                'Puntos Strike': parametros['config']['puntos']['strike'],
                'Puntos Spare': parametros['config']['puntos']['spare']
            }])
            puntos_df.to_excel(writer, sheet_name='Simulación Bowling', index=False, startrow=len(df) + 9)

            # Agregar probabilidades del primer tiro
            probs_tiro1_data = [{'Pinos': p, 'Probabilidad (%)': prob} for p, prob in parametros['config']['probs_tiro1']]
            probs_tiro1_df = pd.DataFrame(probs_tiro1_data)
            probs_tiro1_df.to_excel(writer, sheet_name='Simulación Bowling', index=False, startrow=len(df) + 12, 
                                    header=['Pinos Primer Tiro', 'Probabilidad (%)'])

            # Agregar probabilidades del segundo tiro
            row_offset = len(df) + 15 + len(probs_tiro1_data)
            for pinos1, probs in parametros['config']['probs_tiro2'].items():
                probs_data = [{'Pinos': p, 'Probabilidad (%)': prob} for p, prob in probs]
                probs_df = pd.DataFrame(probs_data)
                probs_df.to_excel(writer, sheet_name='Simulación Bowling', index=False, startrow=row_offset,
                                  header=[f'Pinos 2do Tiro (si 1º={pinos1})', 'Probabilidad (%)'])
                row_offset += len(probs_data) + 2
