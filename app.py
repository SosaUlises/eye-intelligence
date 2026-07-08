import streamlit as st


st.set_page_config(
    page_title="E&E Stock Intelligence",
    page_icon="📊",
    layout="wide"
)


st.title("E&E Stock Intelligence")
st.caption("Sistema inteligente de análisis de ventas, stock y demanda para E&E Calzados.")


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
        "Subí los archivos exportados desde Dux Software para comenzar el análisis."
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

    stock_file = st.file_uploader(
        "Stock actual por sucursal",
        type=["xls", "xlsx"],
        help="Subí el informe de stock actual por producto y depósito.",
    )

    st.divider()

    if mensual_ventas_files:
        st.success(f"Ventas mensuales cargadas: {len(mensual_ventas_files)} archivo/s")

        for file in mensual_ventas_files:
            st.write(f"- {file.name}")

    if detalle_ventas_file :
        st.success(f"Ventas detalladas cargadas: {detalle_ventas_file .name}")

    if stock_file:
        st.success(f"Stock actual cargado: {stock_file.name}")

    if not mensual_ventas_files and not detalle_ventas_file and not stock_file:
        st.info("Todavía no cargaste archivos.")

elif page == "Dashboard":
    st.header("Dashboard comercial")

elif page == "Modelo ML":
    st.header("Modelo de Machine Learning")

elif page == "Asistente IA":
    st.header("Asistente IA")