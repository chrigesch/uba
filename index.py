# Import the required libraries
from datetime import datetime
import pandas as pd
import streamlit as st

# Import local modules
from autoevaluaciones_parcial import (
    cruzar_listas_actas_autoevaluaciones,
    _crear_excel_descargable,
)


OPERACIONES_DISPONIBLES = ("Parcial 1", "Parcial 2")


def main():
    # Page setup
    st.set_page_config(
        page_title="Listados",
        layout="wide",
    )

    st.title(body="Listados")
    operacion = st.selectbox(
        label="**Seleccionar el listado requerido**",
        options=OPERACIONES_DISPONIBLES,
    )
    # Sacar listado para habilitados
    if operacion in ("Parcial 1", "Parcial 2"):
        col_1, col_2 = st.columns(2)
        with col_1:
            # Create file uploader object
            uploaded_file_actas = st.file_uploader(
                label="**Cargar el Excel de 'actas'**",
                type=["xlsx"],
            )
            if uploaded_file_actas is not None:
                listado_actas = pd.read_excel(io=uploaded_file_actas)
        with col_2:
            # Create file uploader object
            uploaded_file_campus = st.file_uploader(
                label="**Cargar el Excel con las autoevaluaciones del campus**",
                type=["xlsx"],
            )
            if uploaded_file_campus is not None:
                listado_campus = pd.read_excel(io=uploaded_file_campus)
                cols = "\n \n".join(listado_campus.columns)
                st.warning(
                    f"Revisar orden de columnas del 'listado_campus' y corregir, si necesario:\n \n{cols}"
                )

        if (uploaded_file_actas is None) | (uploaded_file_campus is None):
            st.stop()

        parcial = {"Parcial 1": 1, "Parcial 2": 2}

        resultado = cruzar_listas_actas_autoevaluaciones(
            listado_actas=listado_actas,
            listado_campus=listado_campus,
            parcial=parcial[operacion],  # type: ignore
            crear_excel=False,
            mostrar_alumnos_no_encontrados=False,
            mostrar_alumnos_corregidos=True,
            mostrar_duplicados_campus=True,
        )
        tab_1, tab_2 = st.tabs(tabs=["**Listas**", "**Correcciones**"])
        with tab_1:
            listados_disponibles = resultado["listas"].keys()
            listado_seleccionado = st.selectbox(
                label="**Seleccionar el listado requerido**",
                options=listados_disponibles,
            )
            st.dataframe(resultado["listas"][listado_seleccionado])
        with tab_2:
            listados_disponibles = resultado["correcciones"].keys()
            listado_seleccionado = st.selectbox(
                label="**Seleccionar el listado requerido**",
                options=listados_disponibles,
            )
            st.dataframe(resultado["correcciones"][listado_seleccionado])

        excel_bytes = _crear_excel_descargable(resultado["listas"])
        now = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        nombre_archivo = f"listado_habilitados_parcial_{parcial[operacion]}_{now}.xlsx"

        st.download_button(
            label="Descargar el listado de habilitadados",
            data=excel_bytes,
            file_name=nombre_archivo,
        )


if __name__ == "__main__":
    main()
