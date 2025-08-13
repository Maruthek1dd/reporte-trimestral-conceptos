import pandas as pd
import os

# Mapeo de nombres de mes a número
meses_orden = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12
}

carpeta = "data"
dfs = []

for archivo in os.listdir(carpeta):
    if archivo.endswith(".txt") and archivo.startswith("libro_"):
        mes = archivo.replace("libro_", "").replace(".txt", "").lower()
        df = pd.read_csv(os.path.join(carpeta, archivo), encoding='latin1', delimiter="|")
        df["mes"] = mes
        df["orden_mes"] = meses_orden[mes]
        dfs.append(df)

df_general = pd.concat(dfs, ignore_index=True)
df_general = df_general.sort_values("orden_mes").reset_index(drop=True)

# Primero filtramos los conceptos relevantes para no trabajar con datos innecesarios
conceptos_validos = [1,80,8,9,17,104,313,314,315,316,317,341,342,194,196,198,301,19,29,47,31,88,153,15, 36,259,253]
df_general = df_general[df_general['CONCEPTO'].isin(conceptos_validos)].copy()

# Función para clasificar tipo_empleado
def clasificar_empleado(row):
    if row["CATEGORIA"] == 1 and row["CONCEPTO"] == 80:
        return "contratado"
    elif row["CATEGORIA"] <= 24 and row["CONCEPTO"] == 1:
        return "planta"
    elif row["CATEGORIA"] > 24 and row["CONCEPTO"] == 1:
        return "funcionario"
    else:
        return "Desconocido"

df_general["tipo_empleado"] = df_general.apply(clasificar_empleado, axis=1)

# Limpiar y convertir CANTIDAD a numérico entero
df_general["CANTIDAD"] = df_general["CANTIDAD"].astype(str).str.strip()
df_general["CANTIDAD"] = pd.to_numeric(df_general["CANTIDAD"], errors="coerce")

mapa_titulos = {
    8: "SECUNDARIO",
    10: "TECNICATURA",
    15: "PROFESORADO/DOCENTE",
    25: "UNIVERSITARIO"
}

def clasificar_empleado_titulo(row):
    if row["CONCEPTO"] == 17:
        cantidad = row["CANTIDAD"]
        if pd.isna(cantidad):
            return "SIN TITULO"
        try:
            cantidad_int = int(cantidad)
        except:
            return "SIN TITULO"
        return mapa_titulos.get(cantidad_int, "SIN TITULO")
    return "SIN TITULO"

df_general["titulo"] = df_general.apply(clasificar_empleado_titulo, axis=1)

# Elegir primer tipo_empleado válido para cada LEGAJO
def primer_tipo_empleado_valido(grupo):
    tipos_validos = grupo[grupo != "Desconocido"]
    if not tipos_validos.empty:
        return tipos_validos.iloc[0]
    else:
        return "Desconocido"

tipo_por_legajo = (
    df_general.groupby("LEGAJO")["tipo_empleado"]
    .apply(primer_tipo_empleado_valido)
    .reset_index()
)

# Elegir primer titulo válido para cada LEGAJO
def primer_titulo_valido(grupo):
    titulos_validos = grupo[grupo != "SIN TITULO"]
    if not titulos_validos.empty:
        return titulos_validos.iloc[0]
    else:
        return "SIN TITULO"

tipo_por_titulo = (
    df_general.groupby("LEGAJO")["titulo"]
    .apply(primer_titulo_valido)
    .reset_index()
)

# Merge para asignar los valores finales
df_general = df_general.drop(columns=["tipo_empleado", "titulo"])
df_general = df_general.merge(tipo_por_legajo, on="LEGAJO", how="left")
df_general = df_general.merge(tipo_por_titulo, on="LEGAJO", how="left")

# Columnas que quieres eliminar
columnas_deleted = [
    'DEPARTAMENTO', 'DEPARTAMENTO_DESC', 'ACTIVIDAD', 'SECRETARIA',
    'SECCION', 'SECCION_DESC', 'TRAMO', 'TRAMO_DESC', 'CATEGORIA', 'TIPO_CONCEPTO'
]
df_general = df_general.drop(columns=columnas_deleted, errors='ignore')

# Limpiar y convertir IMPORTE
df_general["IMPORTE"] = (
    df_general["IMPORTE"]
    .astype(str)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
    .astype(float)
    .abs()
)

# Cargar archivo sexo para asignar genero
ruta = "data/sexo"
df_sexo = pd.read_csv(ruta, sep="\t", header=None, encoding="latin1")
df_sexo_legajos = df_sexo.iloc[:, 11].to_frame()
df_sexo_legajos.columns = ["LEGAJO"]
df_sexo_legajos["LEGAJO"] = df_sexo_legajos["LEGAJO"].astype(int)

df_general["LEGAJO"] = df_general["LEGAJO"].astype(int)
df_general["genero"] = df_general["LEGAJO"].apply(
    lambda x: "masculino" if x in df_sexo_legajos["LEGAJO"].values else "femenino"
)


