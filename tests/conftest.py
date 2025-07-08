# tests/conftest.py
import pytest
import pandas as pd


@pytest.fixture
def df_listado_actas():
    return pd.DataFrame(
        {"Dni": [87654321, 12345678], "e-mail": ["ana@mail.com", "juan@mail.com"]}
    )


@pytest.fixture
def df_listado_campus_completo():
    return pd.DataFrame(
        {
            "Número de ID": [
                87654321,  # caso válido
                123456789,  # dígito de más
                87654321,  # duplicado
                11111111,  # con "-"
                22222222,  # con "Ausente"
            ],
            "Dirección de correo": [
                "ana@mail.com",
                "juan@mail.com",
                "ana_dup@mail.com",
                "caso@guion.com",
                "caso@ausente.com",
            ],
            "Nombre": ["Ana", "Juan", "Ana duplicada", "Guión", "Ausente"],
            "Autoeval 1": [5.0, 4.0, None, 3.0, "Ausente"],
            "Autoeval 2": [4.0, 3.0, None, "-", 2.0],
            "Sobrante": ["X", "Y", "Z", "A", "B"],
        }
    )


@pytest.fixture
def columnas_autoevaluacion():
    return ["Autoeval 1", "Autoeval 2"]
