# tests/conftest.py
import pytest
import pandas as pd


@pytest.fixture
def df_listado_actas():
    return pd.DataFrame(
        {"Dni": [87654321, 12345678], "e-mail": ["ana@mail.com", "juan@mail.com"]}
    )


@pytest.fixture
def listado_actas_realista():
    return pd.DataFrame(
        {
            "O": [1, 2, 3],
            "C": ["A", "A", "B"],
            "Libreta": ["2025001", "2025002", "2025003"],
            "Dni": [111, 222, 333],
            "AyN": ["Ana Pérez", "Luis Gómez", "Mara Díaz"],
            "e-mail": ["ana@ejemplo.com", "luis@ejemplo.com", "mara@ejemplo.com"],
            "Teléfono": ["123456789", "987654321", "555555555"],
            "Fecha Nac.": ["2000-01-01", "1999-05-15", "2001-08-20"],
        }
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
def listado_campus_realista():
    return pd.DataFrame(
        {
            "Nombre": ["Ana", "Luis", "Mara"],
            "Apellido(s)": ["Pérez", "Gómez", "Díaz"],
            "Número de ID": [111, 222, 333],
            "Institución": ["UBA", "UBA", "UBA"],
            "Departamento": ["Psicología", "Psicología", "Psicología"],
            "Dirección de correo": [
                "ana@ejemplo.com",
                "luis@ejemplo.com",
                "mara@ejemplo.com",
            ],
            "Cuestionario:Autoevaluación Unidad 1 - 1er Cuatrimestre de 2025 (Real)": [
                1,
                1,
                1,
            ],
            "Cuestionario:Autoevaluación Unidad 2 - 1er. Cuatrimestre de 2025 (Real)": [
                1,
                1,
                1,
            ],
            "Cuestionario:Autoevaluación Unidad 3 - Parte 1 - 1er. Cuatrimestre de 2025 (Real)": [
                1,
                1,
                1,
            ],
            "Cuestionario:Autoevaluación Unidad 3 - Parte 2 - 1er. Cuatrimestre de 2025 (Real)": [
                1,
                1,
                1,
            ],
            "Última descarga de este curso": ["2025-07-01"] * 3,
        }
    )


@pytest.fixture
def columnas_autoevaluacion():
    return ["Autoeval 1", "Autoeval 2"]
