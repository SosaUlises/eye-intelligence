import pandas as pd


def calcular_kpis(
    dataset_maestro: pd.DataFrame,
) -> dict[str, int | float]:
    """
    Calcula los indicadores principales del negocio
    a partir del dataset maestro.
    """

    columnas_requeridas = {
        "codigo_producto",
        "deposito",
        "stock_disponible",
        "ventas_recientes",
        "monto_reciente",
        "ventas_historicas",
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

    productos_con_ventas = dataset_maestro.loc[
        dataset_maestro["ventas_recientes"] > 0,
        "codigo_producto",
    ].nunique()

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
        "unidades_vendidas_historicas": dataset_maestro[
            "ventas_historicas"
        ].sum(),
        "productos_con_ventas": productos_con_ventas,
        "productos_sin_ventas": productos_sin_ventas,
    }


def obtener_ventas_por_rubro(
    dataset_maestro: pd.DataFrame,
) -> pd.DataFrame:
    """
    Agrupa las ventas recientes por rubro.
    """

    ventas_por_rubro = (
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
            monto_vendido=(
                "monto_reciente",
                "sum",
            ),
        )
        .sort_values(
            by="unidades_vendidas",
            ascending=False,
        )
    )

    return ventas_por_rubro


def obtener_top_productos(
    dataset_maestro: pd.DataFrame,
    limite: int = 10,
) -> pd.DataFrame:
    """
    Devuelve los productos con más unidades vendidas
    en el período reciente.
    """

    top_productos = (
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
            monto_vendido=(
                "monto_reciente",
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

    return top_productos