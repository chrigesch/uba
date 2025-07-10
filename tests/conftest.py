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
def listado_campus_autoevaluaciones_realista():
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
def listado_campus_notas_preliminar_realista():
    data = {
        "Nombre": ["Ana", "Bruno", "Carla"],
        "Apellido(s)": ["Pérez", "Gómez", "Rojas"],
        "Número de ID": [123, 456, 789],
        "Institución": ["Inst A"] * 3,
        "Departamento": ["Depto X"] * 3,
        "Dirección de correo": ["ana@mail.com", "bruno@mail.com", "carla@mail.com"],
        "Tarea:Calificación del Primer Parcial - Primer Cuatrimestre 2025 (Real)": [
            6,
            7,
            None,
        ],
        "Tarea:Calificación del Segundo Parcial - Primer Cuatrimestre 2025 (Real)": [
            6,
            8,
            4,
        ],
        "Última descarga de este curso": ["2025-07-01"] * 3,
    }
    return pd.DataFrame(data)


@pytest.fixture
def listado_campus_notas_final_realista():
    data = {
        "Nombre": ["Ana", "Bruno", "Carla"],
        "Apellido(s)": ["Pérez", "Gómez", "Rojas"],
        "Número de ID": [123, 456, 789],
        "Institución": ["Inst A"] * 3,
        "Departamento": ["Depto X"] * 3,
        "Dirección de correo": ["ana@mail.com", "bruno@mail.com", "carla@mail.com"],
        "Tarea:Calificación del Primer Parcial - Primer Cuatrimestre 2024 (Real)": [
            6,
            7,
            3,
        ],
        "Tarea:Calificación del Segundo Parcial - Primer Cuatrimestre 2024 (Real)": [
            5,
            6,
            4,
        ],
        "Tarea:Calificación del Recuperatorio - Primer Cuatrimestre 2024 (Real)": [
            6,
            None,
            6,
        ],
        "Última descarga de este curso": ["2024-06-30"] * 3,
    }
    return pd.DataFrame(data)


@pytest.fixture
def listado_certificados_realista():
    data = {
        "C": ["01", "01", "01"],
        "AyN": ["Pérez Ana", "Gómez Bruno", "Rojas Carla"],
        "Dni": [123, 456, 789],
        "Certificado_valido_1erParcial": ["sí", "Si", "no"],
        "Tipo_de_certificado_1erParcial": ["médico", "médico", "otro"],
        "Certificado_valido_2doParcial": ["no", "sí", "no"],
        "Tipo_de_certificado_2doParcial": ["", "médico", ""],
    }
    return pd.DataFrame(data)


@pytest.fixture
def columnas_autoevaluacion():
    return ["Autoeval 1", "Autoeval 2"]
