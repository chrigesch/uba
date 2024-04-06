import numpy as np
import pandas as pd

listado_actas = pd.read_excel("./downloads/listado_actas_2024-04-04.xlsx")
listado_campus = pd.read_excel("./downloads/listado_campus_2024-04-04.xlsx")
parcial = 1

# Eliminar última columna del listado_campus y cambiar los nombres de las columnas
listado_campus = listado_campus.iloc[:, :-1]
if parcial == 1:
    cols_autoevaluaciones = ["au_1", "au_2", "au_3_p1", "au_3_p2"]
elif parcial == 2:
    cols_autoevaluaciones = ["au_6_p1", "au_6_p2", "au_7_p1", "au_7_p2"]

listado_campus.columns.values[-4:] = cols_autoevaluaciones
listado_campus[cols_autoevaluaciones] = listado_campus[cols_autoevaluaciones].replace(
    {"-": np.nan}
)
# Determinar alumnos duplicados en el listado del campus
dni_alumnos_duplicados = listado_campus["Número de ID"].value_counts()
dni_alumnos_duplicados = dni_alumnos_duplicados[
    dni_alumnos_duplicados > 1
].index.to_list()
# Por cada alumno duplicado, determinar cuál entrada tiene menos valores faltantes en las columnas de las autoevaluaciones y eliminar las demás # noqa E501
for dni in dni_alumnos_duplicados:
    lista_temp = listado_campus.copy()
    lista_temp = lista_temp[lista_temp["Número de ID"] == dni]
    lista_temp["n_nan"] = lista_temp[cols_autoevaluaciones].isna().sum(axis=1)
    filas_a_eliminar = [
        fila
        for fila in lista_temp.index.to_list()
        if fila != lista_temp["n_nan"].idxmin()
    ]
    listado_campus = listado_campus.drop(filas_a_eliminar, axis=0)
# Crear el listado cruzado y seleccionar solamente las columnas de interés
listado_cruzado = pd.merge(
    left=listado_actas,
    right=listado_campus,
    how="left",
    left_on="Dni",
    right_on="Número de ID",
)
cols_listado_cruzado = ["C", "AyN", "Dni"]
for col in cols_autoevaluaciones:
    cols_listado_cruzado.append(col)
listado_cruzado = listado_cruzado[cols_listado_cruzado]
# Determinar alumnos inhabilitados
listado_cruzado["inhabilitado"] = (
    listado_cruzado[cols_autoevaluaciones].isnull().values.any(axis=1)
)
