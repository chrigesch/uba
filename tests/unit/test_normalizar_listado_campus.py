# tests/test_normalizar_listado_campus.py
import pandas as pd


from autoevaluaciones_parcial import _normalizar_listado_campus


def test_normaliza_listado_elimina_columna_final_y_renombra(
    df_listado_campus_completo,
    columnas_autoevaluacion,
):
    df_normalizado = _normalizar_listado_campus(
        listado_campus=df_listado_campus_completo,
        cols_autoevaluaciones=columnas_autoevaluacion,
    )

    columnas_esperadas = [
        "Número de ID",
        "Dirección de correo",
        "Nombre",
        "Autoeval 1",
        "Autoeval 2",
    ]
    assert list(df_normalizado.columns) == columnas_esperadas


def test_normaliza_reemplaza_valores_invalidos(
    df_listado_campus_completo,
    columnas_autoevaluacion,
):
    df_normalizado = _normalizar_listado_campus(
        listado_campus=df_listado_campus_completo,
        cols_autoevaluaciones=columnas_autoevaluacion,
    )

    # Checkea que valores "-" y "Ausente" hayan sido reemplazados por np.nan
    assert pd.isna(df_normalizado.loc[3, "Autoeval 2"])  # era "-"
    assert pd.isna(df_normalizado.loc[4, "Autoeval 1"])  # era "Ausente"
