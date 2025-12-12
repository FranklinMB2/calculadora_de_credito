from datetime import datetime, timedelta
from typing import Dict, Any
import math

# =================================================================
# Archivo: calculadora_simulacion_terminal.py
# Propósito: Lógica de cálculo de crédito con manejo de mora por interés
# =================================================================

# ==================== FUNCIONES DE CÁLCULO ====================

def calcular_cuota_fija(capital: float, tasa: float, meses: int) -> float:
    """
    Cálculo de cuota fija (Sistema Francés), con manejo de tasa 0%.
    """
    tasa_decimal = tasa / 100
    
    if meses <= 0 or capital <= 0:
        return 0

    if tasa_decimal == 0:
        return capital / meses

    try:
        numerador = tasa_decimal * (1 + tasa_decimal)**meses
        denominador = (1 + tasa_decimal)**meses - 1
        if denominador == 0:
             return capital
             
        cuota = capital * (numerador / denominador)
        return max(cuota, 0)
    except OverflowError:
        return float('inf')


def sumar_un_mes(fecha: datetime.date) -> datetime.date:
    """Devuelve la misma fecha del siguiente mes, corrigiendo días inexistentes."""
    mes = fecha.month + 1
    año = fecha.year
    if mes > 12:
        mes = 1
        año += 1
    
    try:
        return fecha.replace(year=año, month=mes)
    except ValueError:
        # Si el día no existe (ej: 31 de marzo -> 31 de abril), usar el último día del nuevo mes.
        next_month_start = (fecha.replace(day=1, month=mes, year=año) + timedelta(days=32)).replace(day=1)
        return next_month_start - timedelta(days=1)

# ==================== LÓGICA PRINCIPAL DE SIMULACIÓN ====================

def main():
    print("=== CALCULADORA DE CRÉDITO (Continuación hasta Saldo Cero) ===\n")

    try:
        capital_inicial = float(input("Valor del crédito: "))
        interes = float(input("Interés mensual (%): "))
        meses_plazo_original = int(input("Número de meses (Plazo Original): "))
    except ValueError:
        print("\nError: Por favor, ingrese valores numéricos válidos.")
        return

    if capital_inicial <= 0 or meses_plazo_original <= 0:
        print("\nEl capital y el número de meses deben ser mayores a cero.")
        return

    fecha_aprobacion = datetime.now().date()
    print(f"\nFecha de aprobación del crédito: {fecha_aprobacion}\n")

    # La cuota original se calcula con el plazo inicial
    cuota_original = calcular_cuota_fija(capital_inicial, interes, meses_plazo_original)
    saldo = capital_inicial
    
    # Pre-calcular las primeras fechas límite para la tabla inicial
    fechas_limite = []
    fecha_limite = fecha_aprobacion
    for _ in range(meses_plazo_original):
        fecha_limite = sumar_un_mes(fecha_limite)
        fechas_limite.append(fecha_limite)

    # ================= TABLA INICIAL ==================
    print("\n===== TABLA INICIAL DE CUOTAS =====")
    for i, fecha in enumerate(fechas_limite):
        print(f"Mes {i+1} | Cuota inicial: ${cuota_original:,.2f} | Fecha límite: {fecha}")

    # ============= PROCESO MENSUAL DE PAGOS (BUCLE INDEFINIDO) ==============
    print("\n===== REGISTRO DE PAGOS Y SIMULACIÓN =====\n")
    
    # Inicializar contadores para el bucle WHILE
    mes_actual = 0
    fecha_limite_actual = fecha_aprobacion
    
    # El bucle continúa mientras haya saldo pendiente
    while saldo > 0:
        
        mes_actual += 1
        fecha_limite_actual = sumar_un_mes(fecha_limite_actual)
        
        # El número de meses restantes para el recálculo debe basarse en el plazo original
        if mes_actual <= meses_plazo_original:
            meses_restantes_para_cuota = meses_plazo_original - mes_actual + 1
            es_plazo_extra = False
        else:
            # Si ya pasamos el plazo original, usamos 1 mes para forzar la liquidación
            meses_restantes_para_cuota = 1 
            es_plazo_extra = True

        cuota_esperada = calcular_cuota_fija(saldo, interes, meses_restantes_para_cuota)
        pago = 0.0

        print(f"--- MES {mes_actual} --- (Plazo Original: {meses_plazo_original} meses)")
        print(f"Saldo actual: ${saldo:,.2f}")
        
        if es_plazo_extra:
             print(f"*** ¡PLAZO ORIGINAL VENCIDO! ***")
             print(f"Cuota esperada (para liquidar en 1 mes): ${cuota_esperada:,.2f}")
        else:
             print(f"Cuota esperada: ${cuota_esperada:,.2f}")
             
        print(f"Fecha límite de pago: {fecha_limite_actual}")

        # 1. CONFIRMACIÓN DE PAGO
        pago_confirmado_str = input(f"¿Se realizó algún pago en el mes {mes_actual}? (s/n): ").lower()
        hubo_pago = (pago_confirmado_str == 's' or pago_confirmado_str == 'si')

        # 2. CALCULAR INTERÉS PERIÓDICO (Necesario para ambos casos: Mora o Pago)
        interes_periodo = saldo * (interes / 100)
        
        # 3. GESTIÓN DE INCUMPLIMIENTO/PAGO
        if not hubo_pago:
            # === INCUMPLIMIENTO TOTAL (APLICAR SOLO INTERÉS) ===
            print("\n¡INCUMPLIMIENTO TOTAL! No se realizó el pago este mes.")
            
            # LÓGICA DE PENALIDAD: SUMAR SOLO EL INTERÉS GENERADO AL SALDO
            saldo += interes_periodo
            
            print(f"Se aplicó un cargo de ${interes_periodo:,.2f} al saldo (Solo Interés de la Mora).")
            print(f"La cuota esperada de ${cuota_esperada:,.2f} NO fue cargada al capital.")
            
        else:
            # === PAGO REALIZADO ===
            try:
                pago = float(input(f"¿Cuánto pagó el usuario? "))
            except ValueError:
                print("Monto de pago inválido. Asumiendo pago de $0.")
                pago = 0.0
                
            if pago < 0:
                pago = 0.0
            
            print("-" * 35)

            # 4. AMORTIZACIÓN REAL Y GESTIÓN DE SALDO (Solo si hubo pago)
            
            if pago < interes_periodo:
                # Pago < Interés: Capitalización. El saldo SUBE.
                capitalizacion = interes_periodo - pago
                saldo += capitalizacion
                print(f"\nPago < Interés (${interes_periodo:,.2f}). El capital aumentó (Capitalización): ${capitalizacion:,.2f}.")
            
            else:
                # Pago >= Interés: Amortización. El saldo BAJA.
                amortizacion = pago - interes_periodo
                saldo -= amortizacion
                
                print(f"\nInterés cubierto: ${interes_periodo:,.2f} | Amortización a capital: ${amortizacion:,.2f}")
                
                # Chequeo de pago extra
                if pago > cuota_esperada:
                    extra = pago - cuota_esperada
                    print(f"¡Pago EXTRA de capital por ${extra:,.2f}!")

        # 5. Ajuste final del saldo
        if saldo < 0:
            saldo = 0
            
        print(f"\n*** Saldo después del procesamiento: ${saldo:,.2f} ***\n")

    # ============= FIN DEL PROCESO =============
    print("\n======================================")
    print(f"*** CRÉDITO LIQUIDADO COMPLETAMENTE ***")
    print(f"Saldo final: ${saldo:,.2f}")
    print(f"El crédito fue pagado en un total de {mes_actual} meses.")
    print(f"======================================")


if __name__ == "__main__":
    main()