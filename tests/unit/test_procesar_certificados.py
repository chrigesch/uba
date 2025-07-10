# tests/test_procesar_certificados.py
import pandas as pd

from autoevaluaciones_parcial import _procesar_certificados


def test_procesar_certificados_none():
    df_notas = pd.DataFrame({"Dni": [1, 2]})
    df_actas = df_notas.copy()
    result = _procesar_certificados(
        df_notas.copy(),
        df_actas,
        listado_certificados=None,
    )

    assert result["certificado_valido_p1"].eq(False).all()
    assert result["certificado_valido_p2"].eq(False).all()
    assert result["tipo_de_certificado_p1"].isna().all()
    assert result["tipo_de_certificado_p2"].isna().all()


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

    result = _procesar_certificados(df_notas.copy(), df_actas, df_certs)

    assert result["certificado_valido_p1"].tolist() == [True, True, False]
    assert result["certificado_valido_p2"].tolist() == [True, False, True]
