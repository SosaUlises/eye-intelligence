from typing import BinaryIO

import pandas as pd


def read_excel_file(file: BinaryIO) -> pd.DataFrame:
    """
    Lee un archivo Excel subido desde Streamlit y devuelve un DataFrame.
    Soporta archivos .xls y .xlsx.
    """
    try:
        return pd.read_excel(file)
    except Exception as error:
        raise ValueError(f"No se pudo leer el archivo Excel: {error}") from error


def read_multiple_excel_files(files: list[BinaryIO]) -> list[pd.DataFrame]:
    """
    Lee varios archivos Excel y devuelve una lista de DataFrames.
    """
    dataframes = []

    for file in files:
        dataframe = read_excel_file(file)
        dataframes.append(dataframe)

    return dataframes