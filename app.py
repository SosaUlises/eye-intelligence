import streamlit as st
from src.cleaning import normalizar_excel_dux
from src.loaders import read_excel_file, read_multiple_excel_files


st.set_page_config(
    page_title="E&E Stock Intelligence",
    page_icon="📊",
    layout="wide",
)


st.title("E&E Stock Intelligence")
st.caption(
    "Sistema inteligente de análisis de ventas, stock y demanda para E&E Calzados."
)


st.sidebar.title("Navegación")

page = st.sidebar.radio(
    "Seleccioná una sección",
    [
        "Carga de datos",
        "Dashboard",
        "Modelo ML",
        "Asistente IA",
    ],
)


if page == "Carga de datos":
    st.header("Carga de datos de Dux")

    st.write(
        "Subí los archivos exportados desde Dux Software "
        "para comenzar el análisis."
    )

    mensual_ventas_files = st.file_uploader(
        "Ventas mensuales por producto",
        type=["xls", "xlsx"],
        accept_multiple_files=True,
        help="Subí los Excel mensuales de ventas por producto.",
    )

    detalle_ventas_file = st.file_uploader(
        "Ventas detalladas recientes",
        type=["xls", "xlsx"],
        help="Subí el informe de ventas detalladas recientes.",
    )

    stock_actual_file = st.file_uploader(
        "Stock actual por sucursal",
        type=["xls", "xlsx"],
        help="Subí el informe de stock actual por producto y depósito.",
    )

    st.divider()

    if mensual_ventas_files:
        st.success(
            f"Ventas mensuales cargadas: "
            f"{len(mensual_ventas_files)} archivo/s"
        )

        try:
            mensual_ventas_dataframes = read_multiple_excel_files(
                mensual_ventas_files
            )

            columnas_requeridas_ventas_mensuales = {
                "Código",
                "Producto",
                "Cantidad Total Vendida",
                "Monto Vendido",
            }

            for file, dataframe in zip(
                mensual_ventas_files,
                mensual_ventas_dataframes,
            ):
                with st.expander(f"Vista previa limpia: {file.name}"):
                    try:
                        dataframe_limpio = normalizar_excel_dux(
                            dataframe,
                            columnas_requeridas_ventas_mensuales,
                        )

                        st.write(
                            f"Filas: {dataframe_limpio.shape[0]} | "
                            f"Columnas: {dataframe_limpio.shape[1]}"
                        )

                        st.dataframe(
                            dataframe_limpio.head(10).astype(str),
                            width="stretch",
                        )

                    except ValueError as error:
                        st.error(str(error))

        except ValueError as error:
            st.error(str(error))

    if detalle_ventas_file:
        st.success(
            f"Ventas detalladas cargadas: "
            f"{detalle_ventas_file.name}"
        )

        try:
            detalle_ventas_dataframe = read_excel_file(
                detalle_ventas_file
            )

            with st.expander("Vista previa ventas detalladas"):
                st.write(
                    f"Filas: {detalle_ventas_dataframe.shape[0]} | "
                    f"Columnas: {detalle_ventas_dataframe.shape[1]}"
                )

                st.dataframe(
                    detalle_ventas_dataframe.head(10).astype(str),
                    width="stretch",
                )

        except ValueError as error:
            st.error(str(error))

    if stock_actual_file:
        st.success(
            f"Stock actual cargado: {stock_actual_file.name}"
        )

        try:
            stock_actual_dataframe = read_excel_file(
                stock_actual_file
            )

            with st.expander("Vista previa stock actual"):
                st.write(
                    f"Filas: {stock_actual_dataframe.shape[0]} | "
                    f"Columnas: {stock_actual_dataframe.shape[1]}"
                )

                st.dataframe(
                    stock_actual_dataframe.head(10).astype(str),
                    width="stretch",
                )

        except ValueError as error:
            st.error(str(error))

    if (
        not mensual_ventas_files
        and not detalle_ventas_file
        and not stock_actual_file
    ):
        st.info("Todavía no cargaste archivos.")

elif page == "Dashboard":
    st.header("Dashboard comercial")
    st.info(
        "Esta sección se completará cuando procesemos los datos."
    )

elif page == "Modelo ML":
    st.header("Modelo de Machine Learning")
    st.info(
        "Esta sección mostrará entrenamiento, "
        "evaluación y predicciones."
    )

elif page == "Asistente IA":
    st.header("Asistente IA")
    st.info(
        "Esta sección permitirá consultar "
        "los resultados en lenguaje natural."
    )