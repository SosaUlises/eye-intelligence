import re

import pandas as pd


def extraer_periodo_desde_nombre(
    nombre_archivo: str,
) -> tuple[int, int]:
    """
    Extrae el año y el mes desde un nombre de archivo.

    Formato esperado:
    ventas_2026_07.xls
    ventas_2026_07.xlsx
    """

    patron = r"(\d{4})[_-](\d{2})"

    coincidencia = re.search(
        patron,
        nombre_archivo,
    )

    if coincidencia is None:
        raise ValueError(
            f"No se pudo obtener el período del archivo "
            f"'{nombre_archivo}'. "
            f"Usá el formato ventas_AAAA_MM.xls."
        )

    anio = int(coincidencia.group(1))
    mes = int(coincidencia.group(2))

    if mes < 1 or mes > 12:
        raise ValueError(
            f"El mes detectado en '{nombre_archivo}' "
            f"no es válido: {mes}."
        )

    return anio, mes


def consolidar_ventas_mensuales(
    reportes_mensuales: list[tuple[str, pd.DataFrame]],
) -> pd.DataFrame:
    """
    Consolida múltiples reportes mensuales de ventas
    en un único DataFrame.

    Cada tupla contiene:
    - nombre del archivo
    - DataFrame previamente procesado
    """

    if not reportes_mensuales:
        raise ValueError(
            "No se recibieron reportes mensuales para consolidar."
        )

    dataframes_con_periodo = []

    periodos_detectados = set()

    for nombre_archivo, dataframe in reportes_mensuales:
        anio, mes = extraer_periodo_desde_nombre(
            nombre_archivo
        )

        periodo = f"{anio}-{mes:02d}"

        if periodo in periodos_detectados:
            raise ValueError(
                f"Se detectaron dos archivos para el período "
                f"{periodo}."
            )

        periodos_detectados.add(periodo)

        dataframe_con_periodo = dataframe.copy()

        dataframe_con_periodo["Año"] = anio
        dataframe_con_periodo["Mes"] = mes
        dataframe_con_periodo["Periodo"] = periodo
        dataframe_con_periodo["Archivo Origen"] = nombre_archivo

        dataframes_con_periodo.append(
            dataframe_con_periodo
        )

    ventas_mensuales_consolidadas = pd.concat(
        dataframes_con_periodo,
        ignore_index=True,
    )

    ventas_mensuales_consolidadas = (
        ventas_mensuales_consolidadas.sort_values(
            by=["Año", "Mes", "codigo_producto"]
        )
        .reset_index(drop=True)
    )

    return ventas_mensuales_consolidadas