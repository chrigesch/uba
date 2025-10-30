from datetime import datetime
from io import BytesIO
import numpy as np
import pandas as pd
from typing import Literal
import xlsxwriter  # noqa F401


def cruzar_listas_actas_autoevaluaciones(
    listado_actas: pd.DataFrame,
    listado_campus: pd.DataFrame,
    parcial: Literal[1, 2, "recuperatorio"],
    crear_excel: bool,
    mostrar_alumnos_no_encontrados: bool = False,
    mostrar_alumnos_corregidos: bool = False,
    mostrar_duplicados_campus: bool = False,
) -> dict:
    print(
        f"Revisar orden de columnas del 'listado_campus' y corregir, si necesario:\n{72 * '*'}\n{listado_campus.columns}"  # noqa E501
    )

    cols_autoevaluaciones = _obtener_columnas_por_parcial(parcial)

    listado_campus = _normalizar_listado_campus(
        listado_campus=listado_campus,
        cols_autoevaluaciones=cols_autoevaluaciones,
    )
    listado_campus_con_correcciones = _aplicar_correcciones(
        listado_actas=listado_actas,
        listado_campus=listado_campus,
        cols_autoevaluaciones=cols_autoevaluaciones,
        mostrar_alumnos_no_encontrados=mostrar_alumnos_no_encontrados,
        mostrar_alumnos_corregidos=mostrar_alumnos_corregidos,
        mostrar_duplicados_campus=mostrar_duplicados_campus,
    )
    listado_cruzado = _crear_listado_cruzado(
        listado_actas=listado_actas,
        listado_campus=listado_campus_con_correcciones["listado_campus"],
        cols_autoevaluaciones=cols_autoevaluaciones,
        incluir_correo_campus=False,
    )
    listado_cruzado = _determinar_alumnos_habilitados(
        df=listado_cruzado,
        columnas=cols_autoevaluaciones,
    )
    resumen = _generar_resumen_habilitados(listado_cruzado)

    # Crear un diccionario con los DataFrames para poder crear el excel
    dfs_finales = _crear_diccionario_con_comisiones_y_resumen(
        listado_cruzado=listado_cruzado,
        resumen=resumen,
    )
    if crear_excel:
        # Crear el excel ajustando el ancho de las columnas dinámicamente
        _crear_excel(dfs=dfs_finales, nombre_excel="listado_habilitados_")

    correcciones = {
        e: listado_campus_con_correcciones[e]
        for e in listado_campus_con_correcciones.keys()
        if e != "listado_campus"
    }

    output = {"listas": dfs_finales, "correcciones": correcciones}
    return output


def cruzar_listas_actas_notas(
    listado_actas: pd.DataFrame,
    listado_campus: pd.DataFrame,
    listado_certificados: pd.DataFrame | None,
    cond_promocion: Literal[
        "cond_prom_6_y_6", "cond_prom_6_y_7", "cond_prom_7_y_7", None
    ],
    condicion: Literal["preliminar", "final"],
    crear_excel: bool,
    mostrar_alumnos_no_encontrados: bool = False,
    mostrar_alumnos_corregidos: bool = False,
    mostrar_duplicados_campus: bool = False,
) -> dict:
    if condicion == "final":
        assert (
            cond_promocion is not None
        ), "Si es para condiciones finales, debe elegirse una condición de promoción."
        assert (
            listado_certificados is not None
        ), "Si es para condiciones finales, debe aportarse listado_certificados."
    print(
        f"Revisar orden de columnas del 'listado_campus' y corregir, si necesario:\n{72 * '*'}\n{listado_campus.columns}"  # noqa E501
    )
    COLS_POR_CONDICION = {
        "preliminar": ["parcial_1", "parcial_2"],
        "final": ["parcial_1", "parcial_2", "nota_recuperatorio"],
    }
    cols_autoevaluaciones = COLS_POR_CONDICION[condicion]

    listado_campus = _normalizar_listado_campus(
        listado_campus=listado_campus,
        cols_autoevaluaciones=cols_autoevaluaciones,
    )
    listado_campus_con_correcciones = _aplicar_correcciones(
        listado_actas=listado_actas,
        listado_campus=listado_campus,
        cols_autoevaluaciones=cols_autoevaluaciones,
        mostrar_alumnos_no_encontrados=mostrar_alumnos_no_encontrados,
        mostrar_alumnos_corregidos=mostrar_alumnos_corregidos,
        mostrar_duplicados_campus=mostrar_duplicados_campus,
    )
    listado_cruzado_notas = _crear_listado_cruzado(
        listado_actas=listado_actas,
        listado_campus=listado_campus_con_correcciones["listado_campus"],
        cols_autoevaluaciones=cols_autoevaluaciones,
        incluir_correo_campus=True,
    )
    # Agregamos los certificados
    listado_cruzado_notas = _procesar_certificados(
        listado_cruzado=listado_cruzado_notas,
        listado_actas=listado_actas,
        listado_certificados=listado_certificados,
    )
    # Agregamos columna para indicar si es diferido
    listado_cruzado_notas["diferido"] = np.where(
        listado_cruzado_notas["certificado_valido_p1"]
        | listado_cruzado_notas["certificado_valido_p2"],
        True,
        False,
    )
    # Establecer las condiciones (para promocionar)
    if cond_promocion is None:
        posibles_condiciones_para_promocionar = [
            "cond_prom_6_y_6",
            "cond_prom_6_y_7",
            "cond_prom_7_y_7",
        ]
    else:
        posibles_condiciones_para_promocionar = [cond_promocion]

    # Evaluar las condiciones
    listado_cruzado_notas = _determinar_condiciones_de_promocion(
        df=listado_cruzado_notas,
        condicion=condicion,
        posibles_condiciones=posibles_condiciones_para_promocionar,
    )
    # Agregamos columna para indicar cuál parcial debe recuperar
    listado_cruzado_notas = _determinar_cual_parcial_recupera(listado_cruzado_notas)

    # Crear "resumen"
    resumen_df = _generar_resumen_condiciones(
        df=listado_cruzado_notas,
        condiciones=posibles_condiciones_para_promocionar,
    )
    # Calcular los promedios para el listado de condiciones finales y renombrar columna de condición para promocionar
    if condicion == "final":
        listado_cruzado_notas = _aplicar_calculo_promedio_y_renombrar(
            df=listado_cruzado_notas,
            columna_condicion_original=cond_promocion,  # type: ignore
        )
    dfs_finales = {
        "resumen": resumen_df,
        "todos": listado_cruzado_notas,
    }
    # Crear Excel
    if crear_excel:
        _crear_excel(dfs=dfs_finales, nombre_excel="listado_notas_")

    correcciones = {
        e: listado_campus_con_correcciones[e]
        for e in listado_campus_con_correcciones.keys()
        if e != "listado_campus"
    }

    output = {"listas": dfs_finales, "correcciones": correcciones}
    return output


def _aplicar_correcciones(
    listado_actas: pd.DataFrame,
    listado_campus: pd.DataFrame,
    cols_autoevaluaciones: list[str],
    mostrar_alumnos_no_encontrados: bool,
    mostrar_alumnos_corregidos: bool,
    mostrar_duplicados_campus: bool,
) -> dict:
    correcciones_1 = _corregir_dni_en_listado_campus(
        listado_actas=listado_actas,
        listado_campus=listado_campus,
        mostrar_alumnos_no_encontrados=mostrar_alumnos_no_encontrados,
        mostrar_alumnos_corregidos=mostrar_alumnos_corregidos,
    )
    correcciones_2 = _corregir_alumnos_duplicados_en_campus(
        listado_campus=correcciones_1["listado_campus"],
        cols_autoevaluaciones=cols_autoevaluaciones,
        mostrar_duplicados_campus=mostrar_duplicados_campus,
    )
    dfs = {
        "listado_campus": correcciones_2["listado_campus"],
        "en_actas_pero_no_en_campus": correcciones_1["en_actas_pero_no_en_campus"],
        "corregidos": correcciones_1["corregidos"],
        "duplicados": correcciones_2["duplicados"],
        "no_encontrados": correcciones_1["no_encontrados"],
    }
    return dfs


def _aplicar_calculo_promedio_y_renombrar(
    df: pd.DataFrame,
    columna_condicion_original: str,
) -> pd.DataFrame:
    """
    Calcula el promedio por fila según reglas específicas,
    redondea y renombra la columna de condición a 'condicion'.
    """

    def _calcular_promedio(row):
        p1, p2, rec = row["parcial_1"], row["parcial_2"], row["nota_recuperatorio"]

        if pd.notna(p1) and pd.notna(p2) and 4 <= p1 <= 10 and 4 <= p2 <= 10:
            return (p1 + p2) / 2
        elif p1 > 3 and pd.notna(rec) and rec > 3:
            return (p1 + rec) / 2
        elif p2 > 3 and pd.notna(rec) and rec > 3:
            return (p2 + rec) / 2
        elif p1 < 4 and p2 < 4 and p1 <= p2:
            return p2
        elif p1 < 4 and p2 < 4 and p1 >= p2:
            return p1
        elif p1 < 4 and p2 > 3 and pd.isna(rec):
            return p1
        elif p1 > 3 and p2 < 4 and pd.isna(rec):
            return p2
        elif p1 < 4 and rec < 4 and p1 >= rec:
            return p1
        elif p1 < 4 and rec < 4 and p1 <= rec:
            return rec
        elif p2 < 4 and rec < 4 and p2 >= rec:
            return p2
        elif p2 < 4 and rec < 4 and p2 <= rec:
            return rec
        elif p1 > 3 and pd.isna(p2) and rec < 4:
            return rec
        elif pd.isna(p1) and p2 > 3 and rec < 4:
            return rec
        elif p1 < 4 and pd.isna(p2) and pd.isna(rec):
            return p1
        elif pd.isna(p1) and p2 < 4 and pd.isna(rec):
            return p2
        else:
            return np.nan

    df["promedio"] = df.apply(_calcular_promedio, axis=1)
    df["promedio"] = (df["promedio"] + 0.05).round()
    df = df.rename(columns={columna_condicion_original: "condicion"})
    return df


def _corregir_alumnos_duplicados_en_campus(
    listado_campus: pd.DataFrame,
    cols_autoevaluaciones: list[str],
    mostrar_duplicados_campus: bool = False,
) -> dict:
    # Calcular número de NaN por fila en las columnas de autoevaluación (sin asignarlo)
    n_nan = listado_campus[cols_autoevaluaciones].isna().sum(axis=1)

    # Seleccionar los índices de las filas “mejores” (menos NaN) para cada alumno
    mejores_idx = n_nan.groupby(listado_campus["Número de ID"]).idxmin()

    # Filtrar el DataFrame conservando solo las mejores filas
    df_corregido = listado_campus.loc[mejores_idx].reset_index(drop=True).copy()

    # Detectar duplicados originales (antes de corregir)
    dni_duplicados = (
        listado_campus["Número de ID"].value_counts().loc[lambda x: x > 1].index
    )

    df_duplicados = listado_campus[listado_campus["Número de ID"].isin(dni_duplicados)]

    # Mostrar duplicados si corresponde
    if mostrar_duplicados_campus and not df_duplicados.empty:
        print(f"Alumnos duplicados:\n{'*' * 19}\n{df_duplicados.to_string()}")

    return {
        "listado_campus": df_corregido,
        "duplicados": df_duplicados.reset_index(drop=True),
    }


def _corregir_dni_en_listado_campus(
    listado_actas: pd.DataFrame,
    listado_campus: pd.DataFrame,
    mostrar_alumnos_no_encontrados: bool = False,
    mostrar_alumnos_corregidos: bool = False,
) -> dict:
    # Copia principal
    df = listado_campus.copy()

    # --- 1️⃣ Detectar alumnos no encontrados ---
    dni_campus = df["Número de ID"]
    dni_actas = listado_actas["Dni"]

    mask_no_encontrados = ~dni_campus.isin(dni_actas)
    df_no_encontrados = df.loc[mask_no_encontrados]

    if mostrar_alumnos_no_encontrados and not df_no_encontrados.empty:
        print(f"Alumnos no encontrados:\n{'*' * 23}\n{df_no_encontrados.to_string()}")

    # --- 2️⃣ Corregir DNIs usando e-mail ---
    # Crear mapeo correo → DNI correcto (diccionario)
    correo_a_dni = pd.Series(listado_actas["Dni"].values, index=listado_actas["e-mail"])

    # Mapear directamente en la subserie correspondiente
    mask_no_encontrados_idx = df_no_encontrados.index
    correos = df.loc[mask_no_encontrados_idx, "Dirección de correo"]
    dni_corregidos_por_correo = correos.map(correo_a_dni)

    # Actualizar solo donde se encontró correspondencia
    mask_corregibles = dni_corregidos_por_correo.notna()
    df.loc[mask_no_encontrados_idx[mask_corregibles], "Número de ID"] = (
        dni_corregidos_por_correo[mask_corregibles].astype(int)
    )

    # Guardar los DNIs corregidos por correo
    dni_corregidos = dni_corregidos_por_correo.dropna().astype(int).tolist()

    # --- 3️⃣ Intentar corregir DNIs con un dígito de más ---
    # Transformar a str una sola vez
    dni_str = df["Número de ID"].astype(str)
    dni_fix = dni_str.where(
        ~(dni_str.str.len() == 9) | ~dni_str.str.isdigit(), dni_str.str[:-1]
    )
    # Identificar cambios y actualizar
    mask_dni_cambiados = dni_fix != dni_str
    if mask_dni_cambiados.any():
        df.loc[mask_dni_cambiados, "Número de ID"] = dni_fix[mask_dni_cambiados].astype(
            int
        )
        dni_corregidos.extend(df.loc[mask_dni_cambiados, "Número de ID"].tolist())

    # --- 4️⃣ Detectar alumnos que están en actas pero no en campus ---
    en_actas_no_en_campus = listado_actas.loc[
        ~listado_actas["Dni"].isin(df["Número de ID"])
    ]

    if en_actas_no_en_campus.empty:
        texto = "Todos los alumnos del acta se encontraron en el listado campus"
        print(f"\n{texto}\n{len(texto) * '*'}\n")
    else:
        texto = "Alumnos en actas, pero NO en el campus:"
        print(f"{texto}\n{len(texto) * '*'}\n{en_actas_no_en_campus.to_string()}")

    # --- 5️⃣ Alumnos efectivamente corregidos ---
    df_corregidos = df[df["Número de ID"].isin(dni_corregidos)]

    if mostrar_alumnos_corregidos and not df_corregidos.empty:
        texto = "Alumnos corregidos:"
        print(f"{texto}\n{len(texto) * '*'}\n{df_corregidos.to_string()}")

    return {
        "listado_campus": df.reset_index(drop=True),
        "corregidos": df_corregidos.reset_index(drop=True),
        "en_actas_pero_no_en_campus": en_actas_no_en_campus.reset_index(drop=True),
        "no_encontrados": df_no_encontrados.reset_index(drop=True),
    }


def _crear_diccionario_con_comisiones_y_resumen(
    listado_cruzado: pd.DataFrame,
    resumen: pd.DataFrame,
) -> dict:
    dfs = {
        "resumen": resumen,
        "todos": listado_cruzado,
    }
    # Crear un diccionario con un DataFrame que contiene todas las comisiones y un DataFrame por cada una de las comisiones # noqa E501
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
        if len(str(comision)) == 1:
            comision = f"0{comision}"
        dfs[f"Comision_{comision}"] = listado_temp
    return dfs


def _crear_excel(
    dfs: dict,
    nombre_excel: str,
):
    # Crear el excel ajustando el ancho de las columnas dinámicamente
    now = f"{datetime.now().strftime('%Y-%m-%d--%H-%M-%S.%f')[:-3]}"
    with pd.ExcelWriter(f"{nombre_excel}{now}.xlsx", engine="xlsxwriter") as writer:
        for sheetname, df in dfs.items():
            df.to_excel(writer, sheet_name=sheetname, index=False)
            for column in df.columns.to_list():
                column_length = (
                    int(max(df[column].astype(str).map(len).max(), len(column))) + 1
                )
                col_idx = df.columns.get_loc(column)
                writer.sheets[sheetname].set_column(col_idx, col_idx, column_length)


def _crear_excel_descargable(dfs: dict) -> BytesIO:
    """Crea un archivo Excel en memoria con múltiples hojas."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for sheetname, df in dfs.items():
            df.to_excel(writer, sheet_name=sheetname, index=False)
            worksheet = writer.sheets[sheetname]
            for column in df.columns:
                column_length = (
                    int(max(df[column].astype(str).map(len).max(), len(column))) + 1
                )
                col_idx = df.columns.get_loc(column)
                worksheet.set_column(col_idx, col_idx, column_length)
    output.seek(0)  # Volver al inicio del archivo en memoria
    return output


def _crear_listado_cruzado(
    listado_actas: pd.DataFrame,
    listado_campus: pd.DataFrame,
    cols_autoevaluaciones: list,
    incluir_correo_campus: bool = False,
) -> pd.DataFrame:
    # Crear el listado cruzado y seleccionar solamente las columnas de interés
    listado_cruzado = pd.merge(
        left=listado_actas,
        right=listado_campus.rename(columns={"Dirección de correo": "correo_campus"}),
        how="left",
        left_on="Dni",
        right_on="Número de ID",
    )
    cols_listado_cruzado = ["C", "AyN", "Dni"]
    if incluir_correo_campus:
        cols_listado_cruzado.append("correo_campus")

    cols_listado_cruzado.extend(cols_autoevaluaciones)

    return listado_cruzado[cols_listado_cruzado]


def _determinar_alumnos_habilitados(
    df: pd.DataFrame,
    columnas: list[str],
) -> pd.DataFrame:
    df["habilitada/o"] = df[columnas].notna().all(axis=1)
    df = df.sort_values(
        by=["C", "habilitada/o", "AyN"], ascending=[True, False, True]
    ).reset_index(drop=True)
    return df


def _determinar_condiciones_de_promocion(
    df: pd.DataFrame,
    condicion: Literal["preliminar", "final"],
    posibles_condiciones: list[str],
) -> pd.DataFrame:
    p1, p2 = df["parcial_1"], df["parcial_2"]
    cert1, cert2 = df["certificado_valido_p1"], df["certificado_valido_p2"]
    pos_dif = df["diferido"]
    rec = (
        df["nota_recuperatorio"]
        if condicion == "final"
        else pd.Series([np.nan] * len(df))
    )

    for cond_prom in posibles_condiciones:
        df[cond_prom] = "pendiente"

        if condicion == "preliminar":
            condicion_libre = (p1.isna()) & (p2.isna() & ~cert1 & ~cert2)
            condicion_libre_por_nota = (
                ((p1.isna()) & (p2 < 4) & ~cert1 & ~cert2)
                | ((p1 < 4) & (p2.isna()) & ~cert1 & ~cert2)
                | ((p1 < 4) & (p2 < 4) & ~cert1 & ~cert2)
            )
            condicion_regular = (p1 >= 4) & (p2 >= 4)
        else:  # condicion == "final"
            condicion_libre = (
                ((p1.isna()) & (p2.isna()))
                | ((p1 >= 4) & (p2.isna()) & (rec.isna()))
                | ((p1.isna()) & (p2 >= 4) & (rec.isna()))
            )
            condicion_libre_por_nota = (
                ((p1.isna()) & (p2 < 4))
                | ((p1 < 4) & (p2.isna()))
                | ((p1 < 4) & (p2 < 4))
                | ((p1 >= 4) & (p2 < 4) & (rec.isna()))
                | ((p1 < 4) & (p2 >= 4) & (rec.isna()))
                | (rec < 4)
            )
            condicion_regular = (
                ((p1 >= 4) & (p2 >= 4))
                | ((p1 >= 4) & ((p2 < 4) | p2.isna()) & (rec >= 4))
                | (((p1 < 4) | p1.isna()) & (p2 >= 4) & (rec >= 4))
            )
            condicion_pendiente = (
                (pos_dif & p1.isna() & p2.isna() & (rec >= 4))
                | (pos_dif & (((rec >= 4) & (p1 < 4)) | ((rec < 4) & (p1 >= 4))))
                | (pos_dif & (((rec >= 4) & (p2 < 4)) | ((rec < 4) & (p2 >= 4))))
            )

        # Condiciones de promoción
        if cond_prom == "cond_prom_6_y_6":
            condicion_promocion = (
                ((p1 >= 6) & (p2 >= 6))
                | (cert1 & (p2 >= 6) & (rec >= 6))
                | (cert2 & (p1 >= 6) & (rec >= 6))
            )
        elif cond_prom == "cond_prom_6_y_7":
            condicion_promocion = (
                ((p1 >= 7) & (p2 >= 6))
                | ((p1 >= 6) & (p2 >= 7))
                | (cert1 & (((p2 >= 7) & (rec >= 6)) | ((p2 >= 6) & (rec >= 7))))
                | (cert2 & (((p1 >= 7) & (rec >= 6)) | ((p1 >= 6) & (rec >= 7))))
            )
        elif cond_prom == "cond_prom_7_y_7":
            condicion_promocion = (
                ((p1 >= 7) & (p2 >= 7))
                | (cert1 & (p2 >= 7) & (rec >= 7))
                | (cert2 & (p1 >= 7) & (rec >= 7))
            )

        # Aplicar condiciones al DataFrame
        df.loc[condicion_libre, cond_prom] = "libre"
        df.loc[condicion_libre_por_nota, cond_prom] = "libre_por_nota"
        df.loc[condicion_regular, cond_prom] = "regular"
        if condicion == "final":
            df.loc[condicion_pendiente, cond_prom] = "pendiente"
        df.loc[condicion_promocion, cond_prom] = "promocion"

    return df


def _determinar_cual_parcial_recupera(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega la columna 'recuperatorio' al DataFrame.
    Indica qué parcial debe recuperar el estudiante:
    - 1 si debe recuperar el parcial 1,
    - 2 si debe recuperar el parcial 2,
    - np.nan si ya tiene definida su condición.
    """
    ultima_columna_condicion = df.columns[-1]
    ya_definido = df[ultima_columna_condicion] != "pendiente"
    recupera_p2 = (df[ultima_columna_condicion] == "pendiente") & (
        (df["parcial_2"] < 4) | (df["parcial_2"].isna())
    )
    df["recuperatorio"] = np.select(
        condlist=[ya_definido, recupera_p2],
        choicelist=[np.nan, 2],
        default=1,
    )
    return df


def _generar_resumen_condiciones(
    df: pd.DataFrame,
    condiciones: list[str],
) -> pd.DataFrame:
    VALORES_POSIBLES = ("promocion", "regular", "libre_por_nota", "libre", "pendiente")

    resumen_list = [
        df[cond].value_counts().reindex(VALORES_POSIBLES, fill_value=0).rename(cond)
        for cond in condiciones
    ]
    resumen_df = pd.concat(resumen_list, axis=1).reset_index(names="index")
    return resumen_df


def _generar_resumen_habilitados(df: pd.DataFrame) -> pd.DataFrame:
    resumen = df[["C", "habilitada/o"]].value_counts().unstack(fill_value=0)
    resumen.columns.name = None

    resumen["total"] = resumen.sum(axis=1)
    resumen.loc["total"] = resumen.sum(axis=0)

    columnas_renombradas = {}

    if True in resumen.columns:
        columnas_renombradas[True] = "habilitados"
    if False in resumen.columns:
        columnas_renombradas[False] = "inhabilitados"

    resumen = resumen.rename(columns=columnas_renombradas)

    columnas_finales = [
        col
        for col in ["habilitados", "inhabilitados", "total"]
        if col in resumen.columns
    ]
    resumen = resumen[columnas_finales]
    return resumen.reset_index()


def _normalizar_listado_campus(
    listado_campus: pd.DataFrame,
    cols_autoevaluaciones: list[str],
) -> pd.DataFrame:
    listado_campus = listado_campus.iloc[:, :-1]
    listado_campus.columns.values[-len(cols_autoevaluaciones) :] = (  # noqa F203
        cols_autoevaluaciones
    )
    listado_campus[cols_autoevaluaciones] = listado_campus[
        cols_autoevaluaciones
    ].replace({"-": np.nan, "Ausente": np.nan})
    return listado_campus


def _obtener_columnas_por_parcial(parcial: Literal[1, 2, "recuperatorio"]) -> list[str]:
    return {
        1: ["au_1", "au_2", "au_3_p1", "au_3_p2"],
        2: ["au_6_p1", "au_6_p2", "au_7_p1", "au_7_p2"],
        "recuperatorio": [
            "au_1",
            "au_2",
            "au_3_p1",
            "au_3_p2",
            "au_6_p1",
            "au_6_p2",
            "au_7_p1",
            "au_7_p2",
        ],
    }[parcial]


def _procesar_certificados(
    listado_cruzado: pd.DataFrame,
    listado_actas: pd.DataFrame,
    listado_certificados: pd.DataFrame | None,
) -> pd.DataFrame:
    COLS_NOMBRES = (
        "certificado_valido_p1",
        "tipo_de_certificado_p1",
        "certificado_valido_p2",
        "tipo_de_certificado_p2",
    )
    # Crear placeholders
    for col in COLS_NOMBRES:
        listado_cruzado[col] = np.nan if "tipo" in col else False

    if listado_certificados is None:
        return listado_cruzado

    print(
        f"Revisar orden de columnas del 'listado_certificados' y corregir, si necesario:\n{78 * '*'}\n{listado_certificados.columns}"  # noqa: E501
    )

    # Renombrar las últimas 4 columnas
    listado_certificados.columns.values[-4:] = COLS_NOMBRES

    # Convertir columnas de tipo str a minúscula
    for col in COLS_NOMBRES:
        listado_certificados[col] = listado_certificados[col].str.lower()

    # Merge temporal
    listado_cruzado_temp = pd.merge(
        left=listado_actas,
        right=listado_certificados,
        how="left",
        left_on="Dni",
        right_on="Dni",
    )

    # Actualizar los valores en el DataFrame final
    for col in ["certificado_valido_p1", "certificado_valido_p2"]:
        listado_cruzado[col] = np.where(
            listado_cruzado_temp[col].isin(["si", "sí"]), True, False
        )
    for col in ["tipo_de_certificado_p1", "tipo_de_certificado_p2"]:
        listado_cruzado[col] = listado_cruzado_temp[col]

    return listado_cruzado
