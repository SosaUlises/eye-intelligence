import pandas as pd

from src.cleaning import normalizar_excel_dux
from src.mappings import obtener_deposito_desde_sucursal
from src.transformations import (
    convertir_columnas_numericas,
    normalizar_codigo_producto,
    normalizar_columnas_texto,
    renombrar_columnas,
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

    dataframe_procesado = renombrar_columnas(
        dataframe_procesado,
        {
            "Código": "codigo_producto",
            "Producto": "producto",
            "Marca": "marca",
            "Rubro": "rubro",
            "Sub Rubro": "subrubro",
            "Cantidad de Ventas": "cantidad_ventas",
            "Cantidad Total Vendida": "cantidad_vendida",
            "Monto Vendido": "monto_vendido",
            "Monto Vendido Sin Iva": "monto_sin_iva",
            "Costo Total": "costo_total",
            "Margen": "margen",
            "Ganancia": "ganancia",
        },
    )

    dataframe_procesado["codigo_producto"] = (
        normalizar_codigo_producto(
            dataframe_procesado["codigo_producto"]
        )
    )

    dataframe_procesado = dataframe_procesado.reset_index(
        drop=True
    )


    return dataframe_procesado


def procesar_ventas_detalladas(
    dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
    dataframe_procesado = normalizar_excel_dux(
        dataframe,
        COLUMNAS_REQUERIDAS_VENTAS_DETALLADAS,
    )

    columnas_texto = [
        "Sucursal",
        "Código Producto",
        "Producto",
        "Rubro",
        "Sub Rubro",
        "Marca",
        "Proveedor",
        "Vendedor",
        "Forma Pago",
    ]

    columnas_numericas = [
        "Cantidad",
        "Precio Uni",
        "% Desc.",
        "Total Sin IVA",
        "IVA",
        "Total Con Iva",
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

    dataframe_procesado["Fecha Comp"] = pd.to_datetime(
        dataframe_procesado["Fecha Comp"],
        errors="coerce",
        dayfirst=True,
    )

    dataframe_procesado = dataframe_procesado.dropna(
        subset=[
            "Código Producto",
            "Producto",
            "Fecha Comp",
        ]
    )

    dataframe_procesado = renombrar_columnas(
        dataframe_procesado,
        {
            "Sucursal": "sucursal",
            "Código Producto": "codigo_producto",
            "Producto": "producto",
            "Rubro": "rubro",
            "Sub Rubro": "subrubro",
            "Marca": "marca",
            "Proveedor": "proveedor",
            "Vendedor": "vendedor",
            "Forma Pago": "forma_pago",
            "Fecha Comp": "fecha_venta",
            "Cantidad": "cantidad",
            "Precio Uni": "precio_unitario",
            "% Desc.": "porcentaje_descuento",
            "Total Sin IVA": "total_sin_iva",
            "IVA": "iva",
            "Total Con Iva": "total_con_iva",
            "Ganancia": "ganancia",
        },
    )

    dataframe_procesado["codigo_producto"] = (
        normalizar_codigo_producto(
            dataframe_procesado["codigo_producto"]
        )
    )

    dataframe_procesado["deposito"] = (
        dataframe_procesado["sucursal"].apply(
            obtener_deposito_desde_sucursal
        )
    )

    dataframe_procesado = dataframe_procesado.reset_index(
        drop=True
    )

    return dataframe_procesado



def procesar_stock_actual(
    dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
    dataframe_procesado = normalizar_excel_dux(
        dataframe,
        COLUMNAS_REQUERIDAS_STOCK_ACTUAL,
    )

    columnas_texto = [
        "Cod Producto",
        "Producto",
        "Depósito",
        "Rubro",
        "Sub Rubro",
        "Unidad",
        "Proveedor",
    ]

    columnas_numericas = [
        "Stock Real",
        "Stock Reservado",
        "Stock Disponible",
        "Valorización Unitaria",
        "Valorización",
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
        subset=[
            "Cod Producto",
            "Producto",
            "Depósito",
        ]
    )

    dataframe_procesado = renombrar_columnas(
        dataframe_procesado,
        {
            "Cod Producto": "codigo_producto",
            "Producto": "producto",
            "Depósito": "deposito",
            "Rubro": "rubro",
            "Sub Rubro": "subrubro",
            "Stock Real": "stock_real",
            "Stock Reservado": "stock_reservado",
            "Stock Disponible": "stock_disponible",
            "Unidad": "unidad",
            "Proveedor": "proveedor",
            "Valorización Unitaria": "valorizacion_unitaria",
            "Valorización": "valorizacion_total",
        },
    )

    dataframe_procesado["codigo_producto"] = (
        normalizar_codigo_producto(
            dataframe_procesado["codigo_producto"]
        )
    )

    dataframe_procesado = dataframe_procesado.reset_index(
        drop=True
    )

    return dataframe_procesado