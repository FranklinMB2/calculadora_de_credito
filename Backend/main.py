from datetime import datetime, timedelta
import math

# ============================================================
#        CALCULADORA COMPLETA DE CRÉDITO CON MORA
#        - Cuotas fijas (método francés)
#        - Mora automática si no paga o paga incompleto
#        - Recalculo de cuotas cuando hay mora o pagos parciales
#        - Evita saldos negativos y cuotas negativas
#        - Pagos adelantados reducen saldo
# ============================================================


def calcular_cuota_fija(capital, tasa, meses):
    """Cálculo de cuota fija (método francés)."""
    tasa_decimal = tasa / 100
    if meses == 0:
        return 0
    cuota = capital * (tasa_decimal * (1 + tasa_decimal)**meses) / ((1 + tasa_decimal)**meses - 1)
    return max(cuota, 0)  # nunca negativa


def sumar_un_mes(fecha):
    """Devuelve la misma fecha del siguiente mes, corrigiendo días inexistentes."""
    mes = fecha.month + 1
    año = fecha.year
    if mes > 12:
        mes = 1
        año += 1
    try:
        return fecha.replace(year=año, month=mes)
    except:
        # Si el día no existe (ej: 31), usar el último día del nuevo mes
        return (fecha.replace(day=1, month=mes, year=año) + timedelta(days=32)).replace(day=1) - timedelta(days=1)


def main():
    print("=== CALCULADORA COMPLETA DE CRÉDITO ===\n")

    capital_inicial = float(input("Valor del crédito: "))
    interes = float(input("Interés mensual (%): "))
    meses = int(input("Número de meses: "))

    fecha_aprobacion = datetime.now().date()
    print(f"\nFecha de aprobación del crédito: {fecha_aprobacion}\n")

    cuota = calcular_cuota_fija(capital_inicial, interes, meses)

    # ================= TABLA INICIAL ==================
    print("===== TABLA INICIAL DE CUOTAS =====")
    fechas_limite = []
    fecha_limite = sumar_un_mes(fecha_aprobacion)

    for i in range(1, meses + 1):
        fechas_limite.append(fecha_limite)
        print(f"Mes {i} | Cuota: ${cuota:,.2f} | Fecha límite: {fecha_limite}")
        fecha_limite = sumar_un_mes(fecha_limite)

    # ============= PROCESO MENSUAL DE PAGOS ==============
    saldo = capital_inicial
    fecha_actual_limite = fechas_limite[0]

    print("\n===== REGISTRO DE PAGOS =====\n")

    for mes_actual in range(1, meses + 1):

        if saldo <= 0:
            print("\n*** CRÉDITO PAGADO COMPLETAMENTE ***")
            break

        cuota_esperada = calcular_cuota_fija(saldo, interes, meses - mes_actual + 1)
        cuota_esperada = max(cuota_esperada, 0)

        print(f"--- MES {mes_actual} ---")
        print(f"Saldo actual: ${saldo:,.2f}")
        print(f"Cuota esperada: ${cuota_esperada:,.2f}")
        print(f"Fecha límite: {fecha_actual_limite}")

        pago = float(input(f"¿Cuánto pagó el usuario en el mes {mes_actual}? "))

        # ===================== MORA =====================
        fecha_pago = datetime.now().date()
        if fecha_pago > fecha_actual_limite:
            print("Pago con mora")
            interes_mora = saldo * (interes / 100)
            saldo += interes_mora
            print(f"Se aplicó interés de mora: ${interes_mora:,.2f}")

        # ================== PAGO NORMAL ==================
        if pago < cuota_esperada:
            falta = cuota_esperada - pago
            print(f"Pagó menos que la cuota. Falta: ${falta:,.2f}")
            saldo += falta * (interes / 100)
            print(f"Se aplicó interés por saldo faltante.")

        elif pago > cuota_esperada:
            extra = pago - cuota_esperada
            print(f"Pagó más de lo debido, extra: ${extra:,.2f}")
            saldo -= extra

        # descontar pago normal
        saldo -= min(pago, cuota_esperada)

        # evitar saldo negativo
        if saldo < 0:
            saldo = 0

        print(f"Saldo después del pago: ${saldo:,.2f}\n")

        # ========== RECÁLCULO DE CUOTAS SI NO SE PAGÓ COMPLETO ============
        meses_restantes = meses - mes_actual
        if saldo > 0 and meses_restantes > 0:
            cuota = calcular_cuota_fija(saldo, interes, meses_restantes)
            cuota = max(cuota, 0)

            print("*** NUEVAS CUOTAS CALCULADAS ***")
            print(f"Meses restantes: {meses_restantes}")
            print(f"Nueva cuota mensual: ${cuota:,.2f}\n")

        # avanzar fecha límite
        if mes_actual < meses:
            fecha_actual_limite = fechas_limite[mes_actual]

    # ============= FIN DEL PROCESO =============
    print("\n===== RESUMEN FINAL =====")
    print(f"Saldo final del crédito: ${saldo:,.2f}")
    if saldo == 0:
        print("El crédito fue pagado completamente.")


if __name__ == "__main__":
    main()
