from datetime import date
import numpy as np
import pandas as pd
from typing import Literal
import xlsxwriter  # noqa F401


def cruzar_listas_actas_campus(
    listado_actas: pd.DataFrame,
    listado_campus: pd.DataFrame,
    parcial: Literal[1, 2],
    crear_excel: bool,
    mostar_duplicados_campus: bool = False,
) -> dict:
    # Eliminar última columna del listado_campus y cambiar los nombres de las columnas
    listado_campus = listado_campus.iloc[:, :-1]
    if parcial == 1:
        cols_autoevaluaciones = ["au_1", "au_2", "au_3_p1", "au_3_p2"]
    elif parcial == 2:
        cols_autoevaluaciones = ["au_6_p1", "au_6_p2", "au_7_p1", "au_7_p2"]

    listado_campus.columns.values[-4:] = cols_autoevaluaciones
    listado_campus[cols_autoevaluaciones] = listado_campus[
        cols_autoevaluaciones
    ].replace({"-": np.nan})
    # Determinar alumnos duplicados en el listado del campus
    dni_alumnos_duplicados = listado_campus["Número de ID"].value_counts()
    dni_alumnos_duplicados = dni_alumnos_duplicados[
        dni_alumnos_duplicados > 1
    ].index.to_list()
    # Por cada alumno duplicado, determinar cuál entrada tiene menos valores faltantes en las columnas de las autoevaluaciones y eliminar las demás # noqa E501
    if len(dni_alumnos_duplicados) > 0:
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
            if mostar_duplicados_campus:
                print(lista_temp)
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
    listado_cruzado["habilitada/o"] = (
        listado_cruzado[cols_autoevaluaciones].notna().all(axis=1)
    )
    listado_cruzado = listado_cruzado.sort_values(
        by=["C", "habilitada/o", "AyN"], ascending=[True, False, True]
    ).reset_index(drop=True)
    # Crear el resumen de todas las comisiones
    resumen = (
        listado_cruzado[["C", "habilitada/o"]].value_counts().unstack(fill_value=0)
    )
    resumen["total"] = resumen.sum(axis=1)
    resumen.loc["total"] = resumen.sum(axis=0)
    try:
        resumen = resumen[[True, False, "total"]].rename(
            columns={True: "habilitados", False: "inhabilitados"}
        )
    except Exception:
        try:
            resumen = resumen[[False, "total"]].rename(columns={False: "inhabilitados"})
        except Exception:
            resumen = resumen[[True, "total"]].rename(columns={True: "habilitados"})
    resumen = resumen.reset_index()
    # Crear un excel con una hoja por cada comisión
    if crear_excel:
        # Crear un diccionario con un DataFrame que contiene todas las comisiones y un DataFrame por cada una de las comisiones # noqa E501
        dfs = {
            "resumen": resumen,
            "todas": listado_cruzado,
        }
        for comision in listado_cruzado["C"].unique():
            listado_temp = listado_cruzado[listado_cruzado["C"] == comision]
            if len(listado_temp["habilitada/o"].unique()) > 1:
                # Inlcuir filas vacías entre habilitados e inhabilitados
                n_filas_vacias = 3
                listado_temp = pd.concat(
                    [
                        listado_temp.loc[listado_temp["habilitada/o"]],
                        pd.DataFrame(
                            np.nan,
                            index=pd.RangeIndex(n_filas_vacias),
                            columns=listado_temp.columns,
                        ),
                        listado_temp.loc[~listado_temp["habilitada/o"]],
                    ],
                    ignore_index=True,
                    axis=0,
                )
                listado_temp["habilitada/o"] = listado_temp["habilitada/o"].replace(
                    {1: True, 0: False}
                )
            dfs[f"Comision_{comision}"] = listado_temp
        # Crear el excel ajustando el ancho de las columnas dinámicamente
        with pd.ExcelWriter(
            f"listado_habilitados_{date.today()}.xlsx", engine="xlsxwriter"
        ) as writer:
            for sheetname, df in dfs.items():
                df.to_excel(writer, sheet_name=sheetname, index=False)
                for column in df.columns.to_list():
                    column_length = (
                        int(max(df[column].astype(str).map(len).max(), len(column))) + 1
                    )
                    col_idx = df.columns.get_loc(column)
                    writer.sheets[sheetname].set_column(col_idx, col_idx, column_length)
    return {"resumen": resumen, "listado_cruzado": listado_cruzado}
