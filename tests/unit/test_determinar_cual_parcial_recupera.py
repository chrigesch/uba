# tests/test_calcular_recuperatorio.py

import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal

from autoevaluaciones_parcial import _determinar_cual_parcial_recupera


def test_recuperatorio_p2_cuando_p2_desaprobado():
    df = pd.DataFrame(
        {
            "parcial_2": [3, np.nan],
            "cond_prom_6_y_6": ["pendiente", "pendiente"],
        }
    )

    result = _determinar_cual_parcial_recupera(df=df.copy())

    assert result["recuperatorio"].tolist() == [2, 2]


def test_recuperatorio_p1_cuando_p2_aprobado():
    df = pd.DataFrame(
        {
            "parcial_2": [4, 9],
            "cond_prom_6_y_6": ["pendiente", "pendiente"],
        }
    )

    result = _determinar_cual_parcial_recupera(df=df.copy())

    assert result["recuperatorio"].tolist() == [1, 1]


def test_sin_pendiente_sin_recuperatorio():
    df = pd.DataFrame(
        {
            "parcial_2": [2, 3, 4],
            "cond_prom_6_y_6": ["regular", "libre", "promocion"],
        }
    )

    result = _determinar_cual_parcial_recupera(df=df.copy())

    assert result["recuperatorio"].isna().all()


def test_recuperatorio_mixto():
    df = pd.DataFrame(
        {
            "parcial_2": [np.nan, 7, 2],
            "cond_prom_6_y_6": ["pendiente", "pendiente", "libre"],
        }
    )

    result = _determinar_cual_parcial_recupera(df=df.copy())
    esperado = pd.Series([2, 1, np.nan], name="recuperatorio")

    assert_series_equal(result["recuperatorio"], esperado)
