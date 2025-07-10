# tests/test_corregir_duplicados.py
import pandas as pd
from pandas.testing import assert_frame_equal
from autoevaluaciones_parcial import _corregir_alumnos_duplicados_en_campus


def test_elimina_duplicado_con_mas_nans(
    df_listado_campus_completo,
    columnas_autoevaluacion,
):
    resultado = _corregir_alumnos_duplicados_en_campus(
        listado_campus=df_listado_campus_completo,
        cols_autoevaluaciones=columnas_autoevaluacion,
        mostrar_duplicados_campus=False,
    )

    listado = resultado["listado_campus"].reset_index(drop=True)

    # Debe quedarse con el registro de Ana con menos NaNs (no el duplicado sin notas)
    assert listado["Número de ID"].value_counts().loc[87654321] == 1
    assert listado.shape[0] == 4  # Se elimina 1 duplicado


def test_sin_duplicados_no_elimina():
    df = pd.DataFrame(
        {
            "Número de ID": [123, 456],
            "Nombre": ["Ana", "Juan"],
            "Autoeval 1": [5.0, 4.0],
            "Autoeval 2": [4.0, 3.0],
        }
    )

    resultado = _corregir_alumnos_duplicados_en_campus(
        listado_campus=df,
        cols_autoevaluaciones=["Autoeval 1", "Autoeval 2"],
        mostrar_duplicados_campus=False,
    )

    assert_frame_equal(
        resultado["listado_campus"].reset_index(drop=True), df.reset_index(drop=True)
    )
    assert resultado["duplicados"].empty
