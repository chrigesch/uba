import pandas as pd
from autoevaluaciones_parcial import cruzar_listas_actas_autoevaluaciones


def test_cruzar_listas_actas_autoevaluaciones_basico(
    listado_actas_realista,
    listado_campus_autoevaluaciones_realista,
):
    resultado = cruzar_listas_actas_autoevaluaciones(
        listado_actas=listado_actas_realista,
        listado_campus=listado_campus_autoevaluaciones_realista,
        parcial=1,
        crear_excel=False,
    )

    # Verificaciones mínimas
    listas = resultado["listas"]
    correcciones = resultado["correcciones"]

    assert "todos" in listas
    assert "resumen" in listas

    df_todos = listas["todos"]
    df_resumen = listas["resumen"]

    # Verificar que se agregó la columna "habilitada/o"
    assert "habilitada/o" in df_todos.columns
    assert df_todos["habilitada/o"].all()  # todos deberían estar habilitados

    # Verificar que el resumen tiene la fila "total"
    assert "total" in df_resumen["C"].values

    # Verificar que correcciones no esté vacío (aunque esté vacío, debe ser dict)
    assert isinstance(correcciones, dict)


def test_cruzar_listas_actas_autoevaluaciones_estudiante_inhabilitado(
    listado_actas_realista,
    listado_campus_autoevaluaciones_realista,
):
    # Modificar el listado_campus para que un/a estudiante tenga una autoevaluación faltante
    listado_campus_modificado = listado_campus_autoevaluaciones_realista.copy()
    listado_campus_modificado.loc[
        1, "Cuestionario:Autoevaluación Unidad 2 - 1er. Cuatrimestre de 2025 (Real)"
    ] = pd.NA

    resultado = cruzar_listas_actas_autoevaluaciones(
        listado_actas=listado_actas_realista,
        listado_campus=listado_campus_modificado,
        parcial=1,
        crear_excel=False,
    )

    todos_df = resultado["listas"]["todos"]
    resumen_df = resultado["listas"]["resumen"]

    # Conteo de valores en la columna "habilitada/o"
    habilitados = todos_df["habilitada/o"].value_counts().get(True, 0)
    inhabilitados = todos_df["habilitada/o"].value_counts().get(False, 0)

    # Verifica que uno esté inhabilitado y dos habilitados
    assert habilitados == 2
    assert inhabilitados == 1

    # Verifica que el resumen refleje correctamente la cuenta
    fila_total = resumen_df[resumen_df["C"] == "total"].iloc[0]
    assert fila_total["habilitados"] == 2
    assert fila_total["inhabilitados"] == 1
    assert fila_total["total"] == 3
