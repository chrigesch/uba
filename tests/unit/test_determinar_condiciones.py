# tests/test_determinar_condiciones.py

import pandas as pd
import numpy as np
from autoevaluaciones_parcial import _determinar_condiciones_de_promocion


def test_evaluar_condiciones_preliminar_varios_estados():
    df = pd.DataFrame(
        {
            "parcial_1": [np.nan, 3, 4, 7],
            "parcial_2": [np.nan, 3, 4, 6],
            "certificado_valido_p1": [False, False, False, False],
            "certificado_valido_p2": [False, False, False, False],
            "diferido": [False] * 4,
        }
    )

    condiciones = ["cond_prom_6_y_6"]
    result = _determinar_condiciones_de_promocion(
        df=df.copy(),
        condicion="preliminar",
        posibles_condiciones=condiciones,
    )

    assert result["cond_prom_6_y_6"].tolist() == [
        "libre",  # ambos parciales ausentes
        "libre_por_nota",  # ambos < 4
        "regular",  # ambos ≥ 4
        "promocion",  # ambos ≥ 6
    ]


def test_evaluar_condiciones_final_con_recuperatorio():
    df = pd.DataFrame(
        {
            "parcial_1": [4, 7, 3],
            "parcial_2": [np.nan, np.nan, 7],
            "nota_recuperatorio": [6, 6, 6],
            "certificado_valido_p1": [False, False, False],
            "certificado_valido_p2": [True, True, False],
            "diferido": [False] * 3,
        }
    )

    condiciones = ["cond_prom_6_y_6"]
    result = _determinar_condiciones_de_promocion(
        df=df.copy(),
        condicion="final",
        posibles_condiciones=condiciones,
    )

    assert result["cond_prom_6_y_6"].tolist() == [
        "regular",  # p1 ≥ 4, p2 ausente y sin certificado, rec ≥ 4
        "promocion",  # p1 ≥ 6, p2 ausente y con certicicado, rec ≥ 6
        "regular",  # p1 < 4, p2 ≥ 6, rec ≥ 6
    ]


def test_evaluar_condiciones_final_con_diferido_pendiente():
    df = pd.DataFrame(
        {
            "parcial_1": [np.nan, 3],
            "parcial_2": [np.nan, np.nan],
            "nota_recuperatorio": [6, 6],
            "certificado_valido_p1": [True, False],
            "certificado_valido_p2": [True, True],
            "diferido": [True, True],
        }
    )

    condiciones = ["cond_prom_6_y_6"]
    result = _determinar_condiciones_de_promocion(
        df=df.copy(),
        condicion="final",
        posibles_condiciones=condiciones,
    )

    assert result["cond_prom_6_y_6"].tolist() == [
        "pendiente",  # ambos ausentes, rec ≥ 4, diferido
        "pendiente",  # p1 < 4, p2 ausente pero con certificado y rec ≥ 4, diferido activo
    ]


def test_evaluar_condiciones_final_sin_recuperatorio():
    df = pd.DataFrame(
        {
            "parcial_1": [3, 4],
            "parcial_2": [3, 2],
            "nota_recuperatorio": [np.nan, np.nan],
            "certificado_valido_p1": [False, False],
            "certificado_valido_p2": [False, False],
            "diferido": [False, False],
        }
    )

    condiciones = ["cond_prom_6_y_6"]
    result = _determinar_condiciones_de_promocion(
        df=df.copy(),
        condicion="final",
        posibles_condiciones=condiciones,
    )

    assert result["cond_prom_6_y_6"].tolist() == [
        "libre_por_nota",  # ambos < 4, sin recup.
        "libre_por_nota",  # uno < 4, otro ≥ 4, sin recup.
    ]


def test_evaluar_varias_condiciones_promocion():
    df = pd.DataFrame(
        {
            "parcial_1": [6],
            "parcial_2": [7],
            "nota_recuperatorio": [np.nan],
            "certificado_valido_p1": [False],
            "certificado_valido_p2": [False],
            "diferido": [False],
        }
    )

    condiciones = ["cond_prom_6_y_6", "cond_prom_7_y_7"]
    result = _determinar_condiciones_de_promocion(
        df=df.copy(),
        condicion="final",
        posibles_condiciones=condiciones,
    )

    assert result["cond_prom_6_y_6"][0] == "promocion"
    assert result["cond_prom_7_y_7"][0] == "regular"
