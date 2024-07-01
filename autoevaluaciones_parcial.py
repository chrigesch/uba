from datetime import date
import numpy as np
import pandas as pd
from typing import Literal
import xlsxwriter  # noqa F401


def cruzar_listas_actas_campus(
    listado_actas: pd.DataFrame,
    listado_campus: pd.DataFrame,
    parcial: Literal[1, 2, "notas", "recuperatorio"],
    crear_excel: bool,
    mostar_alumnos_no_encontrados: bool = False,
    mostar_alumnos_corregidos: bool = False,
    mostar_duplicados_campus: bool = False,
) -> dict:
    print(
        f"Revisar orden de columnas del 'listado_campus' y corregir, si necesario:\n{72 * '*'}\n{listado_campus.columns}"  # noqa E501
    )
    # Eliminar última columna del listado_campus y cambiar los nombres de las columnas
    listado_campus = listado_campus.iloc[:, :-1]
    if parcial == 1:
        cols_autoevaluaciones = ["au_1", "au_2", "au_3_p1", "au_3_p2"]
    elif parcial == 2:
        cols_autoevaluaciones = ["au_6_p1", "au_6_p2", "au_7_p1", "au_7_p2"]
    elif parcial == "notas":
        cols_autoevaluaciones = ["parcial_1", "parcial_2"]
    elif parcial == "recuperatorio":
        cols_autoevaluaciones = [
            "au_1",
            "au_2",
            "au_3_p1",
            "au_3_p2",
            "au_6_p1",
            "au_6_p2",
            "au_7_p1",
            "au_7_p2",
        ]
    listado_campus.columns.values[-len(cols_autoevaluaciones) :] = (  # noqa F203
        cols_autoevaluaciones
    )
    listado_campus[cols_autoevaluaciones] = listado_campus[
        cols_autoevaluaciones
    ].replace({"-": np.nan, "Ausente": np.nan})
    # Determinar cuáles DNIs están en el listado del campus, pero no en el listado de actas
    dni_no_encontrados = listado_campus.copy()[
        ~listado_campus["Número de ID"].isin(listado_actas["Dni"])
    ]
    if mostar_alumnos_no_encontrados:
        print(f"Alumnos no encontrados:\n{23 * '*'}\n{dni_no_encontrados.to_string()}")
    # Corregir los DNIs, utilizando la dirección de correo para encontrarlos en el listado de actas
    dni_corregido = []
    for dni in dni_no_encontrados["Número de ID"].unique():
        correo = dni_no_encontrados[dni_no_encontrados["Número de ID"] == dni][
            "Dirección de correo"
        ]
        dni_correcto = listado_actas[listado_actas["e-mail"].isin(correo)]["Dni"]
        if len(dni_correcto) > 0:
            dni_corregido.append(dni_correcto.iloc[0])
            idx_a_corregir = listado_campus.index[
                listado_campus["Número de ID"] == dni
            ].tolist()
            for idx_ in idx_a_corregir:
                listado_campus.at[idx_, "Número de ID"] = dni_correcto.iloc[0]
    if mostar_alumnos_corregidos:
        print(
            f"Alumnos corregidos:\n{19 * '*'}\n{listado_campus[listado_campus['Número de ID'].isin(dni_corregido)].to_string()}"  # noqa E501
        )
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
        print(
            f"Alumnos duplicados:\n{19 * '*'}\n{listado_campus[listado_campus['Número de ID'].isin(dni_alumnos_duplicados)].to_string()}"  # noqa E501
        )
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

    # Crear "resumen"
    if parcial == "notas":
        resumen = {"posible_recuperatorio": [True, False]}
        for col in cols_autoevaluaciones:
            posible_recuperatorio_falso = len(
                listado_cruzado[listado_cruzado[col] >= 4]
            )
            resumen[col] = [  # type: ignore
                len(listado_cruzado) - posible_recuperatorio_falso,
                posible_recuperatorio_falso,
            ]
        resumen = pd.DataFrame(resumen)
    else:
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
                resumen = resumen[[False, "total"]].rename(
                    columns={False: "inhabilitados"}
                )
            except Exception:
                resumen = resumen[[True, "total"]].rename(columns={True: "habilitados"})
        resumen = resumen.reset_index()
    # Crear un diccionario con los DataFrames para poder crear el excel
    if crear_excel:
        dfs = {
            "resumen": resumen,
            "todas": listado_cruzado,
        }
        if parcial in [1, 2, "recuperatorio"]:
            # Crear un diccionario con un DataFrame que contiene todas las comisiones y un DataFrame por cada una de las comisiones # noqa E501
            nombre_excel = "listado_habilitados_"
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
        else:
            nombre_excel = "listado_notas_"
        # Crear el excel ajustando el ancho de las columnas dinámicamente
        with pd.ExcelWriter(
            f"{nombre_excel}{date.today()}.xlsx", engine="xlsxwriter"
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
