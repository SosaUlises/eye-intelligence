"""Preparacion del dataset que usa el modelo de segmentacion comercial."""

import numpy as np
import pandas as pd


COLUMNAS_REQUERIDAS_ML = {
    "codigo_producto",
    "producto",
    "marca",
    "rubro",
    "subrubro",
    "deposito",
    "stock_disponible",
    "ventas_recientes",
    "operaciones_recientes",
    "ventas_historicas",
    "promedio_ventas_mensual",
    "meses_con_ventas",
    "primera_venta",
    "ultima_venta",
}


def validar_columnas_ml(
    dataset_maestro: pd.DataFrame,
) -> None:
    """
    Verifica que el dataset maestro tenga las columnas
    necesarias para construir el dataset de Machine Learning.
    """

    columnas_faltantes = COLUMNAS_REQUERIDAS_ML.difference(
        dataset_maestro.columns
    )

    if columnas_faltantes:
        raise ValueError(
            "Faltan columnas para construir el dataset de ML: "
            + ", ".join(sorted(columnas_faltantes))
        )


def calcular_dias_periodo_reciente(
    dataset_maestro: pd.DataFrame,
) -> int:
    """
    Calcula la cantidad real de días cubierta por
    el archivo de ventas detalladas.
    """

    fechas = pd.concat(
        [
            dataset_maestro["primera_venta"],
            dataset_maestro["ultima_venta"],
        ]
    ).dropna()

    if fechas.empty:
        raise ValueError(
            "No se encontraron fechas de ventas recientes."
        )

    fecha_desde = fechas.min()
    fecha_hasta = fechas.max()

    cantidad_dias = (fecha_hasta - fecha_desde).days + 1

    if cantidad_dias <= 0:
        raise ValueError(
            "El período de ventas recientes no es válido."
        )

    return cantidad_dias


def construir_dataset_ml(
    dataset_maestro: pd.DataFrame,
) -> pd.DataFrame:
    """
    Construye el dataset utilizado por el modelo
    no supervisado de segmentación comercial.
    """

    validar_columnas_ml(dataset_maestro)

    cantidad_dias_recientes = calcular_dias_periodo_reciente(
        dataset_maestro
    )

    dataset_ml = dataset_maestro.copy()

    columnas_numericas = [
        "stock_disponible",
        "ventas_recientes",
        "operaciones_recientes",
        "ventas_historicas",
        "promedio_ventas_mensual",
        "meses_con_ventas",
    ]

    for columna in columnas_numericas:
        dataset_ml[columna] = pd.to_numeric(
            dataset_ml[columna],
            errors="coerce",
        ).fillna(0)

    # Convierte las ventas del período reciente
    # a una tasa comparable de aproximadamente 30 días.
    dataset_ml["ventas_recientes_mensualizadas"] = (
        dataset_ml["ventas_recientes"]
        * 30
        / cantidad_dias_recientes
    )

    promedio_historico_seguro = (
        dataset_ml["promedio_ventas_mensual"]
        .replace(0, np.nan)
    )

    stock_seguro = (
        dataset_ml["stock_disponible"]
        .replace(0, np.nan)
    )

    dataset_ml["indice_demanda"] = (
        dataset_ml["ventas_recientes_mensualizadas"]
        / promedio_historico_seguro
    )

    dataset_ml["cobertura_stock_meses"] = (
        dataset_ml["stock_disponible"]
        / promedio_historico_seguro
    )

    dataset_ml["rotacion_reciente"] = (
        dataset_ml["ventas_recientes_mensualizadas"]
        / stock_seguro
    )

    dataset_ml["frecuencia_operaciones"] = (
        dataset_ml["operaciones_recientes"]
        / dataset_ml["ventas_recientes"].replace(0, np.nan)
    )

    columnas_derivadas = [
        "indice_demanda",
        "cobertura_stock_meses",
        "rotacion_reciente",
        "frecuencia_operaciones",
    ]

    dataset_ml[columnas_derivadas] = (
        dataset_ml[columnas_derivadas]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    # Limitamos valores extremos para evitar que pocos productos
    # distorsionen por completo los grupos de K-Means.
    columnas_a_limitar = [
        "stock_disponible",
        "ventas_recientes_mensualizadas",
        "promedio_ventas_mensual",
        "indice_demanda",
        "cobertura_stock_meses",
        "rotacion_reciente",
    ]

    for columna in columnas_a_limitar:
        limite_superior = dataset_ml[columna].quantile(0.99)

        if limite_superior > 0:
            dataset_ml[columna] = dataset_ml[columna].clip(
                upper=limite_superior
            )

    # Solo analizamos productos que tienen stock actual.
    dataset_ml = dataset_ml[
        dataset_ml["stock_disponible"] > 0
    ].copy()

    columnas_finales = [
        "codigo_producto",
        "producto",
        "marca",
        "rubro",
        "subrubro",
        "deposito",
        "stock_disponible",
        "ventas_recientes",
        "ventas_recientes_mensualizadas",
        "operaciones_recientes",
        "ventas_historicas",
        "promedio_ventas_mensual",
        "meses_con_ventas",
        "indice_demanda",
        "cobertura_stock_meses",
        "rotacion_reciente",
        "frecuencia_operaciones",
    ]

    return dataset_ml[
        columnas_finales
    ].reset_index(drop=True)
