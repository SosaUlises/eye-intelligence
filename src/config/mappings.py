MAPEO_SUCURSAL_DEPOSITO = {
    "RICARDONE": "DEPOSITO RICARDONE",
    "PUERTO": "DEPOSITO PUERTO",
    "SAN LORENZO": "DEPOSITO SAN LORENZO",
    "SAN LORENZO KIDS": "DEPOSITO SAN LORENZO KIDS",
    "BERMUDEZ OUTLET": "DEPOSITO BERMUDEZ OUTLET",
}


def obtener_deposito_desde_sucursal(
    sucursal: str,
    ) -> str | None:
    """
    Devuelve el depósito asociado a una sucursal.
    """

    if not sucursal:
        return None

    sucursal_normalizada = str(sucursal).strip().upper()

    return MAPEO_SUCURSAL_DEPOSITO.get(
        sucursal_normalizada
    )