from autoevaluaciones_parcial import cruzar_listas_actas_notas


def test_cruzar_listas_actas_notas_preliminar_funciona(
    listado_actas_realista,
    listado_campus_notas_preliminar_realista,
):
    resultado = cruzar_listas_actas_notas(
        listado_actas=listado_actas_realista,
        listado_campus=listado_campus_notas_preliminar_realista,
        listado_certificados=None,
        cond_promocion="cond_prom_6_y_6",
        condicion="preliminar",
        crear_excel=False,
    )

    todos_df = resultado["listas"]["todos"]
    resumen_df = resultado["listas"]["resumen"]

    # Verificar que se haya agregado la columna de promoción
    assert "cond_prom_6_y_6" in todos_df.columns

    # Verificar que hay al menos un estudiante clasificado como "promocion" o "regular"
    valores_posibles = todos_df["cond_prom_6_y_6"].unique()
    assert any(v in valores_posibles for v in ["promocion", "regular", "libre"])

    # Verificar que el resumen contenga fila para la condición usada
    assert "cond_prom_6_y_6" in resumen_df.columns
    assert "index" in resumen_df.columns


def test_cruzar_listas_actas_notas_final_con_certificados_funciona(
    listado_actas_realista,
    listado_campus_notas_final_realista,
    listado_certificados_realista,
):
    resultado = cruzar_listas_actas_notas(
        listado_actas=listado_actas_realista,
        listado_campus=listado_campus_notas_final_realista,
        listado_certificados=listado_certificados_realista,
        cond_promocion="cond_prom_6_y_6",
        condicion="final",
        crear_excel=False,
    )

    todos_df = resultado["listas"]["todos"]
    resumen_df = resultado["listas"]["resumen"]

    # Verificar columnas clave
    for col in [
        "condicion",
        "certificado_valido_p1",
        "certificado_valido_p2",
        "diferido",
        "recuperatorio",
        "promedio",
    ]:
        assert col in todos_df.columns

    # Verificar redondeo del promedio
    promedios_validos = todos_df["promedio"].dropna()
    assert all(promedios_validos.apply(lambda x: isinstance(x, (int, float))))

    # Verificar contenido del resumen
    assert resumen_df["cond_prom_6_y_6"].sum() > 0
