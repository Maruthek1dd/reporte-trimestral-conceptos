import streamlit as st
import pandas as pd
from script.cleaner import df_general as df
from script.func import grafico_por_concepto, grafico_distribucion
import datetime




st.markdown("""
    <style>
        /* Fondo general */
        .main {
            background-color: #f8f9fa;
        }
        div[data-baseweb="menu"] {
            background-color: #e0f7fa !important;  /* color celeste claro, por ejemplo */
            color: #003366 !important;              /* texto azul oscuro */
        }
        div[data-baseweb="option"] {
            background-color: #e0f7fa !important;
            color: #003366 !important;
        }
        div[data-baseweb="option"][aria-selected="true"] {
            background-color: #90caf9 !important; /* azul más fuerte */
            color: #000000 !important;
        }
        /* Cambiar color de los selectboxes */
        div[data-baseweb="select"] > div {
            border-color: #A3C6FF !important;
        }
            
        span[data-baseweb="tag"] {
            background-color:  #003366 !important;  /* fondo azul oscuro */
            color: #003366 !important;               /* texto blanco */
            border-radius: 4px !important;         /* bordes redondeados */
            padding: 3px 8px !important;           /* un poco de padding para mejor estética */
            font-weight: 600 !important;
        }

        div[data-baseweb="select"] > div:focus-within {
            border-color: #ffffff !important;
            box-shadow: 0 0 0 2px rgba(0, 51, 102, 0.3) !important;
        }

        /* Texto activo en los selectboxes */
        div[data-baseweb="select"] span {
            color: #ffffff !important;
        }

        /* Scrollbar si hay muchas opciones */
        div[data-baseweb="menu"] {
            max-height: 250px;
            overflow-y: auto;
        }

        .block-container {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');

        h1.custom-title {
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            color: #003366 !important;  /* azul oscuro, forzando el color */
            text-align: center;
            margin-bottom: 1rem;
        }
    </style>
    <h1 class="custom-title">Análisis Detallado de Conceptos</h1>
""", unsafe_allow_html=True)

st.sidebar.image("https://www.villamaria.gob.ar/static/images/logo.92f64765ca39.svg", width=200)

# Fecha y hora actual
now = datetime.datetime.now()
st.sidebar.markdown(f"**Fecha:** {now.strftime('%d/%m/%Y')}")
st.sidebar.markdown(f"**Hora:** {now.strftime('%H:%M:%S')}")

# Elementos interactivos extra

modo_visualizacion = st.sidebar.selectbox("Modo de Visualización", ["Concepto", "Distribución por Categoría"])
if st.sidebar.button("🔄 Reiniciar filtros"):
    st.rerun()

# ----------------------------------------------------------
# BLOQUE: CONCEPTO
# ----------------------------------------------------------
if modo_visualizacion == "Concepto":
    df = df[~df['CONCEPTO'].isin([1, 80])]
    st.header("🔍 Análisis por Concepto")

    conceptos_disponibles = df["CONCEPTO_DESC"].unique()
    concepto_seleccionado = st.selectbox("Seleccionar concepto", conceptos_disponibles)

    # Filtros específicos del modo Concepto
    secretarias_disponibles = df["SECRETARIA_DESC"].dropna().unique()
    secretaria_filtrada = st.multiselect("Filtrar por Secretaría", secretarias_disponibles, default=secretarias_disponibles)

    tipos_disponibles = df["tipo_empleado"].dropna().unique()
    tipo_empleado_filtrado = st.multiselect("Filtrar por Tipo de Empleado", tipos_disponibles, default=tipos_disponibles)

    meses_disponibles = df["mes"].dropna().unique()
    mes_filtrado = st.multiselect("Filtrar por Mes", meses_disponibles, default=meses_disponibles)

    sexos_disponibles = df["genero"].dropna().unique()
    sexo_filtrado = st.multiselect("Filtrar por Sexo", sexos_disponibles, default=sexos_disponibles)

    df_filtrado = df[
        (df["CONCEPTO_DESC"] == concepto_seleccionado) &
        (df["SECRETARIA_DESC"].isin(secretaria_filtrada)) &
        (df["tipo_empleado"].isin(tipo_empleado_filtrado)) &
        (df["mes"].isin(mes_filtrado)) &
        (df["genero"].isin(sexo_filtrado))
    ]

    st.write(f"**{concepto_seleccionado}**")
    st.dataframe(df_filtrado)
    csv = df_filtrado.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Descargar CSV",
        data=csv,
        file_name='datos_filtrados.csv',
        mime='text/csv',
)

    st.subheader("Agrupar por")
    opciones_agrupacion = {
        "Secretaría": "SECRETARIA_DESC",
        "Tipo de Empleado": "tipo_empleado",
        "Mes": "mes",
        "genero": "genero"
    }
    agrupado_por_opciones = st.multiselect("Agrupar por", list(opciones_agrupacion.keys()), default=["Secretaría"])
    columnas_agrupadas = [opciones_agrupacion[key] for key in agrupado_por_opciones]

    fig = grafico_por_concepto(df, concepto_seleccionado, columnas_agrupadas)

    if fig:
        st.plotly_chart(fig)
    else:
        st.warning("No hay datos para este concepto.")


# ----------------------------------------------------------
# BLOQUE: DISTRIBUCIÓN POR CATEGORÍA
# ----------------------------------------------------------
elif modo_visualizacion == "Distribución por Categoría":
    st.header("📊 Distribución por Categoría")


    opciones_categorias = {
        "Género": "genero",
        "Título": "titulo",
        "Tipo de Empleado": "tipo_empleado",
        "Secretaría": "SECRETARIA_DESC"
    }

    # Selectbox con keys amigables
    col_distrib_key = st.selectbox(
        "Seleccionar columna para distribución",
        list(opciones_categorias.keys())
    )
    col_distrib = opciones_categorias[col_distrib_key]

    mes_distribucion = st.selectbox("Seleccionar mes", df["mes"].dropna().unique())

    mostrar_porcentaje = st.checkbox("Mostrar como porcentaje", value=False)
    orientacion_horizontal = st.checkbox("Gráfico horizontal", value=False)

    if col_distrib and mes_distribucion:
        df_distrib = df[df["CONCEPTO"].isin([1, 80])]
        fig_distrib = grafico_distribucion(
            df_distrib,
            columna=col_distrib,
            mes=mes_distribucion,
            porcentaje=mostrar_porcentaje,
            orientation="h" if orientacion_horizontal else "v"
        )

        if fig_distrib:
            st.plotly_chart(fig_distrib)
        else:
            st.warning("No hay datos para esta columna.")




st.markdown("<hr>", unsafe_allow_html=True)
st.caption("Desarrollado por Leonardo Marusich - Municipalidad de Villa María, 2025")