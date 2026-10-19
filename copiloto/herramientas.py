"""Funciones independientes del LLM: se prueban primero y se registran después como tools."""

from decimal import ROUND_HALF_UP, Decimal


def calcular_presupuesto(horas: float, tarifa: float) -> dict:
    """Calcula el costo en bolivianos de una actividad según horas y tarifa por hora."""
    h, t = Decimal(str(horas)), Decimal(str(tarifa))
    if not h.is_finite() or not t.is_finite() or not (0 <= h <= 1000 and 0 <= t <= 100000):
        raise ValueError("Horas y tarifa deben ser finitas, positivas y estar dentro del rango.")
    return {
        "horas": horas,
        "tarifa": tarifa,
        "total": float((h * t).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "moneda": "BOB",
    }
