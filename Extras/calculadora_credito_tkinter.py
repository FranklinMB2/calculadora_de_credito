import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


# =============== LÓGICA DEL CRÉDITO ===================

def calcular_interes(capital, tasa):
    return capital * (tasa / 100)


def actualizar_capital_por_meses(capital, tasa, meses_mora):
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
    if fecha_pago_real <= fecha_pago_esperado:
        return 0  # Pagó a tiempo

    years_diff = fecha_pago_real.year - fecha_pago_esperado.year
    months_diff = fecha_pago_real.month - fecha_pago_esperado.month

    meses = years_diff * 12 + months_diff

    if fecha_pago_real.day < fecha_pago_esperado.day:
        meses -= 1

    return max(0, meses)


# =============== INTERFAZ TKINTER ===================

def procesar():
    try:
        capital = float(entry_capital.get())
        tasa = float(entry_tasa.get())

        fecha_esperada = datetime.strptime(entry_fecha_esperada.get(), "%Y-%m-%d")
        fecha_real = datetime.strptime(entry_fecha_real.get(), "%Y-%m-%d")

    except ValueError:
        messagebox.showerror("Error", "Por favor verifica los valores ingresados.")
        return

    meses_mora = calcular_meses_de_mora(fecha_esperada, fecha_real)

    # Limpiamos tabla
    for row in tabla.get_children():
        tabla.delete(row)

    if meses_mora == 0:
        messagebox.showinfo("Resultado", f"El pago fue puntual.\nCapital final: ${capital:,.2f}")
        return

    capital_final, historial = actualizar_capital_por_meses(capital, tasa, meses_mora)

    # Insertar filas en la tabla
    for h in historial:
        tabla.insert("", "end", values=(
            h["mes"],
            h["capital_antes"],
            h["interes"],
            h["capital_despues"]
        ))

    messagebox.showinfo("Resultado",
                        f"Meses de mora: {meses_mora}\n\nCapital final: ${capital_final:,.2f}")


# =============== CREACIÓN DE LA VENTANA ===================

ventana = tk.Tk()
ventana.title("Calculadora de Crédito con Mora")
ventana.geometry("650x500")

# ==== Entradas ====

tk.Label(ventana, text="Valor del crédito (capital):").pack()
entry_capital = tk.Entry(ventana)
entry_capital.pack()

tk.Label(ventana, text="Interés (%):").pack()
entry_tasa = tk.Entry(ventana)
entry_tasa.pack()

tk.Label(ventana, text="Fecha límite de pago (YYYY-MM-DD):").pack()
entry_fecha_esperada = tk.Entry(ventana)
entry_fecha_esperada.pack()

tk.Label(ventana, text="Fecha real de pago (YYYY-MM-DD):").pack()
entry_fecha_real = tk.Entry(ventana)
entry_fecha_real.pack()

# Botón
tk.Button(ventana, text="Calcular", command=procesar, bg="green", fg="white").pack(pady=10)

# ==== Tabla ====

columnas = ("Mes", "Capital Antes", "Interés", "Capital Después")
tabla = ttk.Treeview(ventana, columns=columnas, show="headings", height=10)

for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, anchor="center", width=120)

tabla.pack(expand=True)

ventana.mainloop()
