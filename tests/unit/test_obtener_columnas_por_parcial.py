# tests/test_obtener_columnas_por_parcial.py
from autoevaluaciones_parcial import _obtener_columnas_por_parcial


def test_obtener_columnas_por_parcial():
    assert _obtener_columnas_por_parcial(1) == ["au_1", "au_2", "au_3_p1", "au_3_p2"]
    assert _obtener_columnas_por_parcial(2) == [
        "au_6_p1",
        "au_6_p2",
        "au_7_p1",
        "au_7_p2",
    ]
    assert _obtener_columnas_por_parcial("recuperatorio") == [
        "au_1",
        "au_2",
        "au_3_p1",
        "au_3_p2",
        "au_6_p1",
        "au_6_p2",
        "au_7_p1",
        "au_7_p2",
    ]
