# tests/test_generar_resumen_condiciones.py
import pandas as pd
from pandas.testing import assert_frame_equal
from autoevaluaciones_parcial import _generar_resumen_condiciones


def test_generar_resumen_promociones_basico():
    df = pd.DataFrame(
        {
            "cond_prom_6_y_6": ["promocion", "regular", "libre"],
            "cond_prom_7_y_7": ["libre", "promocion", "promocion"],
        }
    )
    expected = pd.DataFrame(
        {
            "index": ["libre", "libre_por_nota", "regular", "pendiente", "promocion"],
            "cond_prom_6_y_6": [1.0, 0.0, 1.0, 0.0, 1.0],
            "cond_prom_7_y_7": [1.0, 0.0, 0.0, 0.0, 2.0],
        }
    )

    result = _generar_resumen_condiciones(df, ["cond_prom_6_y_6", "cond_prom_7_y_7"])

    # Comparación sin importar el orden de las filas
    assert_frame_equal(
        result.set_index("index").sort_index(),
        expected.set_index("index").sort_index(),
        check_dtype=False,
    )


def test_generar_resumen_ignora_nan():
    df = pd.DataFrame(
        {
            "cond_prom_6_y_6": ["promocion", "regular", None],
        }
    )

    result = _generar_resumen_condiciones(df, ["cond_prom_6_y_6"])
    valores = result["cond_prom_6_y_6"].values

    assert "nan" not in result["index"].astype(str).values
    assert sum(valores) == 2
