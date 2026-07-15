"""Entrenamiento e interpretacion del modelo K-Means."""

import pandas as pd

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


COLUMNAS_MODELO = [
    "stock_disponible",
    "ventas_recientes_mensualizadas",
    "promedio_ventas_mensual",
    "meses_con_ventas",
    "indice_demanda",
    "cobertura_stock_meses",
    "rotacion_reciente",
]


def entrenar_modelo_segmentacion(
    dataset_ml: pd.DataFrame,
    cantidad_clusters: int = 4,
) -> tuple[
    KMeans,
    StandardScaler,
    pd.DataFrame,
    float,
]:
    """
    Entrena un modelo K-Means para agrupar productos
    según su comportamiento comercial.
    """

    columnas_faltantes = [
        columna
        for columna in COLUMNAS_MODELO
        if columna not in dataset_ml.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            "Faltan columnas para entrenar el modelo: "
            + ", ".join(columnas_faltantes)
        )

    if len(dataset_ml) < cantidad_clusters:
        raise ValueError(
            "No hay suficientes registros para generar "
            f"{cantidad_clusters} grupos."
        )

    matriz_variables = dataset_ml[
        COLUMNAS_MODELO
    ].copy()

    escalador = StandardScaler()

    matriz_escalada = escalador.fit_transform(
        matriz_variables
    )

    modelo = KMeans(
        n_clusters=cantidad_clusters,
        random_state=42,
        n_init=10,
    )

    grupos = modelo.fit_predict(
        matriz_escalada
    )

    dataset_segmentado = dataset_ml.copy()
    dataset_segmentado["cluster"] = grupos

    puntaje_silueta = silhouette_score(
        matriz_escalada,
        grupos,
    )

    return (
        modelo,
        escalador,
        dataset_segmentado,
        puntaje_silueta,
    )


def obtener_resumen_clusters(
    dataset_segmentado: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calcula los valores promedio de cada grupo.
    """

    resumen = (
        dataset_segmentado.groupby(
            "cluster",
            as_index=False,
        )
        .agg(
            productos=("codigo_producto", "count"),
            stock_promedio=("stock_disponible", "mean"),
            ventas_recientes_promedio=(
                "ventas_recientes_mensualizadas",
                "mean",
            ),
            promedio_historico=(
                "promedio_ventas_mensual",
                "mean",
            ),
            indice_demanda_promedio=(
                "indice_demanda",
                "mean",
            ),
            cobertura_promedio=(
                "cobertura_stock_meses",
                "mean",
            ),
            rotacion_promedio=(
                "rotacion_reciente",
                "mean",
            ),
        )
    )

    return resumen


def asignar_nombre_clusters(
    resumen_clusters: pd.DataFrame,
) -> dict[int, str]:
    """
    Asigna una descripción comercial a cada cluster
    según sus características promedio.

    El modelo crea los grupos.
    Esta función solamente los interpreta.
    """

    nombres_clusters: dict[int, str] = {}

    cluster_mayor_rotacion = (
        resumen_clusters["rotacion_promedio"].idxmax()
    )

    cluster_mayor_cobertura = (
        resumen_clusters["cobertura_promedio"].idxmax()
    )

    cluster_menores_ventas = (
        resumen_clusters[
            "ventas_recientes_promedio"
        ].idxmin()
    )

    for indice, fila in resumen_clusters.iterrows():
        cluster = int(fila["cluster"])

        if indice == cluster_mayor_rotacion:
            nombre = "Alta rotación"

        elif indice == cluster_mayor_cobertura:
            nombre = "Cobertura elevada"

        elif indice == cluster_menores_ventas:
            nombre = "Stock sin movimiento"

        else:
            nombre = "Rotación moderada"

        nombres_clusters[cluster] = nombre

    return nombres_clusters


def incorporar_perfiles_comerciales(
    dataset_segmentado: pd.DataFrame,
    nombres_clusters: dict[int, str],
) -> pd.DataFrame:
    """
    Agrega al dataset el nombre comercial
    correspondiente a cada cluster.
    """

    resultado = dataset_segmentado.copy()

    resultado["perfil_comercial"] = (
        resultado["cluster"].map(
            nombres_clusters
        )
    )

    return resultado


def obtener_productos_representativos(
    resultados_ml: pd.DataFrame,
    limite_por_grupo: int = 5,
) -> pd.DataFrame:
    """
    Devuelve los productos más representativos
    de cada perfil comercial.
    """

    columnas_requeridas = {
        "perfil_comercial",
        "codigo_producto",
        "producto",
        "deposito",
        "stock_disponible",
        "ventas_recientes_mensualizadas",
        "promedio_ventas_mensual",
        "cobertura_stock_meses",
        "rotacion_reciente",
    }

    columnas_faltantes = columnas_requeridas.difference(
        resultados_ml.columns
    )

    if columnas_faltantes:
        raise ValueError(
            "Faltan columnas para obtener productos representativos: "
            + ", ".join(sorted(columnas_faltantes))
        )

    grupos = []

    for perfil, grupo in resultados_ml.groupby(
        "perfil_comercial"
    ):
        if perfil == "Alta rotación":
            grupo_ordenado = grupo.sort_values(
                by="rotacion_reciente",
                ascending=False,
            )

        elif perfil == "Cobertura elevada":
            grupo_ordenado = grupo.sort_values(
                by="cobertura_stock_meses",
                ascending=False,
            )

        elif perfil == "Stock sin movimiento":
            grupo_ordenado = grupo.sort_values(
                by=[
                    "ventas_recientes_mensualizadas",
                    "stock_disponible",
                ],
                ascending=[
                    True,
                    False,
                ],
            )

        else:
            grupo_ordenado = grupo.sort_values(
                by="stock_disponible",
                ascending=False,
            )

        grupos.append(
            grupo_ordenado.head(limite_por_grupo)
        )

    return pd.concat(
        grupos,
        ignore_index=True,
    )
