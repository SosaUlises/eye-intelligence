import pandas as pd


def filtrar_dataset(
    dataset_maestro: pd.DataFrame,
    depositos: list[str] | None = None,
    rubros: list[str] | None = None,
    marcas: list[str] | None = None,
) -> pd.DataFrame:
    """
    Filtra el dataset maestro por depósito, rubro y marca.
    """

    dataset_filtrado = dataset_maestro.copy()

    if depositos:
        dataset_filtrado = dataset_filtrado[
            dataset_filtrado["deposito"].isin(depositos)
        ]

    if rubros:
        dataset_filtrado = dataset_filtrado[
            dataset_filtrado["rubro"].isin(rubros)
        ]

    if marcas:
        dataset_filtrado = dataset_filtrado[
            dataset_filtrado["marca"].isin(marcas)
        ]

    return dataset_filtrado


def calcular_kpis(
    dataset_maestro: pd.DataFrame,
) -> dict[str, int | float]:
    """
    Calcula los indicadores principales del dashboard.

    Las ventas recientes corresponden al archivo detallado.
    Las ventas históricas se calculan una sola vez por producto
    para evitar duplicarlas entre depósitos.
    """

    columnas_requeridas = {
        "codigo_producto",
        "deposito",
        "stock_disponible",
        "ventas_recientes",
        "monto_reciente",
        "ventas_historicas",
        "periodos_analizados",
    }

    columnas_faltantes = columnas_requeridas.difference(
        dataset_maestro.columns
    )

    if columnas_faltantes:
        raise ValueError(
            "Faltan columnas para calcular los KPIs: "
            + ", ".join(sorted(columnas_faltantes))
        )

    productos_sin_ventas = dataset_maestro.loc[
        (dataset_maestro["stock_disponible"] > 0)
        & (dataset_maestro["ventas_recientes"] <= 0),
        "codigo_producto",
    ].nunique()

    historico_por_producto = (
        dataset_maestro[
            [
                "codigo_producto",
                "ventas_historicas",
                "periodos_analizados",
            ]
        ]
        .drop_duplicates(subset=["codigo_producto"])
        .copy()
    )

    cantidad_periodos = int(
        historico_por_producto["periodos_analizados"].max()
    )

    ventas_historicas_totales = (
        historico_por_producto["ventas_historicas"].sum()
    )

    promedio_mensual_historico = (
        ventas_historicas_totales / cantidad_periodos
        if cantidad_periodos > 0
        else 0
    )

    return {
        "productos": dataset_maestro[
            "codigo_producto"
        ].nunique(),
        "depositos": dataset_maestro[
            "deposito"
        ].nunique(),
        "stock_disponible": dataset_maestro[
            "stock_disponible"
        ].sum(),
        "unidades_vendidas_recientes": dataset_maestro[
            "ventas_recientes"
        ].sum(),
        "monto_ventas_recientes": dataset_maestro[
            "monto_reciente"
        ].sum(),
        "productos_sin_ventas": productos_sin_ventas,
        "promedio_mensual_historico": promedio_mensual_historico,
        "cantidad_periodos_historicos": cantidad_periodos,
    }


def obtener_rango_fechas_recientes(
    dataset_maestro: pd.DataFrame,
) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    """
    Obtiene el rango real del archivo de ventas detalladas.
    """

    fechas = pd.concat(
        [
            dataset_maestro["primera_venta"],
            dataset_maestro["ultima_venta"],
        ]
    ).dropna()

    if fechas.empty:
        return None, None

    return fechas.min(), fechas.max()


def obtener_ventas_por_rubro(
    dataset_maestro: pd.DataFrame,
) -> pd.DataFrame:
    """
    Agrupa las ventas recientes por rubro.
    """

    return (
        dataset_maestro.dropna(subset=["rubro"])
        .groupby(
            "rubro",
            as_index=False,
        )
        .agg(
            unidades_vendidas=(
                "ventas_recientes",
                "sum",
            ),
        )
        .sort_values(
            by="unidades_vendidas",
            ascending=False,
        )
    )


def obtener_top_productos(
    dataset_maestro: pd.DataFrame,
    limite: int = 10,
) -> pd.DataFrame:
    """
    Obtiene los productos más vendidos
    durante el período reciente.
    """

    return (
        dataset_maestro.groupby(
            [
                "codigo_producto",
                "producto",
            ],
            as_index=False,
            dropna=False,
        )
        .agg(
            unidades_vendidas=(
                "ventas_recientes",
                "sum",
            ),
            stock_disponible=(
                "stock_disponible",
                "sum",
            ),
        )
        .sort_values(
            by="unidades_vendidas",
            ascending=False,
        )
        .head(limite)
    )


def obtener_productos_sin_movimiento(
    dataset_maestro: pd.DataFrame,
    limite: int = 10,
) -> pd.DataFrame:
    """
    Obtiene productos que tienen stock disponible
    pero no registraron ventas recientes.
    """

    return (
        dataset_maestro[
            (dataset_maestro["stock_disponible"] > 0)
            & (dataset_maestro["ventas_recientes"] <= 0)
        ]
        .groupby(
            [
                "codigo_producto",
                "producto",
            ],
            as_index=False,
            dropna=False,
        )
        .agg(
            stock_disponible=(
                "stock_disponible",
                "sum",
            ),
            ventas_historicas=(
                "ventas_historicas",
                "max",
            ),
            promedio_ventas_mensual=(
                "promedio_ventas_mensual",
                "max",
            ),
        )
        .sort_values(
            by="stock_disponible",
            ascending=False,
        )
        .head(limite)
    )