# Import the required libraries
from datetime import datetime
import pandas as pd
import streamlit as st

# Import local modules
from autoevaluaciones_parcial import (
    cruzar_listas_actas_autoevaluaciones,
    cruzar_listas_actas_notas,
    _crear_excel_descargable,
)


OPERACIONES_DISPONIBLES = (
    "Parcial 1",
    "Parcial 2",
    "Condiciones preliminares",
    "Diferencias entre dos actas",
)


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
                label="**Cargar el Excel del campus que incluye las CUATRO autoevaluaciones**",
                type=["xlsx"],
            )
            if uploaded_file_campus is not None:
                listado_campus = pd.read_excel(io=uploaded_file_campus)
                cols = "\n \n".join(listado_campus.columns)
                st.warning(
                    f"Revisar orden de columnas del listado y corregir, si necesario:\n \n{cols}"
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
            mostrar_alumnos_corregidos=False,
            mostrar_duplicados_campus=False,
        )
        len_en_actas_pero_no_en_campus = len(
            resultado["correcciones"]["en_actas_pero_no_en_campus"]
        )
        if len_en_actas_pero_no_en_campus == 0:
            texto = "Todos los alumnos del acta se encontraron en el listado campus"
            st.success(body=texto)
        else:
            texto = f"Cuidado: {len_en_actas_pero_no_en_campus} alumnos en actas, pero NO en el campus:"
            st.warning(body=texto)

        # Pestañas para todos los resultados
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
    # Sacar listado con condiciones preliminares
    if operacion == "Condiciones preliminares":
        col_1, col_2, col_3 = st.columns(3)
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
                label="**Cargar el Excel del campus que incluye las notas de los DOS parciales**",
                type=["xlsx"],
            )
            if uploaded_file_campus is not None:
                listado_campus = pd.read_excel(io=uploaded_file_campus)
                cols = "\n \n".join(listado_campus.columns)
                st.warning(
                    f"Revisar orden de columnas del listado y corregir, si necesario:\n \n{cols}"
                )
        with col_3:
            # Create file uploader object
            uploaded_file_certificados = st.file_uploader(
                label="**Cargar el Excel con los certificados**",
                type=["xlsx"],
            )
            if uploaded_file_certificados is not None:
                listado_certificados = pd.read_excel(io=uploaded_file_certificados)
            else:
                listado_certificados = None

        if (uploaded_file_actas is None) | (uploaded_file_campus is None):
            st.stop()

        resultado_actas_notas = cruzar_listas_actas_notas(
            listado_actas=listado_actas,
            listado_campus=listado_campus,
            listado_certificados=listado_certificados,
            cond_promocion=None,
            condicion="preliminar",
            crear_excel=False,
            mostrar_alumnos_no_encontrados=False,
            mostrar_alumnos_corregidos=False,
            mostrar_duplicados_campus=False,
        )
        len_en_actas_pero_no_en_campus = len(
            resultado_actas_notas["correcciones"]["en_actas_pero_no_en_campus"]
        )
        if len_en_actas_pero_no_en_campus == 0:
            texto = "Todos los alumnos del acta se encontraron en el listado campus"
            st.success(body=texto)
        else:
            texto = f"Cuidado: {len_en_actas_pero_no_en_campus} alumnos en actas, pero NO en el campus:"
            st.warning(body=texto)

        # Pestañas para todos los resultados
        tab_1, tab_2 = st.tabs(tabs=["**Listas**", "**Correcciones**"])
        with tab_1:
            listados_disponibles = resultado_actas_notas["listas"].keys()
            listado_seleccionado = st.selectbox(
                label="**Seleccionar el listado requerido**",
                options=listados_disponibles,
            )
            st.dataframe(resultado_actas_notas["listas"][listado_seleccionado])
        with tab_2:
            listados_disponibles = resultado_actas_notas["correcciones"].keys()
            listado_seleccionado = st.selectbox(
                label="**Seleccionar el listado requerido**",
                options=listados_disponibles,
            )
            st.dataframe(resultado_actas_notas["correcciones"][listado_seleccionado])

        excel_bytes = _crear_excel_descargable(resultado_actas_notas["listas"])
        now = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        nombre_archivo = f"listado_condiciones_preliminares_{now}.xlsx"

        st.download_button(
            label="Descargar el listado de condiciones preliminares",
            data=excel_bytes,
            file_name=nombre_archivo,
        )
    # Analizar diferencias entre dos actas
    if operacion == "Diferencias entre dos actas":
        col_1, col_2 = st.columns(2)
        with col_1:
            # Create file uploader object
            uploaded_file_actas_1 = st.file_uploader(
                label="**Cargar el PRIMER Excel de 'actas'**",
                type=["xlsx"],
            )
            if uploaded_file_actas_1 is not None:
                listado_actas_1 = pd.read_excel(io=uploaded_file_actas_1)
        with col_2:
            # Create file uploader object
            uploaded_file_actas_2 = st.file_uploader(
                label="**Cargar el SEGUNDO Excel de 'actas'**",
                type=["xlsx"],
            )
            if uploaded_file_actas_2 is not None:
                listado_actas_2 = pd.read_excel(io=uploaded_file_actas_2)

        if (uploaded_file_actas_1 is None) | (uploaded_file_actas_2 is None):
            st.stop()

        listado_actas_1["acta"] = 1
        listado_actas_2["acta"] = 2
        listado_actas_juntas = pd.concat([listado_actas_1, listado_actas_2], axis=0)
        alumnos_diferentes = listado_actas_juntas["Dni"].drop_duplicates(keep=False)
        listado_diferencias = listado_actas_juntas[
            listado_actas_juntas["Dni"].isin(alumnos_diferentes)
        ]

        if len(listado_diferencias) == 0:
            texto = "Las dos actas son idénticas"
            st.success(body=texto)
        else:
            texto = (
                f"Cuidado: hay {len(listado_diferencias)} diferencias entre las actas."
            )
            st.warning(body=texto)
            st.dataframe(listado_diferencias)


if __name__ == "__main__":
    main()
