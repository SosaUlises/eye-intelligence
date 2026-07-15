import pandas as pd


def limpiar_columnas(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe_limpio = dataframe.copy()

    dataframe_limpio.columns = [
        str(columna).strip()
        for columna in dataframe_limpio.columns
    ]

    return dataframe_limpio


def detectar_fila_encabezado(
    dataframe: pd.DataFrame,
    columnas_requeridas: set[str],
    max_filas_busqueda: int = 10,
) -> int:
    for indice in range(min(max_filas_busqueda, len(dataframe))):
        valores_fila = {
            str(valor).strip()
            for valor in dataframe.iloc[indice].tolist()
            if pd.notna(valor)
        }

        if columnas_requeridas.issubset(valores_fila):
            return indice

    raise ValueError(
        "No se pudo detectar la fila de encabezado del archivo."
    )


def normalizar_excel_dux(
    dataframe: pd.DataFrame,
    columnas_requeridas: set[str],
) -> pd.DataFrame:
    fila_encabezado = detectar_fila_encabezado(
        dataframe,
        columnas_requeridas,
    )

    nuevas_columnas = dataframe.iloc[fila_encabezado].tolist()

    dataframe_limpio = dataframe.iloc[fila_encabezado + 1:].copy()
    dataframe_limpio.columns = nuevas_columnas
    dataframe_limpio = limpiar_columnas(dataframe_limpio)
    dataframe_limpio = dataframe_limpio.dropna(how="all")
    dataframe_limpio = dataframe_limpio.reset_index(drop=True)

    return dataframe_limpio