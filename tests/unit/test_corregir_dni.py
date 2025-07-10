# tests/test_corregir_dni.py
import pandas as pd
from pandas.testing import assert_frame_equal
from autoevaluaciones_parcial import _corregir_dni_en_listado_campus


def test_corregir_dni_por_correo(
    df_listado_actas,
    df_listado_campus_completo,
):
    resultado = _corregir_dni_en_listado_campus(
        listado_actas=df_listado_actas,
        listado_campus=df_listado_campus_completo,
        mostrar_alumnos_no_encontrados=False,
        mostrar_alumnos_corregidos=False,
    )

    # Comprobamos que al menos uno de los DNIs se corrigió usando correo
    assert 12345678 in resultado["listado_campus"]["Número de ID"].tolist()


def test_corregir_dni_por_truncamiento(
    df_listado_actas,
    df_listado_campus_completo,
):
    resultado = _corregir_dni_en_listado_campus(
        listado_actas=df_listado_actas,
        listado_campus=df_listado_campus_completo,
        mostrar_alumnos_no_encontrados=False,
        mostrar_alumnos_corregidos=False,
    )

    # El DNI con 9 dígitos debe haber sido corregido a 87654321
    assert 87654321 in resultado["listado_campus"]["Número de ID"].tolist()


def test_detectar_dni_en_actas_pero_no_en_campus(df_listado_actas):
    df_campus = pd.DataFrame(
        {
            "Número de ID": [12345678],
            "Dirección de correo": ["juan@mail.com"],
            "Nombre": ["Juan"],
        }
    )

    resultado = _corregir_dni_en_listado_campus(
        listado_actas=df_listado_actas,
        listado_campus=df_campus,
        mostrar_alumnos_no_encontrados=False,
        mostrar_alumnos_corregidos=False,
    )

    df_esperado = pd.DataFrame({"Dni": [87654321], "e-mail": ["ana@mail.com"]})

    assert_frame_equal(
        resultado["en_actas_pero_no_en_campus"].reset_index(drop=True),
        df_esperado.reset_index(drop=True),
    )
