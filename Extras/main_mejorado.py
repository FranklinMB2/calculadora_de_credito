from datetime import datetime, date
from decimal import Decimal, getcontext, ROUND_HALF_UP
from typing import Tuple, List, Dict

# =========================================
#   CALCULADORA DE CRÉDITO CON MORA (MEJORADA)
# =========================================

# Precisión suficiente para cálculos monetarios
getcontext().prec = 28


def _to_decimal(value: float | str | Decimal) -> Decimal:
    """Convierte entrada a Decimal, aceptando comas como separador decimal."""
    if isinstance(value, Decimal):
        return value
    s = str(value).replace(',', '.')
    return Decimal(s)


def calcular_interes(capital: Decimal, tasa_porcentaje: Decimal) -> Decimal:
    """Retorna el interés (en la misma unidad que `capital`).

    `tasa_porcentaje` se interpreta como porcentaje por periodo (ej. por mes).
    """
    return (capital * tasa_porcentaje / Decimal(100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def actualizar_capital_por_meses(capital: Decimal, tasa_porcentaje: Decimal, meses_mora: int) -> Tuple[Decimal, List[Dict]]:
    """Aplica interés compuesto por cada mes de mora y devuelve (capital_final, historial)."""
    historial: List[Dict] = []

    for mes in range(1, max(0, meses_mora) + 1):
        interes = calcular_interes(capital, tasa_porcentaje)
        nuevo_capital = (capital + interes).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        historial.append({
            'mes': mes,
            'capital_antes': capital.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            'interes': interes,
            'capital_despues': nuevo_capital,
        })

        capital = nuevo_capital

    return capital, historial


def calcular_meses_de_mora(fecha_pago_esperado: date, fecha_pago_real: date) -> int:
    """Calcula meses completos de mora entre dos fechas.

    Si `fecha_pago_real` <= `fecha_pago_esperado` retorna 0.
    """
    if fecha_pago_real <= fecha_pago_esperado:
        return 0

    years_diff = fecha_pago_real.year - fecha_pago_esperado.year
    months_diff = fecha_pago_real.month - fecha_pago_esperado.month
    meses = years_diff * 12 + months_diff

    if fecha_pago_real.day < fecha_pago_esperado.day:
        meses -= 1

    return max(0, meses)


def formato_moneda(valor: Decimal) -> str:
    v = valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return f"${v:,.2f}"


def parse_fecha(texto: str) -> date:
    """Parsea una fecha en formato ISO `YYYY-MM-DD`. Lanza ValueError si falla."""
    return datetime.strptime(texto.strip(), "%Y-%m-%d").date()


def run_cli() -> None:
    """Interfaz por consola separada de la lógica, preparada para pruebas."""
    print("=== CALCULADORA DE CRÉDITO CON DETECCIÓN AUTOMÁTICA DE MORA ===\n")

    try:
        raw_capital = input("Valor del crédito: ").strip()
        raw_capital = raw_capital.replace(' ', '')
        capital = _to_decimal(raw_capital)

        raw_tasa = input("Interés (% por mes): ").strip()
        tasa = _to_decimal(raw_tasa)

        if capital <= 0:
            raise ValueError("El capital debe ser mayor que cero.")
        if tasa < 0:
            raise ValueError("La tasa no puede ser negativa.")

        fecha_esperada = parse_fecha(input("Fecha límite de pago (YYYY-MM-DD): "))
        fecha_real = parse_fecha(input("Fecha real de pago (YYYY-MM-DD): "))

    except Exception as e:
        print(f"Entrada inválida: {e}")
        return

    meses_mora = calcular_meses_de_mora(fecha_esperada, fecha_real)
    print(f"\nMeses de mora detectados: {meses_mora}")

    if meses_mora == 0:
        print("\nEl pago fue puntual. No se incrementa el capital.")
        print(f"Capital final: {formato_moneda(capital)}")
        return

    capital_final, historial = actualizar_capital_por_meses(capital, tasa, meses_mora)

    print("\n===== RESULTADOS =====")
    print(f"Capital inicial: {formato_moneda(capital)}")
    print(f"Capital final después de mora: {formato_moneda(capital_final)}")

    print("\n===== HISTORIAL MENSUAL =====")
    for h in historial:
        print(
            f"Mes {h['mes']} | Capital antes: {formato_moneda(h['capital_antes'])} "
            f"| Interés: {formato_moneda(h['interes'])} | Capital después: {formato_moneda(h['capital_despues'])}"
        )


if __name__ == "__main__":
    run_cli()
