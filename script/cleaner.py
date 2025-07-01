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

# Concatenar todos los datos
df_general = pd.concat(dfs, ignore_index=True)

# Ordenar por la columna orden_mes
df_general = df_general.sort_values("orden_mes").reset_index(drop=True)

# --- Definir función para clasificar empleado ---
def clasificar_empleado(row):
    if row["CATEGORIA"] == 1 and row["CONCEPTO"] == 80:
        return "contratado"
    elif row["CATEGORIA"] <= 24 and row["CONCEPTO"] == 1:
        return "planta"
    elif row["CATEGORIA"] > 24 and row["CONCEPTO"] == 1:
        return "funcionario"
    else:
        return "Desconocido"

# Aplicar la función para crear la columna tipo_empleado
df_general["tipo_empleado"] = df_general.apply(clasificar_empleado, axis=1)

# Obtener un tipo por legajo (el primero que no sea "Desconocido")
tipo_por_legajo = (
    df_general[df_general["tipo_empleado"] != "Desconocido"]
    .groupby("LEGAJO")["tipo_empleado"]
    .first()
    .reset_index()
)


df_general = df_general.drop(columns="tipo_empleado")  # Quitamos para evitar conflictos
df_general = df_general.merge(tipo_por_legajo, on="LEGAJO", how="left")






columnas_deleted = ['DEPARTAMENTO', 'DEPARTAMENTO_DESC', 'ACTIVIDAD', 'SECRETARIA','SECCION', 'SECCION_DESC', 'TRAMO', 'TRAMO_DESC', 'CATEGORIA','TIPO_CONCEPTO']


df_general = df_general.drop(columns=columnas_deleted)

df_general = df_general[df_general['CONCEPTO'].isin([8,9,104,313,314,315,316,317,341,342,194,196,198])]

df_general["IMPORTE"] = (
    df_general["IMPORTE"]
    .astype(str)
    .str.replace(".", "", regex=False)  # elimina puntos de miles
    .str.replace(",", ".", regex=False)  # reemplaza coma por punto decimal
    .astype(float)
    .abs()
)

ruta = r"C:\Users\Usuario\Desktop\reporte\data\sexo"

# Leer el archivo sin header, separador tab (ajustar sep si es otro)
df_sexo = pd.read_csv(ruta, sep="\t", header=None, encoding="latin1")

# Seleccionar solo la columna 12 (índice 11)
df_sexo_legajos = df_sexo.iloc[:, 11].to_frame()

# Renombrar la columna para que quede con nombre 'LEGAJO'
df_sexo_legajos.columns = ["LEGAJO"]

# Convertir a int por las dudas
df_sexo_legajos["LEGAJO"] = df_sexo_legajos["LEGAJO"].astype(int)

df_general["LEGAJO"] = df_general["LEGAJO"].astype(int)

df_general["genero"] = df_general["LEGAJO"].apply(
    lambda x: "masculino" if x in df_sexo_legajos["LEGAJO"].values else "femenino"
)
