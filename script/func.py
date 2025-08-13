import plotly.express as px
import pandas as pd
def grafico_por_concepto(df, concepto, agrupado_por, color_por=None):
    df_filtrado = df[df["CONCEPTO_DESC"] == concepto].copy()

    # Ordenar el mes si está presente
    if "mes" in agrupado_por and "mes" in df_filtrado.columns:
        df_filtrado["mes"] = pd.Categorical(
            df_filtrado["mes"],
            categories=["enero", "febrero", "marzo", "abril", "mayo", "junio"],
            ordered=True
        )

    if df_filtrado.empty:
        return None

    total = (
        df_filtrado
        .groupby(agrupado_por + ([color_por] if color_por and color_por not in agrupado_por else []))["IMPORTE"]
        .sum()
        .reset_index()
    )

    if len(agrupado_por) > 1:
        total["agrupado"] = total[agrupado_por].astype(str).agg(" | ".join, axis=1)
        x_col = "agrupado"
    else:
        x_col = agrupado_por[0]

    fig = px.bar(
        total,
        x=x_col,
        y="IMPORTE",
        color=color_por if color_por in total.columns else None,
        title=f"Total del concepto '{concepto}' por {' y '.join(agrupado_por).title()}",
        text_auto=True,
        height=900
    )

    fig.update_layout(
        xaxis_title=" | ".join(agrupado_por),
        yaxis_title="Total Importe",
        yaxis=dict(
            tickformat=",d",
            tickprefix="$",
            automargin=True
        ),
        xaxis_tickangle=90,
        title_font_size=18,
        margin=dict(t=60, b=100)
    )

    return fig


# ─────────────────────────────────────────────────────────────
# BLOQUE: Filtros y selección de estructura
# ─────────────────────────────────────────────────────────────


import plotly.express as px

def grafico_distribucion(df, columna,mes,porcentaje=False, color=None, orientation="v"):
    """
    Genera un gráfico de barras con la distribución de valores en una columna.
    
    - columna: string, nombre de la columna a analizar
    - porcentaje: bool, si True, se muestran porcentajes en lugar de cantidades
    - color: otra columna para colorear barras (por ejemplo, "genero")
    - orientation: "v" para barras verticales, "h" para horizontales
    """
    if df.empty or columna not in df.columns or "LEGAJO" not in df.columns:
        return None

    df_mes = df[df['mes']== mes]
    df_unicos = df_mes.drop_duplicates(subset="LEGAJO")
    
    conteo = df_unicos[columna].value_counts(dropna=False).reset_index()
    conteo.columns = [columna, "Cantidad"]

    if porcentaje:
        total = conteo["Cantidad"].sum()
        conteo["Porcentaje"] = (conteo["Cantidad"] / total * 100).round(2)
        y_value = "Porcentaje"
        y_format = ".2f%"
        title = f"Distribución porcentual de '{columna}'"
    else:
        y_value = "Cantidad"
        y_format = ",d"
        title = f"Distribución de '{columna}'"

    fig = px.bar(
        conteo,
        x=columna if orientation == "v" else y_value,
        y=y_value if orientation == "v" else columna,
        text=y_value,
        orientation=orientation,
        title=title,
        color=color if color in df.columns else None,
        height=600
    )

    fig.update_layout(
        xaxis_title=columna if orientation == "v" else y_value,
        yaxis_title=y_value if orientation == "v" else columna,
        yaxis_tickformat=y_format if orientation == "v" else None,
        xaxis_tickformat=y_format if orientation == "h" else None,
        xaxis_tickangle=0,
        margin=dict(t=60, b=100)
    )

    return fig
