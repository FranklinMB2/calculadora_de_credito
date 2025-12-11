import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# =========================================
#      LÓGICA DEL CRÉDITO
# =========================================

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
        return 0

    years_diff = fecha_pago_real.year - fecha_pago_esperado.year
    months_diff = fecha_pago_real.month - fecha_pago_esperado.month

    meses = years_diff * 12 + months_diff

    if fecha_pago_real.day < fecha_pago_esperado.day:
        meses -= 1

    return max(0, meses)


# =========================================
#      EXPORTAR PDF
# =========================================

def exportar_pdf(capital_inicial, capital_final, historial):
    try:
        archivo = "resultado_credito.pdf"
        c = canvas.Canvas(archivo, pagesize=letter)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "Reporte del Crédito con Mora")

        c.setFont("Helvetica", 12)
        c.drawString(50, 720, f"Capital inicial: {capital_inicial:,.2f}")
        c.drawString(50, 700, f"Capital final: {capital_final:,.2f}")
        c.drawString(50, 680, "Historial por mes:")

        y = 660
        for h in historial:
            texto = (
                f"Mes {h['mes']}: Capital antes = {h['capital_antes']}, "
                f"Interés = {h['interes']}, Capital después = {h['capital_despues']}"
            )
            c.drawString(50, y, texto)
            y -= 20
            if y < 50:
                c.showPage()
                y = 750

        c.save()
        messagebox.showinfo("PDF generado", f"Archivo creado: {archivo}")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF\n{str(e)}")


# =========================================
#      GRAFICAR
# =========================================

def graficar(historial):
    meses = [h["mes"] for h in historial]
    capitales = [h["capital_despues"] for h in historial]

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(meses, capitales, marker="o")
    ax.set_title("Capital vs Tiempo (Meses de Mora)")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Capital")
    ax.grid(True)

    return fig


# =========================================
#      TKINTER - INTERFAZ
# =========================================

def procesar():
    global historial_global, capital_final_global, capital_inicial_global

    try:
        capital = float(entry_capital.get())
        tasa = float(entry_tasa.get())
        fecha_esperada = datetime.strptime(entry_fecha_esperada.get(), "%Y-%m-%d")
        fecha_real = datetime.strptime(entry_fecha_real.get(), "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Verifique los datos ingresados.")
        return

    capital_inicial_global = capital

    meses_mora = calcular_meses_de_mora(fecha_esperada, fecha_real)

    for row in tabla.get_children():
        tabla.delete(row)

    if meses_mora == 0:
        messagebox.showinfo("Resultado", f"Pago puntual.\nCapital final: ${capital:,.2f}")
        historial_global = []
        capital_final_global = capital
        return

    capital_final, historial = actualizar_capital_por_meses(capital, tasa, meses_mora)

    capital_final_global = capital_final
    historial_global = historial

    for h in historial:
        tabla.insert("", "end", values=(h["mes"], h["capital_antes"], h["interes"], h["capital_despues"]))

    messagebox.showinfo("Resultado", f"Meses de mora: {meses_mora}\nCapital final: ${capital_final:,.2f}")

    fig = graficar(historial)
    canvas_plot = FigureCanvasTkAgg(fig, master=ventana)
    canvas_plot.get_tk_widget().pack()
    canvas_plot.draw()


# ---------------------------------------------

ventana = tk.Tk()
ventana.title("Calculadora de Crédito con Mora")
ventana.geometry("750x800")

tk.Label(ventana, text="Valor del crédito:").pack()
entry_capital = tk.Entry(ventana)
entry_capital.pack()

tk.Label(ventana, text="Interés (%):").pack()
entry_tasa = tk.Entry(ventana)
entry_tasa.pack()

tk.Label(ventana, text="Fecha límite (YYYY-MM-DD):").pack()
entry_fecha_esperada = tk.Entry(ventana)
entry_fecha_esperada.pack()

tk.Label(ventana, text="Fecha real de pago (YYYY-MM-DD):").pack()
entry_fecha_real = tk.Entry(ventana)
entry_fecha_real.pack()

tk.Button(ventana, text="Calcular", command=procesar, bg="green", fg="white").pack(pady=10)

columnas = ("Mes", "Capital Antes", "Interés", "Capital Después")
tabla = ttk.Treeview(ventana, columns=columnas, show="headings", height=8)

for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=150, anchor="center")

tabla.pack()

tk.Button(ventana, text="Exportar PDF", bg="blue", fg="white",
          command=lambda: exportar_pdf(capital_inicial_global, capital_final_global, historial_global)).pack(pady=10)

ventana.mainloop()
