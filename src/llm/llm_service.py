"""Asistente comercial: interpreta preguntas, filtra con Pandas y consulta al LLM."""

import os
import re
import unicodedata

import pandas as pd
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import streamlit as st

load_dotenv()


MAPEO_DEPOSITOS = {
    "san lorenzo kids": "DEPOSITO SAN LORENZO KIDS",
    "san lorenzo": "DEPOSITO SAN LORENZO",
    "bermudez outlet": "DEPOSITO BERMUDEZ OUTLET",
    "bermúdez outlet": "DEPOSITO BERMUDEZ OUTLET",
    "bermudez": "DEPOSITO BERMUDEZ OUTLET",
    "bermúdez": "DEPOSITO BERMUDEZ OUTLET",
    "ricardone": "DEPOSITO RICARDONE",
    "puerto": "DEPOSITO PUERTO",
    "pagina web": "DEPOSITO PAGINA WEB",
    "página web": "DEPOSITO PAGINA WEB",
    "web": "DEPOSITO PAGINA WEB",
    "central": "DEPOSITO CENTRAL",
}


MAPEO_PERFILES = {
    "stock sin movimiento": "Stock sin movimiento",
    "sin movimiento": "Stock sin movimiento",
    "sin ventas": "Stock sin movimiento",
    "mercaderia parada": "Stock sin movimiento",
    "mercadería parada": "Stock sin movimiento",
    "productos parados": "Stock sin movimiento",
    "stock parado": "Stock sin movimiento",
    "poca venta": "Stock sin movimiento",
    "baja venta": "Stock sin movimiento",
    "inmovilizado": "Stock sin movimiento",
    "inmovilizados": "Stock sin movimiento",
    "liquidar": "Stock sin movimiento",
    "alta rotación": "Alta rotación",
    "alta rotacion": "Alta rotación",
    "se mueve mucho": "Alta rotación",
    "buen movimiento": "Alta rotación",
    "mucha venta": "Alta rotación",
    "vende bien": "Alta rotación",
    "cobertura elevada": "Cobertura elevada",
    "sobrestock": "Cobertura elevada",
    "mucho stock": "Cobertura elevada",
    "sobrante": "Cobertura elevada",
    "sobrantes": "Cobertura elevada",
    "exceso de stock": "Cobertura elevada",
    "demasiado stock": "Cobertura elevada",
    "rotación moderada": "Rotación moderada",
    "rotacion moderada": "Rotación moderada",
}


def obtener_configuracion_hugging_face() -> tuple[str, str]:
    """
    Obtiene la configuración de Hugging Face.

    En local utiliza variables de entorno.
    En Streamlit Cloud utiliza st.secrets.
    """

    token = os.getenv("HF_TOKEN")

    if not token:
        token = st.secrets.get("HF_TOKEN")

    modelo = os.getenv("HF_MODEL")

    if not modelo:
        modelo = st.secrets.get(
            "HF_MODEL",
            "Qwen/Qwen2.5-7B-Instruct",
        )

    if not token:
        raise ValueError(
            "No se encontró la configuración HF_TOKEN."
        )

    return token, modelo


def crear_cliente_hugging_face() -> tuple[InferenceClient, str]:
    """
    Crea el cliente de inferencia de Hugging Face.
    """

    token, modelo = obtener_configuracion_hugging_face()

    cliente = InferenceClient(
        provider="auto",
        api_key=token,
    )

    return cliente, modelo


def normalizar_texto(texto: str) -> str:
    """
    Normaliza un texto para comparar consultas
    con marcas, rubros, subrubros y depósitos.
    """

    texto_normalizado = str(texto).lower().strip()

    texto_normalizado = unicodedata.normalize(
        "NFD",
        texto_normalizado,
    )

    texto_normalizado = "".join(
        caracter
        for caracter in texto_normalizado
        if unicodedata.category(caracter) != "Mn"
    )

    texto_normalizado = re.sub(
        r"[^a-z0-9]+",
        " ",
        texto_normalizado,
    )

    texto_normalizado = re.sub(
        r"\s+",
        " ",
        texto_normalizado,
    )

    return texto_normalizado.strip()


def normalizar_texto_compacto(texto: str) -> str:
    """
    Genera una versión sin espacios para detectar valores
    que en Dux pueden aparecer unidos, por ejemplo VIAMARTE.
    """

    return normalizar_texto(texto).replace(" ", "")


def detectar_deposito(pregunta: str) -> str | None:
    """
    Detecta un depósito mencionado en la consulta.
    """

    pregunta_normalizada = normalizar_texto(pregunta)

    depositos_ordenados = sorted(
        MAPEO_DEPOSITOS.items(),
        key=lambda elemento: len(elemento[0]),
        reverse=True,
    )

    for expresion, deposito in depositos_ordenados:
        if normalizar_texto(expresion) in pregunta_normalizada:
            return deposito

    return None


def detectar_perfil(pregunta: str) -> str | None:
    """
    Detecta un perfil comercial mencionado.
    """

    pregunta_normalizada = normalizar_texto(pregunta)

    perfiles_ordenados = sorted(
        MAPEO_PERFILES.items(),
        key=lambda elemento: len(elemento[0]),
        reverse=True,
    )

    for expresion, perfil in perfiles_ordenados:
        if normalizar_texto(expresion) in pregunta_normalizada:
            return perfil

    return None


def detectar_limite_productos(
    pregunta: str,
    limite_default: int = 10,
    limite_maximo: int = 20,
) -> int:
    """
    Detecta una cantidad solicitada, por ejemplo:
    'mostrame 5 productos'.
    """

    coincidencia = re.search(
        r"\b(\d{1,2})\b",
        pregunta,
    )

    if coincidencia is None:
        return limite_default

    limite = int(coincidencia.group(1))

    if limite <= 0:
        return limite_default

    return min(limite, limite_maximo)


def detectar_criterio_orden(pregunta: str) -> str:
    """
    Detecta cómo deben ordenarse los resultados.
    """

    pregunta_normalizada = normalizar_texto(pregunta)

    criterios = {
        "revision_prioritaria": [
            "revisar primero",
            "deberia revisar",
            "debería revisar",
            "conviene revisar",
            "conviendria revisar",
            "convendría revisar",
            "priorizar",
            "prestar atencion",
            "prestar atención",
            "productos problematicos",
            "productos problemáticos",
        ],
        "mas_vendidos": [
            "mas vendidos",
            "mayores ventas",
            "que mas venden",
            "mayor venta",
            "top ventas",
        ],
        "mayor_stock": [
            "mayor stock",
            "mas stock",
            "mayor cantidad de stock",
            "stock mas alto",
        ],
        "mayor_cobertura": [
            "mayor cobertura",
            "mas cobertura",
            "cobertura mas alta",
        ],
        "mayor_rotacion": [
            "mayor rotacion",
            "mas rotacion",
            "rotacion mas alta",
        ],
        "menor_movimiento": [
            "menos movimiento",
            "menor movimiento",
            "sin movimiento",
            "sin ventas",
        ],
    }

    for criterio, expresiones in criterios.items():
        if any(
            expresion in pregunta_normalizada
            for expresion in expresiones
        ):
            return criterio

    return "relevancia_perfil"


def detectar_valor_columna(
    pregunta: str,
    resultados_ml: pd.DataFrame,
    columna: str,
) -> str | None:
    """
    Detecta dinámicamente una marca, rubro o subrubro
    presente en los resultados del modelo.
    """

    if columna not in resultados_ml.columns:
        return None

    pregunta_normalizada = normalizar_texto(pregunta)
    pregunta_compacta = normalizar_texto_compacto(pregunta)

    valores = (
        resultados_ml[columna]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    coincidencias = []

    for valor in valores:
        valor_normalizado = normalizar_texto(valor)
        valor_compacto = normalizar_texto_compacto(valor)

        if not valor_normalizado:
            continue

        coincide_normal = (
            valor_normalizado in pregunta_normalizada
        )

        coincide_compacto = (
            len(valor_compacto) >= 4
            and valor_compacto in pregunta_compacta
        )

        if coincide_normal or coincide_compacto:
            coincidencias.append(
                (
                    len(valor_compacto),
                    valor,
                )
            )

    if not coincidencias:
        return None

    coincidencias.sort(
        key=lambda elemento: elemento[0],
        reverse=True,
    )

    return coincidencias[0][1]


def detectar_marca(
    pregunta: str,
    resultados_ml: pd.DataFrame,
) -> str | None:
    return detectar_valor_columna(
        pregunta,
        resultados_ml,
        "marca",
    )


def detectar_rubro(
    pregunta: str,
    resultados_ml: pd.DataFrame,
) -> str | None:
    return detectar_valor_columna(
        pregunta,
        resultados_ml,
        "rubro",
    )


def detectar_subrubro(
    pregunta: str,
    resultados_ml: pd.DataFrame,
) -> str | None:
    return detectar_valor_columna(
        pregunta,
        resultados_ml,
        "subrubro",
    )


def filtrar_resultados_ml(
    resultados_ml: pd.DataFrame,
    perfil: str | None = None,
    deposito: str | None = None,
    marca: str | None = None,
    rubro: str | None = None,
    subrubro: str | None = None,
) -> pd.DataFrame:
    """
    Filtra los resultados completos del modelo
    según los criterios detectados en la pregunta.
    """

    if resultados_ml.empty:
        raise ValueError(
            "Los resultados del modelo están vacíos."
        )

    resultados_filtrados = resultados_ml.copy()

    if perfil:
        resultados_filtrados = resultados_filtrados[
            resultados_filtrados["perfil_comercial"] == perfil
        ]

    if deposito:
        resultados_filtrados = resultados_filtrados[
            resultados_filtrados["deposito"] == deposito
        ]

    if marca:
        resultados_filtrados = resultados_filtrados[
            resultados_filtrados["marca"]
            .fillna("")
            .astype(str)
            .apply(normalizar_texto_compacto)
            == normalizar_texto_compacto(marca)
        ]

    if rubro:
        resultados_filtrados = resultados_filtrados[
            resultados_filtrados["rubro"]
            .fillna("")
            .astype(str)
            .apply(normalizar_texto_compacto)
            == normalizar_texto_compacto(rubro)
        ]

    if subrubro:
        resultados_filtrados = resultados_filtrados[
            resultados_filtrados["subrubro"]
            .fillna("")
            .astype(str)
            .apply(normalizar_texto_compacto)
            == normalizar_texto_compacto(subrubro)
        ]

    return resultados_filtrados.copy()


def ordenar_resultados(
    resultados: pd.DataFrame,
    criterio: str,
    perfil: str | None,
) -> pd.DataFrame:
    """
    Ordena los resultados según la intención de la consulta.
    """

    if resultados.empty:
        return resultados

    if criterio == "mas_vendidos":
        return resultados.sort_values(
            by="ventas_recientes_mensualizadas",
            ascending=False,
        )

    if criterio == "mayor_stock":
        return resultados.sort_values(
            by="stock_disponible",
            ascending=False,
        )

    if criterio == "mayor_cobertura":
        return resultados.sort_values(
            by="cobertura_stock_meses",
            ascending=False,
        )

    if criterio == "mayor_rotacion":
        return resultados.sort_values(
            by="rotacion_reciente",
            ascending=False,
        )

    if criterio == "menor_movimiento":
        return resultados.sort_values(
            by=[
                "ventas_recientes_mensualizadas",
                "stock_disponible",
            ],
            ascending=[
                True,
                False,
            ],
        )

    if criterio == "revision_prioritaria":
        return resultados.sort_values(
            by=[
                "stock_disponible",
                "ventas_recientes_mensualizadas",
                "cobertura_stock_meses",
            ],
            ascending=[
                False,
                True,
                False,
            ],
        )

    if perfil == "Stock sin movimiento":
        return resultados.sort_values(
            by=[
                "ventas_recientes_mensualizadas",
                "stock_disponible",
            ],
            ascending=[
                True,
                False,
            ],
        )

    if perfil == "Alta rotación":
        return resultados.sort_values(
            by="rotacion_reciente",
            ascending=False,
        )

    if perfil == "Cobertura elevada":
        return resultados.sort_values(
            by="cobertura_stock_meses",
            ascending=False,
        )

    return resultados.sort_values(
        by="stock_disponible",
        ascending=False,
    )


def construir_contexto_consulta(
    pregunta: str,
    resultados_ml: pd.DataFrame,
) -> str:
    """
    Interpreta la consulta, filtra los resultados con Pandas
    y genera un contexto compacto para el LLM.
    """

    perfil = detectar_perfil(pregunta)
    deposito = detectar_deposito(pregunta)

    marca = detectar_marca(
        pregunta,
        resultados_ml,
    )

    rubro = detectar_rubro(
        pregunta,
        resultados_ml,
    )

    subrubro = detectar_subrubro(
        pregunta,
        resultados_ml,
    )

    limite = detectar_limite_productos(pregunta)
    criterio = detectar_criterio_orden(pregunta)

    resultados_filtrados = filtrar_resultados_ml(
        resultados_ml,
        perfil=perfil,
        deposito=deposito,
        marca=marca,
        rubro=rubro,
        subrubro=subrubro,
    )

    resultados_ordenados = ordenar_resultados(
        resultados_filtrados,
        criterio,
        perfil,
    )

    productos_seleccionados = resultados_ordenados.head(
        limite
    )

    cantidad_total = len(resultados_filtrados)

    stock_total = (
        resultados_filtrados["stock_disponible"].sum()
        if not resultados_filtrados.empty
        else 0
    )

    ventas_totales_mensualizadas = (
        resultados_filtrados[
            "ventas_recientes_mensualizadas"
        ].sum()
        if not resultados_filtrados.empty
        else 0
    )

    lineas = [
        "RESULTADO CALCULADO POR PYTHON Y PANDAS:",
        f"- Perfil: {perfil or 'No especificado'}",
        f"- Depósito: {deposito or 'Todos'}",
        f"- Marca: {marca or 'Todas'}",
        f"- Rubro: {rubro or 'Todos'}",
        f"- Subrubro: {subrubro or 'Todos'}",
        f"- Criterio de orden: {criterio}",
        f"- Cantidad total encontrada: {cantidad_total}",
        f"- Stock disponible total: {stock_total:.0f}",
        (
            "- Ventas recientes mensualizadas totales: "
            f"{ventas_totales_mensualizadas:.2f}"
        ),
        (
            "- Cantidad incluida en el detalle: "
            f"{len(productos_seleccionados)}"
        ),
    ]

    if productos_seleccionados.empty:
        lineas.append(
            "- No se encontraron productos que cumplan "
            "los filtros solicitados."
        )
        lineas.append(
            "- Sugerí probar con otra marca, depósito, rubro "
            "o perfil comercial."
        )

        return "\n".join(lineas)

    lineas.extend(
        [
            "",
            "PRODUCTOS SELECCIONADOS:",
        ]
    )

    for posicion, (_, fila) in enumerate(
        productos_seleccionados.iterrows(),
        start=1,
    ):
        lineas.append(
            (
                f"{posicion}. "
                f"Producto: {fila['producto']}; "
                f"código: {fila['codigo_producto']}; "
                f"marca: {fila.get('marca', 'Sin dato')}; "
                f"rubro: {fila.get('rubro', 'Sin dato')}; "
                f"subrubro: {fila.get('subrubro', 'Sin dato')}; "
                f"perfil: {fila['perfil_comercial']}; "
                f"depósito: {fila['deposito']}; "
                f"stock disponible: {fila['stock_disponible']:.0f}; "
                "ventas recientes mensualizadas: "
                f"{fila['ventas_recientes_mensualizadas']:.2f}; "
                "promedio histórico mensual: "
                f"{fila['promedio_ventas_mensual']:.2f}; "
                "cobertura estimada: "
                f"{fila['cobertura_stock_meses']:.2f} meses; "
                f"rotación reciente: "
                f"{fila['rotacion_reciente']:.4f}."
            )
        )

    return "\n".join(lineas)


def consultar_asistente_comercial(
    pregunta: str,
    resultados_ml: pd.DataFrame
) -> str:
    """
    Consulta al LLM después de resolver los filtros
    y cálculos con Python y Pandas.
    """

    pregunta_limpia = pregunta.strip()

    if not pregunta_limpia:
        raise ValueError(
            "La pregunta no puede estar vacía."
        )

    contexto = construir_contexto_consulta(
        pregunta_limpia,
        resultados_ml,
    )

    cliente, modelo = crear_cliente_hugging_face()

    instrucciones = """
    Sos un analista de inteligencia comercial para una cadena
    argentina de calzado e indumentaria.

    Los filtros, búsquedas, ordenamientos y cálculos ya fueron
    realizados mediante Python, Pandas y un modelo K-Means.
    Tu tarea es redactar una respuesta clara usando exclusivamente
    el contexto recibido.

    Reglas:
    - No inventes productos, códigos, marcas, cifras ni depósitos.
    - Indicá cuántos resultados totales se encontraron.
    - Si se muestra una selección, aclaralo.
    - Respetá el criterio de orden indicado en el contexto.
    - Explicá brevemente qué criterio se usó para ordenar
    los productos.
    - Si el criterio es revision_prioritaria, aclarar que se
    priorizan productos con stock alto, baja venta reciente
    y cobertura elevada.
    - Listá únicamente los productos incluidos en el contexto.
    - Diferenciá stock actual, ventas recientes mensualizadas
    y promedio histórico mensual.
    - Los perfiles de K-Means son agrupaciones exploratorias,
    no diagnósticos absolutos.
    - Recordá que el sistema no predice ventas futuras.
    - Si no hay resultados, sugerí reformular la consulta
    con marca, depósito, rubro o perfil comercial.
    - Respondé de forma breve y ejecutiva.
    - Respondé en español.
    """.strip()

    mensaje_usuario = f"""
    CONTEXTO CALCULADO:

    {contexto}

    PREGUNTA:

    {pregunta_limpia}
    """.strip()

    try:
        respuesta = cliente.chat.completions.create(
            model=modelo,
            messages=[
                {
                    "role": "system",
                    "content": instrucciones,
                },
                {
                    "role": "user",
                    "content": mensaje_usuario,
                },
            ],
            temperature=0.2,
            max_tokens=750,
        )

    except Exception as error:
        raise RuntimeError(
            "No se pudo obtener una respuesta de Hugging Face. "
            f"Detalle: {error}"
        ) from error

    contenido = respuesta.choices[0].message.content

    if not contenido:
        raise RuntimeError(
            "El modelo no devolvió contenido."
        )

    return contenido.strip()
