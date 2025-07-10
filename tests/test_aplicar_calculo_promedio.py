# tests/test_aplicar_calculo_promedio.py
import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal

from autoevaluaciones_parcial import _aplicar_calculo_promedio_y_renombrar


def test_aplicar_calculo_promedio_y_renombrar_funciona():
    df = pd.DataFrame(
        {
            "parcial_1": [6, 4, 4, 3, np.nan],
            "parcial_2": [6, 4, 2, 4, 6],
            "nota_recuperatorio": [np.nan, np.nan, 6, 6, 6],
            "cond_prom_6_y_6": [
                "promocion",
                "regular",
                "regular",
                "regular",
                "regular",
            ],
        }
    )

    result = _aplicar_calculo_promedio_y_renombrar(df.copy(), "cond_prom_6_y_6")

    # Chequear columnas nuevas
    assert "promedio" in result.columns
    assert "condicion" in result.columns

    esperado = pd.Series([6.0, 4.0, 5.0, 5.0, 6.0], name="promedio")

    assert_series_equal(result["promedio"], esperado)


def test_aplica_renombrado_columna():
    df = pd.DataFrame(
        {
            "parcial_1": [7],
            "parcial_2": [7],
            "nota_recuperatorio": [np.nan],
            "cond_prom_7_y_7": ["promocion"],
        }
    )

    result = _aplicar_calculo_promedio_y_renombrar(df.copy(), "cond_prom_7_y_7")

    assert "condicion" in result.columns
    assert "cond_prom_7_y_7" not in result.columns
    assert result["condicion"].iloc[0] == "promocion"
