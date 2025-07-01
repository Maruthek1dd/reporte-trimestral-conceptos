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
