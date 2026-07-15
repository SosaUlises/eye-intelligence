import pandas as pd


def normalizar_texto(serie: pd.Series) -> pd.Series:
    """
    Convierte una serie a texto y elimina espacios innecesarios.
    Los valores nulos se mantienen como nulos.
    """

    return serie.apply(
        lambda valor: str(valor).strip()
        if pd.notna(valor)
        else pd.NA
    )


def convertir_columnas_numericas(
    dataframe: pd.DataFrame,
    columnas: list[str],
    ) -> pd.DataFrame:
    """
    Convierte las columnas indicadas a formato numérico.

    Los valores que no puedan convertirse pasan a NaN.
    """

    dataframe_convertido = dataframe.copy()

    for columna in columnas:
        if columna not in dataframe_convertido.columns:
            raise ValueError(
                f"No se encontró la columna numérica '{columna}'."
            )

        dataframe_convertido[columna] = pd.to_numeric(
            dataframe_convertido[columna],
            errors="coerce",
        )

    return dataframe_convertido


def normalizar_columnas_texto(
    dataframe: pd.DataFrame,
    columnas: list[str],
    ) -> pd.DataFrame:
    """
    Normaliza columnas textuales eliminando espacios
    y conservando valores nulos.
    """

    dataframe_normalizado = dataframe.copy()

    for columna in columnas:
        if columna not in dataframe_normalizado.columns:
            raise ValueError(
                f"No se encontró la columna textual '{columna}'."
            )

        dataframe_normalizado[columna] = normalizar_texto(
            dataframe_normalizado[columna]
        )

    return dataframe_normalizado


def renombrar_columnas(
    dataframe: pd.DataFrame,
    mapeo_columnas: dict[str, str],
    ) -> pd.DataFrame:
    """
    Renombra columnas según el diccionario recibido.
    """

    columnas_faltantes = [
        columna
        for columna in mapeo_columnas
        if columna not in dataframe.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            "No se encontraron las siguientes columnas: "
            + ", ".join(columnas_faltantes)
        )

    return dataframe.rename(
        columns=mapeo_columnas
    ).copy()


def normalizar_codigo_producto(
    serie: pd.Series,
    ) -> pd.Series:
    """
    Normaliza códigos de producto como texto.

    Elimina espacios y evita valores como '123.0'
    cuando el código proviene de Excel como número.
    """

    def transformar_codigo(valor):
        if pd.isna(valor):
            return pd.NA

        if isinstance(valor, float) and valor.is_integer():
            return str(int(valor))

        return str(valor).strip()

    return serie.apply(transformar_codigo)