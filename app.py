import streamlit as st
from src.loaders import read_excel_file, read_multiple_excel_files
from src.processors import (
    procesar_stock_actual,
    procesar_ventas_detalladas,
    procesar_ventas_mensuales,
)
from src.integration import consolidar_ventas_mensuales
from src.validation import (
    medir_cruce_codigos,
    medir_cruce_producto_deposito,
)

from src.dataset import construir_dataset_maestro



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

            reportes_mensuales_procesados = []

            for archivo, dataframe in zip(
                mensual_ventas_files,
                mensual_ventas_dataframes,
            ):
                dataframe_limpio = procesar_ventas_mensuales(
                    dataframe
                )

                reportes_mensuales_procesados.append(
                    (
                        archivo.name,
                        dataframe_limpio,
                    )
                )

                with st.expander(
                    f"Vista previa limpia: {archivo.name}"
                ):
                    st.write(
                        f"Filas: {dataframe_limpio.shape[0]} | "
                        f"Columnas: {dataframe_limpio.shape[1]}"
                    )

                    st.dataframe(
                        dataframe_limpio.head(10).astype(str),
                        width="stretch",
                    )

            ventas_mensuales_consolidadas = (
                consolidar_ventas_mensuales(
                    reportes_mensuales_procesados
                )
            )

            st.subheader("Ventas mensuales consolidadas")

            st.write(
                f"Archivos procesados: "
                f"{len(reportes_mensuales_procesados)}"
            )

            st.write(
                f"Filas consolidadas: "
                f"{ventas_mensuales_consolidadas.shape[0]}"
            )

            st.write(
                f"Columnas: "
                f"{ventas_mensuales_consolidadas.shape[1]}"
            )
            
            periodos_detectados = sorted(
                ventas_mensuales_consolidadas[
                    "Periodo"
                ].unique()
            )

            st.write(
                "Períodos detectados: "
                + ", ".join(periodos_detectados)
            )

            st.dataframe(
                ventas_mensuales_consolidadas
                .head(20)
                .astype(str),
                width="stretch",
            )

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

            detalle_ventas_dataframe_limpio = procesar_ventas_detalladas(
                detalle_ventas_dataframe
            )

            with st.expander("Vista previa limpia ventas detalladas"):
                st.write(
                    f"Filas: {detalle_ventas_dataframe_limpio.shape[0]} | "
                    f"Columnas: {detalle_ventas_dataframe_limpio.shape[1]}"
                )

                st.dataframe(
                    detalle_ventas_dataframe_limpio.head(10).astype(str),
                    width="stretch",
                )

        except ValueError as error:
            st.error(str(error))

    if stock_actual_file:
        st.success(
            f"Stock actual cargado: {stock_actual_file.name}"
        )

        try:
            with st.spinner("Leyendo archivo de stock actual..."):
                stock_actual_dataframe = read_excel_file(
                    stock_actual_file
                )
                
            with st.spinner("Normalizando stock actual..."):
                stock_actual_dataframe_limpio = procesar_stock_actual(
                    stock_actual_dataframe
                )

            with st.expander("Vista previa limpia stock actual"):
                st.write(
                    f"Filas: {stock_actual_dataframe_limpio.shape[0]} | "
                    f"Columnas: {stock_actual_dataframe_limpio.shape[1]}"
                )

                st.dataframe(
                    stock_actual_dataframe_limpio.head(10).astype(str),
                    width="stretch",
                )

        except ValueError as error:
            st.error(str(error))
    
    if detalle_ventas_file and stock_actual_file:
        st.divider()
        st.subheader("Validación de cruces")

        try:
            metricas_codigos = medir_cruce_codigos(
                detalle_ventas_dataframe_limpio,
                stock_actual_dataframe_limpio,
            )

            metricas_producto_deposito = (
                medir_cruce_producto_deposito(
                    detalle_ventas_dataframe_limpio,
                    stock_actual_dataframe_limpio,
                )
            )

            st.write("Coincidencia por código de producto")

            columna_1, columna_2, columna_3 = st.columns(3)

            columna_1.metric(
                "Códigos vendidos",
                metricas_codigos["codigos_ventas"],
            )

            columna_2.metric(
                "Códigos coincidentes",
                metricas_codigos["codigos_coincidentes"],
            )

            columna_3.metric(
                "Coincidencia",
                f"{metricas_codigos['porcentaje_coincidencia']:.2f}%",
            )

            st.write("Coincidencia por producto y depósito")

            columna_4, columna_5, columna_6 = st.columns(3)

            columna_4.metric(
                "Combinaciones vendidas",
                metricas_producto_deposito[
                    "combinaciones_ventas"
                ],
            )

            columna_5.metric(
                "Combinaciones coincidentes",
                metricas_producto_deposito[
                    "combinaciones_coincidentes"
                ],
            )

            columna_6.metric(
                "Coincidencia",
                (
                    f"{metricas_producto_deposito['porcentaje_coincidencia']:.2f}%"
                ),
            )

        except ValueError as error:
            st.error(str(error))

    if (
        mensual_ventas_files
        and detalle_ventas_file
        and stock_actual_file
    ):
        st.divider()
        st.subheader("Dataset maestro")

        try:
            with st.spinner(
                "Integrando ventas históricas, ventas recientes y stock..."
            ):
                dataset_maestro = construir_dataset_maestro(
                    ventas_mensuales_consolidadas,
                    detalle_ventas_dataframe_limpio,
                    stock_actual_dataframe_limpio,
                )

            columna_1, columna_2, columna_3 = st.columns(3)

            columna_1.metric(
                "Registros integrados",
                len(dataset_maestro),
            )

            columna_2.metric(
                "Productos",
                dataset_maestro[
                    "codigo_producto"
                ].nunique(),
            )

            columna_3.metric(
                "Depósitos",
                dataset_maestro[
                    "deposito"
                ].nunique(),
            )

            st.dataframe(
                dataset_maestro.head(30),
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