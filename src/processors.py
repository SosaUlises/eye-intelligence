import pandas as pd

from src.cleaning import normalizar_excel_dux


COLUMNAS_REQUERIDAS_VENTAS_MENSUALES = {
    "Código",
    "Producto",
    "Cantidad Total Vendida",
    "Monto Vendido",
}

COLUMNAS_REQUERIDAS_VENTAS_DETALLADAS = {
    "Sucursal",
    "Fecha Comp",
    "Código Producto",
    "Producto",
}

COLUMNAS_REQUERIDAS_STOCK_ACTUAL = {
    "Cod Producto",
    "Producto",
    "Depósito",
    "Stock Disponible",
}


def procesar_ventas_mensuales(dataframe: pd.DataFrame) -> pd.DataFrame:
    return normalizar_excel_dux(
        dataframe,
        COLUMNAS_REQUERIDAS_VENTAS_MENSUALES,
    )


def procesar_ventas_detalladas(dataframe: pd.DataFrame) -> pd.DataFrame:
    return normalizar_excel_dux(
        dataframe,
        COLUMNAS_REQUERIDAS_VENTAS_DETALLADAS,
    )


def procesar_stock_actual(dataframe: pd.DataFrame) -> pd.DataFrame:
    return normalizar_excel_dux(
        dataframe,
        COLUMNAS_REQUERIDAS_STOCK_ACTUAL,
    )