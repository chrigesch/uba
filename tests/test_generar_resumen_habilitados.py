# test/test_generar_resumen_habilitados.py
import pandas as pd
from pandas.testing import assert_frame_equal

from autoevaluaciones_parcial import _generar_resumen_habilitados


def test_generar_resumen_habilitacion():
    df = pd.DataFrame(
        {
            "C": ["1", "1", "2", "2"],
            "habilitada/o": [True, False, True, True],
        }
    )

    resumen = _generar_resumen_habilitados(df)

    esperado = pd.DataFrame(
        {
            "C": ["1", "2", "total"],
            "habilitados": [1, 2, 3],
            "inhabilitados": [1, 0, 1],
            "total": [2, 2, 4],
        }
    )

    assert_frame_equal(
        resumen.sort_values(by="C").reset_index(drop=True),
        esperado.sort_values(by="C").reset_index(drop=True),
        check_dtype=False,
    )
