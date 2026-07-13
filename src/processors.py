import pandas as pd

from src.cleaning import normalizar_excel_dux
from src.transformations import (
    convertir_columnas_numericas,
    normalizar_columnas_texto,
)


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


def procesar_ventas_mensuales(
    dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
    dataframe_procesado = normalizar_excel_dux(
        dataframe,
        COLUMNAS_REQUERIDAS_VENTAS_MENSUALES,
    )

    columnas_texto = [
        "Código",
        "Producto",
        "Marca",
        "Rubro",
        "Sub Rubro",
    ]

    columnas_numericas = [
        "Cantidad de Ventas",
        "Cantidad Total Vendida",
        "Monto Vendido",
        "Monto Vendido Sin Iva",
        "Costo Total",
        "Margen",
        "Ganancia",
    ]

    dataframe_procesado = normalizar_columnas_texto(
        dataframe_procesado,
        columnas_texto,
    )

    dataframe_procesado = convertir_columnas_numericas(
        dataframe_procesado,
        columnas_numericas,
    )

    dataframe_procesado = dataframe_procesado.dropna(
        subset=["Código", "Producto"]
    )

    dataframe_procesado = dataframe_procesado.reset_index(
        drop=True
    )

    return dataframe_procesado


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