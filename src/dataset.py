import pandas as pd


def agregar_ventas_historicas(
    ventas_mensuales: pd.DataFrame,
) -> pd.DataFrame:
    """
    Resume las ventas mensuales por código de producto.

    La información histórica no distingue sucursal,
    por lo que se agrega únicamente por codigo_producto.
    """

    columnas_requeridas = {
        "codigo_producto",
        "producto",
        "marca",
        "rubro",
        "subrubro",
        "cantidad_vendida",
        "monto_vendido",
        "Periodo",
    }

    columnas_faltantes = columnas_requeridas.difference(
        ventas_mensuales.columns
    )

    if columnas_faltantes:
        raise ValueError(
            "Faltan columnas en ventas mensuales: "
            + ", ".join(sorted(columnas_faltantes))
        )

    cantidad_periodos = ventas_mensuales["Periodo"].nunique()

    if cantidad_periodos == 0:
        raise ValueError(
            "No se encontraron períodos válidos en las ventas mensuales."
        )

    ventas_historicas = (
        ventas_mensuales.groupby(
            "codigo_producto",
            as_index=False,
        )
        .agg(
            producto=("producto", "first"),
            marca=("marca", "first"),
            rubro=("rubro", "first"),
            subrubro=("subrubro", "first"),
            ventas_historicas=("cantidad_vendida", "sum"),
            monto_historico=("monto_vendido", "sum"),
            meses_con_ventas=("Periodo", "nunique"),
        )
    )

    ventas_historicas["promedio_ventas_mensual"] = (
        ventas_historicas["ventas_historicas"]
        / cantidad_periodos
    )

    ventas_historicas["periodos_analizados"] = cantidad_periodos

    return ventas_historicas


def agregar_ventas_recientes(
    ventas_detalladas: pd.DataFrame,
) -> pd.DataFrame:
    """
    Resume las ventas recientes por producto y depósito.
    Conserva también los datos descriptivos disponibles.
    """

    columnas_requeridas = {
        "codigo_producto",
        "deposito",
        "sucursal",
        "producto",
        "marca",
        "rubro",
        "subrubro",
        "cantidad",
        "total_con_iva",
        "fecha_venta",
    }

    columnas_faltantes = columnas_requeridas.difference(
        ventas_detalladas.columns
    )

    if columnas_faltantes:
        raise ValueError(
            "Faltan columnas en ventas detalladas: "
            + ", ".join(sorted(columnas_faltantes))
        )

    ventas_validas = ventas_detalladas.dropna(
        subset=["codigo_producto", "deposito"]
    ).copy()

    ventas_recientes = (
        ventas_validas.groupby(
            ["codigo_producto", "deposito"],
            as_index=False,
        )
        .agg(
            sucursal=("sucursal", "first"),
            producto_reciente=("producto", "first"),
            marca_reciente=("marca", "first"),
            rubro_reciente=("rubro", "first"),
            subrubro_reciente=("subrubro", "first"),
            ventas_recientes=("cantidad", "sum"),
            operaciones_recientes=("fecha_venta", "count"),
            monto_reciente=("total_con_iva", "sum"),
            primera_venta=("fecha_venta", "min"),
            ultima_venta=("fecha_venta", "max"),
        )
    )

    return ventas_recientes


def agregar_stock_actual(
    stock_actual: pd.DataFrame,
) -> pd.DataFrame:
    """
    Resume el stock por producto y depósito.
    Conserva los datos descriptivos del catálogo.
    """

    columnas_requeridas = {
        "codigo_producto",
        "producto",
        "deposito",
        "rubro",
        "subrubro",
        "stock_real",
        "stock_disponible",
    }

    columnas_faltantes = columnas_requeridas.difference(
        stock_actual.columns
    )

    if columnas_faltantes:
        raise ValueError(
            "Faltan columnas en stock actual: "
            + ", ".join(sorted(columnas_faltantes))
        )

    stock_resumido = (
        stock_actual.groupby(
            ["codigo_producto", "deposito"],
            as_index=False,
        )
        .agg(
            producto_stock=("producto", "first"),
            rubro_stock=("rubro", "first"),
            subrubro_stock=("subrubro", "first"),
            stock_real=("stock_real", "sum"),
            stock_disponible=("stock_disponible", "sum"),
        )
    )

    return stock_resumido


def construir_dataset_maestro(
    ventas_mensuales: pd.DataFrame,
    ventas_detalladas: pd.DataFrame,
    stock_actual: pd.DataFrame,
) -> pd.DataFrame:
    """
    Integra ventas históricas, ventas recientes
    y stock actual en un único DataFrame.
    """

    historico = agregar_ventas_historicas(
        ventas_mensuales
    )

    recientes = agregar_ventas_recientes(
        ventas_detalladas
    )

    stock = agregar_stock_actual(
        stock_actual
    )

    dataset_maestro = stock.merge(
        recientes,
        on=["codigo_producto", "deposito"],
        how="left",
    )

    dataset_maestro = dataset_maestro.merge(
        historico,
        on="codigo_producto",
        how="left",
    )

    dataset_maestro["producto"] = (
        dataset_maestro["producto"]
        .combine_first(
            dataset_maestro["producto_reciente"]
        )
        .combine_first(
            dataset_maestro["producto_stock"]
        )
    )

    dataset_maestro["marca"] = (
        dataset_maestro["marca"]
        .combine_first(
            dataset_maestro["marca_reciente"]
        )
    )

    dataset_maestro["rubro"] = (
        dataset_maestro["rubro"]
        .combine_first(
            dataset_maestro["rubro_reciente"]
        )
        .combine_first(
            dataset_maestro["rubro_stock"]
        )
    )

    dataset_maestro["subrubro"] = (
        dataset_maestro["subrubro"]
        .combine_first(
            dataset_maestro["subrubro_reciente"]
        )
        .combine_first(
            dataset_maestro["subrubro_stock"]
        )
    )

    columnas_numericas = [
        "ventas_recientes",
        "operaciones_recientes",
        "monto_reciente",
        "ventas_historicas",
        "monto_historico",
        "meses_con_ventas",
        "promedio_ventas_mensual",
        "periodos_analizados",
    ]

    for columna in columnas_numericas:
        dataset_maestro[columna] = (
            dataset_maestro[columna].fillna(0)
        )

    columnas_auxiliares = [
        "producto_reciente",
        "producto_stock",
        "marca_reciente",
        "rubro_reciente",
        "rubro_stock",
        "subrubro_reciente",
        "subrubro_stock",
    ]

    dataset_maestro = dataset_maestro.drop(
        columns=columnas_auxiliares,
    )

    columnas_no_utilizadas = [
        "proveedor",
        "stock_reservado",
        "valorizacion_stock",
    ]

    columnas_no_utilizadas_existentes = [
        columna
        for columna in columnas_no_utilizadas
        if columna in dataset_maestro.columns
    ]

    dataset_maestro = dataset_maestro.drop(
        columns=columnas_no_utilizadas_existentes,
    )

    columnas_finales = [
        "codigo_producto",
        "producto",
        "marca",
        "rubro",
        "subrubro",
        "deposito",
        "sucursal",
        "stock_real",
        "stock_disponible",
        "ventas_recientes",
        "operaciones_recientes",
        "monto_reciente",
        "ventas_historicas",
        "monto_historico",
        "promedio_ventas_mensual",
        "meses_con_ventas",
        "periodos_analizados",
        "primera_venta",
        "ultima_venta",
    ]

    columnas_finales_existentes = [
        columna
        for columna in columnas_finales
        if columna in dataset_maestro.columns
    ]

    dataset_maestro = dataset_maestro[
        columnas_finales_existentes
    ]

    dataset_maestro = dataset_maestro.sort_values(
        by=[
            "stock_disponible",
            "ventas_recientes",
        ],
        ascending=[False, False],
    ).reset_index(drop=True)

    return dataset_maestro