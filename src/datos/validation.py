import pandas as pd


def medir_cruce_codigos(
    ventas_dataframe: pd.DataFrame,
    stock_dataframe: pd.DataFrame,
    ) -> dict[str, int | float]:
    """
    Mide la coincidencia de códigos de producto
    entre ventas y stock.
    """

    codigos_ventas = set(
        ventas_dataframe["codigo_producto"]
        .dropna()
        .unique()
    )

    codigos_stock = set(
        stock_dataframe["codigo_producto"]
        .dropna()
        .unique()
    )

    codigos_coincidentes = codigos_ventas.intersection(
        codigos_stock
    )

    codigos_sin_stock = codigos_ventas.difference(
        codigos_stock
    )

    porcentaje_coincidencia = (
        len(codigos_coincidentes) / len(codigos_ventas) * 100
        if codigos_ventas
        else 0
    )

    return {
        "codigos_ventas": len(codigos_ventas),
        "codigos_stock": len(codigos_stock),
        "codigos_coincidentes": len(codigos_coincidentes),
        "codigos_sin_stock": len(codigos_sin_stock),
        "porcentaje_coincidencia": porcentaje_coincidencia,
    }


def medir_cruce_producto_deposito(
    ventas_dataframe: pd.DataFrame,
    stock_dataframe: pd.DataFrame,
) -> dict[str, int | float]:
    """
    Mide la coincidencia entre ventas y stock usando
    codigo_producto + deposito.
    """

    ventas_validas = ventas_dataframe.dropna(
        subset=["codigo_producto", "deposito"]
    ).copy()

    stock_valido = stock_dataframe.dropna(
        subset=["codigo_producto", "deposito"]
    ).copy()

    claves_ventas = set(
        zip(
            ventas_validas["codigo_producto"],
            ventas_validas["deposito"],
        )
    )

    claves_stock = set(
        zip(
            stock_valido["codigo_producto"],
            stock_valido["deposito"],
        )
    )

    claves_coincidentes = claves_ventas.intersection(
        claves_stock
    )

    claves_sin_stock = claves_ventas.difference(
        claves_stock
    )

    porcentaje_coincidencia = (
        len(claves_coincidentes) / len(claves_ventas) * 100
        if claves_ventas
        else 0
    )

    return {
        "combinaciones_ventas": len(claves_ventas),
        "combinaciones_stock": len(claves_stock),
        "combinaciones_coincidentes": len(claves_coincidentes),
        "combinaciones_sin_stock": len(claves_sin_stock),
        "porcentaje_coincidencia": porcentaje_coincidencia,
    }