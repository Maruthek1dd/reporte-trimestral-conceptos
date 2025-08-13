import pandas as pd
import plotly.io as pio
from cleaner import df_general as df, tipo_por_titulo
from func import grafico_distribucion

df_junio = df[df['mes']=='junio']
pio.renderers.default = "browser"

def main():
    # Cambiá por una de tus columnas categóricas válidas
    columna = "genero"

    # Llamamos a la función que queremos testear
    fig = grafico_distribucion(
        df_junio,
        columna=columna,
        porcentaje=False,
        orientation="v"  # o "h"
    )

    # Mostramos el gráfico si fue generado correctamente
    if fig:
        fig.show()
    else:
        print("⚠️ No se generó ningún gráfico.")

if __name__ == "__main__":
    print(tipo_por_titulo)


