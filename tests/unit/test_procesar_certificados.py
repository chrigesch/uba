# tests/test_procesar_certificados.py
import numpy as np
import pandas as pd
import pytest

from autoevaluaciones_parcial import _procesar_certificados


def test_procesar_certificados_none():
    df_notas = pd.DataFrame({"Dni": [1, 2]})
    df_actas = df_notas.copy()
    result = _procesar_certificados(
        listado_cruzado=df_notas.copy(),
        listado_actas=df_actas,
        listado_certificados=None,
        condicion="preliminar",
    )

    assert result["certificado_valido_p1"].eq(False).all()
    assert result["certificado_valido_p2"].eq(False).all()
    assert result["tipo_de_certificado_p1"].isna().all()
    assert result["tipo_de_certificado_p2"].isna().all()


def test_procesar_certificados_final_valores_invalidos():
    df_notas = pd.DataFrame({"Dni": [1, 2, 3, 4]})
    df_actas = df_notas.copy()

    # Valores: si / no / desconocido / NaN
    df_certs = pd.DataFrame(
        {
            "Dni": [1, 2, 3, 4],
            "certificado_valido_p1": ["si", "no", "tal vez", None],
            "tipo_de_certificado_p1": ["a", "b", "c", "d"],
            "certificado_valido_p2": ["x", "sí", "no", np.nan],
            "tipo_de_certificado_p2": ["e", "f", "g", "h"],
        }
    )

    with pytest.raises(ValueError) as excinfo:
        _procesar_certificados(
            listado_cruzado=df_notas.copy(),
            listado_actas=df_actas,
            listado_certificados=df_certs,
            condicion="final",
        )

    # Comprobamos que el error realmente menciona el problema
    msg = str(excinfo.value).lower()
    assert "condición" in msg


def test_procesar_certificados_preliminar_convierte_desconocidos_en_si():
    df_notas = pd.DataFrame({"Dni": [1, 2, 3, 4]})
    df_actas = df_notas.copy()

    # Valores: si / no / desconocido / NaN
    df_certs = pd.DataFrame(
        {
            "Dni": [1, 2, 3, 4],
            "certificado_valido_p1": ["si", "no", "tal vez", None],
            "tipo_de_certificado_p1": ["a", "b", "c", "d"],
            "certificado_valido_p2": ["x", "sí", "no", np.nan],
            "tipo_de_certificado_p2": ["e", "f", "g", "h"],
        }
    )

    result = _procesar_certificados(
        df_notas.copy(),
        df_actas,
        df_certs,
        condicion="preliminar",
    )

    # P1: si → True ; no → False ; "tal vez" → True ; None → False  (porque None → "no")
    assert result["certificado_valido_p1"].tolist() == [True, False, True, False]

    # P2: "x" → True ; "sí" → True ; "no" → False ; "" → True
    assert result["certificado_valido_p2"].tolist() == [True, True, False, False]


def test_procesar_certificados_varias_formas_si():
    df_notas = pd.DataFrame({"Dni": [1, 2, 3]})
    df_actas = df_notas.copy()
    df_certs = pd.DataFrame(
        {
            "Dni": [1, 2, 3],
            "irrelevante": ["a", "b", "c"],
            "colX": [1, 2, 3],
            "certificado_valido_p1": ["Si", "sí", "no"],
            "tipo_de_certificado_p1": ["medico", "familiar", "otro"],
            "certificado_valido_p2": ["sí", "no", "Si"],
            "tipo_de_certificado_p2": ["x", "y", "z"],
        }
    )

    result = _procesar_certificados(
        listado_cruzado=df_notas.copy(),
        listado_actas=df_actas,
        listado_certificados=df_certs,
        condicion="preliminar",
    )

    assert result["certificado_valido_p1"].tolist() == [True, True, False]
    assert result["certificado_valido_p2"].tolist() == [True, False, True]
