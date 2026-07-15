import streamlit as st
from src.data.loaders import read_excel_file, read_multiple_excel_files
from src.data.processors import (
    procesar_stock_actual,
    procesar_ventas_detalladas,
    procesar_ventas_mensuales,
)
from src.data.integration import consolidar_ventas_mensuales
from src.data.validation import (
    medir_cruce_codigos,
    medir_cruce_producto_deposito,
)

from src.data.dataset import construir_dataset_maestro
from src.analytics.dashboard import (
    calcular_kpis,
    filtrar_dataset,
    obtener_productos_sin_movimiento,
    obtener_rango_fechas_recientes,
    obtener_top_productos,
    obtener_ventas_por_rubro,
)
from src.analytics.features import construir_features

from src.ml.machine_learning import (
    asignar_nombre_clusters,
    entrenar_modelo_segmentacion,
    incorporar_perfiles_comerciales,
    obtener_productos_representativos,
    obtener_resumen_clusters,
)
from src.ml.ml_dataset import construir_dataset_ml


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

            st.session_state["ventas_mensuales_consolidadas"] = (
            ventas_mensuales_consolidadas
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
                dataset_features = construir_features(
                dataset_maestro
                )


            st.session_state["dataset_maestro"] = dataset_maestro
            st.session_state["dataset_features"] = dataset_features


            st.session_state["periodo_historico_desde"] = (
                ventas_mensuales_consolidadas["Periodo"].min()
            )

            st.session_state["periodo_historico_hasta"] = (
                ventas_mensuales_consolidadas["Periodo"].max()
            )

            st.session_state["cantidad_periodos_historicos"] = (
                ventas_mensuales_consolidadas["Periodo"].nunique()
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

    if "dataset_maestro" not in st.session_state:
        st.warning(
            "Primero debés cargar y procesar los archivos "
            "desde la sección Carga de datos."
        )

    else:
        dataset_maestro = st.session_state["dataset_maestro"]

        st.subheader("Filtros")

        depositos_disponibles = sorted(
            dataset_maestro["deposito"]
            .dropna()
            .unique()
            .tolist()
        )

        rubros_disponibles = sorted(
            dataset_maestro["rubro"]
            .dropna()
            .unique()
            .tolist()
        )

        marcas_disponibles = sorted(
            dataset_maestro["marca"]
            .dropna()
            .unique()
            .tolist()
        )

        columna_filtro_1, columna_filtro_2, columna_filtro_3 = (
            st.columns(3)
        )

        depositos_seleccionados = columna_filtro_1.multiselect(
            "Depósitos",
            options=depositos_disponibles,
        )

        rubros_seleccionados = columna_filtro_2.multiselect(
            "Rubros",
            options=rubros_disponibles,
        )

        marcas_seleccionadas = columna_filtro_3.multiselect(
            "Marcas",
            options=marcas_disponibles,
        )

        dataset_filtrado = filtrar_dataset(
            dataset_maestro,
            depositos=depositos_seleccionados,
            rubros=rubros_seleccionados,
            marcas=marcas_seleccionadas,
        )

        if dataset_filtrado.empty:
            st.warning(
                "No hay datos para la combinación "
                "de filtros seleccionada."
            )
            st.stop()

        st.divider()

        st.subheader("Períodos analizados")

        periodo_historico_desde = st.session_state.get(
            "periodo_historico_desde"
        )

        periodo_historico_hasta = st.session_state.get(
            "periodo_historico_hasta"
        )

        cantidad_periodos_historicos = st.session_state.get(
            "cantidad_periodos_historicos",
            0,
        )

        fecha_reciente_desde, fecha_reciente_hasta = (
            obtener_rango_fechas_recientes(
                dataset_filtrado
            )
        )

        columna_periodo_1, columna_periodo_2, columna_periodo_3 = (
            st.columns(3)
        )

        columna_periodo_1.info(
            "Histórico mensual\n\n"
            f"{periodo_historico_desde} a "
            f"{periodo_historico_hasta}\n\n"
            f"{cantidad_periodos_historicos} períodos"
        )

        if (
            fecha_reciente_desde is not None
            and fecha_reciente_hasta is not None
        ):
            columna_periodo_2.info(
                "Ventas recientes\n\n"
                f"{fecha_reciente_desde.strftime('%d/%m/%Y')} "
                f"al "
                f"{fecha_reciente_hasta.strftime('%d/%m/%Y')}"
            )
        else:
            columna_periodo_2.info(
                "Ventas recientes\n\n"
                "Sin fechas disponibles"
            )

        columna_periodo_3.info(
            "Stock\n\n"
            "Estado actual al momento de la carga"
        )

        st.caption(
            f"Registros analizados: {len(dataset_filtrado):,}"
        )

        try:

            kpis = calcular_kpis(
                dataset_filtrado
            )
            
            st.subheader("Resumen general")

            columna_1, columna_2, columna_3, columna_4 = (
                st.columns(4)
            )

            columna_1.metric(
                "Ventas recientes (60 días)",
                f"${kpis['monto_ventas_recientes']:,.0f}",
            )

            columna_2.metric(
                "Stock disponible actual",
                f"{kpis['stock_disponible']:,.0f}",
            )

            columna_3.metric(
                "Unidades vendidas (60 días)",
                f"{kpis['unidades_vendidas_recientes']:,.0f}",
            )

            columna_4.metric(
                "Promedio mensual histórico",
                f"{kpis['promedio_mensual_historico']:,.0f}",
                help=(
                    "Promedio mensual calculado sobre "
                    f"{kpis['cantidad_periodos_historicos']} períodos."
                ),
            )

            st.divider()

            st.subheader(
                "Ventas por rubro — período reciente"
            )

            ventas_por_rubro = obtener_ventas_por_rubro(
                dataset_filtrado
            )

            st.bar_chart(
                ventas_por_rubro,
                x="rubro",
                y="unidades_vendidas",
            )

            st.divider()

            st.subheader(
                "Productos más vendidos — período reciente"
            )

            top_productos = obtener_top_productos(
                dataset_filtrado,
                limite=10,
            )

            st.dataframe(
                top_productos,
                width="stretch",
                hide_index=True,
            )

            st.divider()

            st.subheader(
                "Productos con stock sin movimiento"
            )

            st.caption(
                "Productos con stock disponible que no "
                "registraron ventas durante el período reciente."
            )

            productos_sin_movimiento = (
                obtener_productos_sin_movimiento(
                    dataset_filtrado,
                    limite=10,
                )
            )

            if productos_sin_movimiento.empty:
                st.info(
                    "Todos los productos con stock registraron "
                    "ventas durante el período reciente."
                )

            else:
                st.dataframe(
                    productos_sin_movimiento,
                    width="stretch",
                    hide_index=True,
                )

        except ValueError as error:
            st.error(str(error))

elif page == "Modelo ML":
    st.header("Modelo de Machine Learning")

    st.write(
        "El modelo agrupa productos con comportamientos "
        "comerciales similares mediante K-Means."
    )

    if "dataset_maestro" not in st.session_state:
        st.warning(
            "Primero debés cargar y procesar los archivos "
            "desde la sección Carga de datos."
        )

    else:
        dataset_maestro = st.session_state[
            "dataset_maestro"
        ]

        try:
            with st.spinner(
                "Construyendo variables y entrenando el modelo..."
            ):
                dataset_ml = construir_dataset_ml(
                    dataset_maestro
                )

                (
                    modelo,
                    escalador,
                    dataset_segmentado,
                    puntaje_silueta,
                ) = entrenar_modelo_segmentacion(
                    dataset_ml,
                    cantidad_clusters=4,
                )

                resumen_clusters = obtener_resumen_clusters(
                    dataset_segmentado
                )

                nombres_clusters = asignar_nombre_clusters(
                    resumen_clusters
                )

                resultados_ml = (
                    incorporar_perfiles_comerciales(
                        dataset_segmentado,
                        nombres_clusters,
                    )
                )

                productos_representativos = obtener_productos_representativos(
                    resultados_ml,
                    limite_por_grupo=5,
                )


            st.session_state["modelo_ml"] = modelo
            st.session_state["escalador_ml"] = escalador
            st.session_state["resultados_ml"] = resultados_ml
            st.session_state["resumen_clusters"] = resumen_clusters
            st.session_state["productos_representativos"] = (
                productos_representativos
            )

            columna_1, columna_2, columna_3 = st.columns(3)

            columna_1.metric(
                "Productos analizados",
                f"{len(resultados_ml):,}",
            )

            columna_2.metric(
                "Grupos detectados",
                f"{resultados_ml['cluster'].nunique()}",
            )

            columna_3.metric(
                "Puntaje de silueta",
                f"{puntaje_silueta:.3f}",
                help=(
                    "Mide qué tan separados están los grupos. "
                    "Valores mayores indican mejor separación."
                ),
            )

            st.subheader("Resumen de grupos")

            resumen_mostrable = resumen_clusters.copy()

            resumen_mostrable["perfil_comercial"] = (
                resumen_mostrable["cluster"].map(
                    nombres_clusters
                )
            )

            st.dataframe(
                resumen_mostrable,
                width="stretch",
                hide_index=True,
            )

            st.subheader("Productos representativos por perfil")

            st.dataframe(
                productos_representativos[
                    [
                        "perfil_comercial",
                        "codigo_producto",
                        "producto",
                        "deposito",
                        "stock_disponible",
                        "ventas_recientes_mensualizadas",
                        "promedio_ventas_mensual",
                        "cobertura_stock_meses",
                        "rotacion_reciente",
                    ]
                ],
                width="stretch",
                hide_index=True,
            )

            st.subheader("Clasificación comercial de productos")

            columnas_resultado = [
                "codigo_producto",
                "producto",
                "deposito",
                "stock_disponible",
                "ventas_recientes_mensualizadas",
                "promedio_ventas_mensual",
                "cobertura_stock_meses",
                "rotacion_reciente",
                "perfil_comercial",
            ]

            st.dataframe(
                resultados_ml[
                    columnas_resultado
                ].sort_values(
                    by=[
                        "perfil_comercial",
                        "stock_disponible",
                    ],
                    ascending=[
                        True,
                        False,
                    ],
                ),
                width="stretch",
                hide_index=True,
            )

        except ValueError as error:
            st.error(str(error))

elif page == "Asistente IA":
    st.header("Asistente IA")
    st.info(
        "Esta sección permitirá consultar "
        "los resultados en lenguaje natural."
    )