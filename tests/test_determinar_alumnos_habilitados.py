# test/test_determinar_alumnos_habilitados.py
import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal

from autoevaluaciones_parcial import _determinar_alumnos_habilitados


def test_marcar_alumnos_habilitados_funciona():
    df = pd.DataFrame(
        {
            "C": ["1", "1", "2"],
            "AyN": ["Ana", "Luis", "Mara"],
            "au_1": [1, np.nan, 1],
            "au_2": [1, 1, 1],
            "au_3_p1": [1, 1, 1],
            "au_3_p2": [1, 1, 1],
        }
    )

    columnas = ["au_1", "au_2", "au_3_p1", "au_3_p2"]

    df_resultado = _determinar_alumnos_habilitados(df.copy(), columnas)

    esperado = pd.Series([True, False, True], name="habilitada/o")

    assert_series_equal(
        df_resultado["habilitada/o"].sort_index().reset_index(drop=True),
        esperado.sort_index().reset_index(drop=True),
    )
