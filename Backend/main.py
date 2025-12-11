from datetime import datetime

# =========================================
#   CALCULADORA DE CRÉDITO CON MORA (AUTOMÁTICO)
# =========================================


def calcular_interes(capital, tasa):
    """Retorna el valor del interés sobre el capital."""
    return capital * (tasa / 100)


def actualizar_capital_por_meses(capital, tasa, meses_mora):
    """
    Aplica interés compuesto por cada mes de mora.
    """
    historial = []

    for mes in range(1, meses_mora + 1):
        interes = calcular_interes(capital, tasa)
        nuevo_capital = capital + interes

        historial.append({
            "mes": mes,
            "capital_antes": round(capital, 2),
            "interes": round(interes, 2),
            "capital_despues": round(nuevo_capital, 2)
        })

        capital = nuevo_capital

    return capital, historial


def calcular_meses_de_mora(fecha_pago_esperado, fecha_pago_real):
    """Calcula meses completos de mora considerando años, meses y días."""

    if fecha_pago_real <= fecha_pago_esperado:
        return 0  # pagó puntualmente

    # 1. Diferencia básica de años y meses
    years_diff = fecha_pago_real.year - fecha_pago_esperado.year
    months_diff = fecha_pago_real.month - fecha_pago_esperado.month

    meses = years_diff * 12 + months_diff

    # 2. Ajuste según los días exactos
    # Si todavía no ha llegado al día del mes esperado → NO es mes completo
    if fecha_pago_real.day < fecha_pago_esperado.day:
        meses -= 1

    # No dejar valores negativos
    return max(0, meses)



def main():
    print("=== CALCULADORA DE CRÉDITO CON DETECCIÓN AUTOMÁTICA DE MORA ===\n")

    capital = float(input("Valor del crédito: "))
    tasa = float(input("Interés (%): "))

    fecha_esperada = input("Fecha límite de pago (YYYY-MM-DD): ")
    fecha_real = input("Fecha real de pago (YYYY-MM-DD): ")

    # Convertir fechas a datetime
    fecha_esperada = datetime.strptime(fecha_esperada, "%Y-%m-%d")
    fecha_real = datetime.strptime(fecha_real, "%Y-%m-%d")

    # Calcular mora
    meses_mora = calcular_meses_de_mora(fecha_esperada, fecha_real)

    print(f"\nMeses de mora detectados: {meses_mora}")

    # Si no hubo mora, no se cambia el capital
    if meses_mora == 0:
        print("\nEl pago fue puntual. No se incrementa el capital.")
        print(f"Capital final: ${capital:,.2f}")
        return

    # Aplicar interés por mora
    capital_final, historial = actualizar_capital_por_meses(capital, tasa, meses_mora)

    print("\n===== RESULTADOS =====")
    print(f"Capital inicial: ${capital:,.2f}")
    print(f"Capital final después de mora: ${capital_final:,.2f}")

    print("\n===== HISTORIAL MENSUAL =====")
    for h in historial:
        print(
            f"Mes {h['mes']} | Capital antes: ${h['capital_antes']:,.2f} "
            f"| Interés: ${h['interes']:,.2f} | Capital después: ${h['capital_despues']:,.2f}"
        )


if __name__ == "__main__":
    main()
