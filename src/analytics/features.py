"""Calculo de variables comerciales derivadas para analisis y Machine Learning."""

import numpy as np
import pandas as pd


COLUMNAS_REQUERIDAS_FEATURES = {
    "codigo_producto",
    "producto",
    "marca",
    "rubro",
    "subrubro",
    "deposito",
    "stock_disponible",
    "ventas_recientes",
    "operaciones_recientes",
    "promedio_ventas_mensual",
    "ventas_historicas",
}


def validar_columnas_features(
    dataset_maestro: pd.DataFrame,
) -> None:
    """
    Verifica que el dataset maestro contenga las columnas
    necesarias para generar las variables del modelo.
    """

    columnas_faltantes = COLUMNAS_REQUERIDAS_FEATURES.difference(
        dataset_maestro.columns
    )

    if columnas_faltantes:
        raise ValueError(
            "Faltan columnas para generar las variables: "
            + ", ".join(sorted(columnas_faltantes))
        )


def calcular_rotacion_reciente(
    ventas_recientes: pd.Series,
    stock_disponible: pd.Series,
) -> pd.Series:
    """
    Calcula la relación entre ventas recientes y stock actual.

    Un valor alto indica que las ventas son elevadas
    respecto del stock disponible.
    """

    denominador = stock_disponible.replace(0, np.nan)

    rotacion = ventas_recientes / denominador

    return rotacion.fillna(0)


def calcular_cobertura_stock(
    stock_disponible: pd.Series,
    promedio_ventas_mensual: pd.Series,
) -> pd.Series:
    """
    Estima cuántos meses de ventas promedio puede cubrir
    el stock actual.
    """

    denominador = promedio_ventas_mensual.replace(0, np.nan)

    cobertura = stock_disponible / denominador

    return cobertura.replace(
        [np.inf, -np.inf],
        np.nan,
    ).fillna(0)


def calcular_indice_demanda(
    ventas_recientes: pd.Series,
    promedio_ventas_mensual: pd.Series,
) -> pd.Series:
    """
    Compara las ventas recientes con el promedio mensual histórico.

    Valores superiores a 1 indican ventas recientes
    mayores al promedio histórico mensual.
    """

    denominador = promedio_ventas_mensual.replace(0, np.nan)

    indice = ventas_recientes / denominador

    return indice.replace(
        [np.inf, -np.inf],
        np.nan,
    ).fillna(0)


def construir_features(
    dataset_maestro: pd.DataFrame,
) -> pd.DataFrame:
    """
    Genera las variables derivadas que serán utilizadas
    por el modelo de Machine Learning.
    """

    validar_columnas_features(dataset_maestro)

    dataset_features = dataset_maestro.copy()

    dataset_features["tiene_stock"] = (
        dataset_features["stock_disponible"] > 0
    ).astype(int)

    dataset_features["tiene_ventas_recientes"] = (
        dataset_features["ventas_recientes"] > 0
    ).astype(int)

    dataset_features["rotacion_reciente"] = (
        calcular_rotacion_reciente(
            dataset_features["ventas_recientes"],
            dataset_features["stock_disponible"],
        )
    )

    dataset_features["cobertura_stock_meses"] = (
        calcular_cobertura_stock(
            dataset_features["stock_disponible"],
            dataset_features["promedio_ventas_mensual"],
        )
    )

    dataset_features["indice_demanda"] = (
        calcular_indice_demanda(
            dataset_features["ventas_recientes"],
            dataset_features["promedio_ventas_mensual"],
        )
    )

    dataset_features["frecuencia_operaciones"] = (
        dataset_features["operaciones_recientes"]
        / dataset_features["ventas_recientes"].replace(0, np.nan)
    ).fillna(0)

    columnas_features = [
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
        "tiene_stock",
        "tiene_ventas_recientes",
        "rotacion_reciente",
        "cobertura_stock_meses",
        "indice_demanda",
        "frecuencia_operaciones",
    ]

    dataset_features = dataset_features[
        columnas_features
    ].copy()

    return dataset_features
