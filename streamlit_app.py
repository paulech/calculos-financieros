
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="MatFin – Derecho Bancario", layout="wide")
st.title("Calculadora Interactiva – Matemática Financiera (Derecho Bancario)")

# -------------------------
# Formato de tasa
# -------------------------
st.sidebar.header("Formato de tasa")
modo = st.sidebar.selectbox("Cómo querés ingresar la tasa", ["Decimal (0.2)", "Porcentaje (20)"])

def tasa_input(label, default_decimal=0.10):
    if modo == "Decimal (0.2)":
        i = st.sidebar.number_input(f"{label} (decimal)", min_value=0.0, max_value=1.0, value=float(default_decimal), step=0.005, format="%.3f")
        return i, i*100.0
    else:
        i_pct = st.sidebar.number_input(f"{label} (%)", min_value=0.0, max_value=100.0, value=float(default_decimal*100.0), step=0.1, format="%.1f")
        return i_pct/100.0, i_pct

# -------------------------
# Selector de módulos
# -------------------------
st.sidebar.header("Parámetros generales")
modulo = st.sidebar.selectbox("Módulo",
                              ["Interés simple/compuesto",
                               "Descuento y equivalencias",
                               "Amortización: Francés/Alemán/Americano",
                               "Tasas y CFT (TNA↔TEA+CFT)",
                               "Precanc. y recálculo (consumo/hipoteca)",
                               "Imputación de pagos parciales",
                               "Actualización + tasa pura (simulación)"])

# -------------------------
# Utilidades financieras
# -------------------------
def cuota_frances(P, i, n):
    if n == 0 or i == 0:
        return P / n if n else 0.0
    return P * (i * (1 + i)**n) / ((1 + i)**n - 1)

def tabla_frances(P, i, n):
    A = cuota_frances(P, i, n)
    saldo = P
    rows = []
    for t in range(1, n+1):
        interes = saldo * i
        amort = A - interes
        saldo = round(saldo - amort, 2)
        rows.append([t, max(saldo+amort,0), interes, amort, A, max(saldo,0)])
    return pd.DataFrame(rows, columns=["Periodo","Saldo Inicial","Interés","Amortización","Cuota","Saldo Final"])

def tabla_aleman(P, i, n):
    amort_fija = P / n if n else 0
    saldo = P
    rows = []
    for t in range(1, n+1):
        interes = saldo * i
        cuota = interes + amort_fija
        saldo = round(saldo - amort_fija, 2)
        rows.append([t, max(saldo+amort_fija,0), interes, amort_fija, cuota, max(saldo,0)])
    return pd.DataFrame(rows, columns=["Periodo","Saldo Inicial","Interés","Amortización","Cuota","Saldo Final"])

def tabla_americano(P, i, n):
    rows = []
    for t in range(1, n+1):
        saldo_ini = P
        interes = saldo_ini * i
        amort = P if t == n else 0
        cuota = interes + amort
        saldo_fin = 0 if t == n else P
        rows.append([t, saldo_ini, interes, amort, cuota, saldo_fin])
    return pd.DataFrame(rows, columns=["Periodo","Saldo Inicial","Interés","Amortización","Cuota","Saldo Final"])

def tna_to_tea(tna, m):
    # tna prorrateada a i_per = tna/m y capitalización m veces
    i_per = tna / m
    return (1 + i_per)**m - 1

def tea_to_tna(tea, m):
    i_per = (1 + tea)**(1/m) - 1
    return i_per * m

# -------------------------
# Módulos
# -------------------------
if modulo == "Interés simple/compuesto":
    C = st.sidebar.number_input("Capital (C)", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
    i, i_pct = tasa_input("Tasa por período (i)", default_decimal=0.10)
    n = st.sidebar.number_input("Número de períodos (n)", min_value=1, max_value=360, value=12, step=1)

    I_s = C * i * n
    VF_s = C + I_s
    VF_c = C * (1 + i)**n
    I_c = VF_c - C

    st.subheader("Resultados")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Interés simple total**"); st.write(I_s)
        st.markdown("**VF simple**"); st.write(VF_s)
    with col2:
        st.markdown("**Interés compuesto total**"); st.write(I_c)
        st.markdown("**VF compuesto**"); st.write(VF_c)
    st.caption(f"Tasa usada: {i_pct:.2f}% por período")

    xs = np.arange(0, int(n)+1)
    vf_simple = C * (1 + i*xs)
    vf_comp = C * (1 + i)**xs
    fig, ax = plt.subplots()
    ax.plot(xs, vf_simple, label="Simple")
    ax.plot(xs, vf_comp, label="Compuesto")
    ax.set_xlabel("Períodos"); ax.set_ylabel("Monto"); ax.legend()
    st.pyplot(fig)

elif modulo == "Descuento y equivalencias":
    i, i_pct = tasa_input("Tasa de interés por período (i)", default_decimal=0.10)
    VF = st.sidebar.number_input("Valor Futuro (VF)", min_value=0.0, value=110000.0, step=1000.0, format="%.2f")
    n = st.sidebar.number_input("Número de períodos (n)", min_value=1, max_value=360, value=2, step=1)
    d_s, d_s_pct = tasa_input("Tasa descuento simple (d_s)", default_decimal=0.10)

    d = i / (1 + i) if (1+i)!=0 else 0
    i_rec = d / (1 - d) if d < 1 else float('nan')
    vp_r = VF / (1 + i)**n
    vp_c = VF * (1 - d_s*n)

    st.subheader("Resultados")
    st.write(pd.DataFrame({
        "Magnitud": ["d equivalente a i", "i recuperada desde d", "VP racional compuesto", "VP comercial simple (si d_s·n<1)"],
        "Valor": [d, i_rec, vp_r, vp_c]
    }))
    st.caption(f"i = {i_pct:.2f}% por período | d_s = {d_s_pct:.2f}% simple por período")

elif modulo == "Amortización: Francés/Alemán/Americano":
    sistema = st.sidebar.selectbox("Sistema", ["Francés","Alemán","Americano"])
    P = st.sidebar.number_input("Principal (P)", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
    i, i_pct = tasa_input("Tasa por período (i)", default_decimal=0.02)
    n = st.sidebar.number_input("Número de períodos (n)", min_value=1, max_value=360, value=12, step=1)

    if sistema == "Francés":
        df = tabla_frances(P, i, n)
    elif sistema == "Alemán":
        df = tabla_aleman(P, i, n)
    else:
        df = tabla_americano(P, i, n)

    st.subheader("Cronograma"); st.dataframe(df)
    st.caption(f"Tasa usada: {i_pct:.3f}% por período")
    fig, ax = plt.subplots()
    if sistema in ("Francés","Alemán"):
        ax.plot(df["Periodo"], df["Interés"], label="Interés")
        ax.plot(df["Periodo"], df["Amortización"], label="Amortización")
    else:
        ax.plot(df["Periodo"], df["Cuota"], label="Cuota")
    ax.set_xlabel("Periodo"); ax.set_ylabel("Monto"); ax.legend()
    st.pyplot(fig)

elif modulo == "Tasas y CFT (TNA↔TEA+CFT)":
    st.subheader("Conversión TNA ↔ TEA y CFT")
    base = st.sidebar.selectbox("Base de capitalización m (por año)", [1,2,4,12,365])
    # entrada flexible: TNA o TEA
    tipo = st.sidebar.selectbox("Ingresar", ["TNA", "TEA"])
    if tipo == "TNA":
        tna, tna_pct = tasa_input("TNA", default_decimal=0.60)
        tea = tna_to_tea(tna, base)
    else:
        tea, tea_pct = tasa_input("TEA", default_decimal=0.796)
        tna = tea_to_tna(tea, base)

    # CFT: sumar cargos porcentuales por período equivalentes
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Componentes de CFT (% sobre saldo o capital)**")
    gastos_pct = st.sidebar.number_input("Gastos administrativos (%)", min_value=0.0, max_value=100.0, value=3.0, step=0.1, format="%.1f")
    seguros_pct = st.sidebar.number_input("Seguros (%)", min_value=0.0, max_value=100.0, value=2.0, step=0.1, format="%.1f")
    impuestos_pct = st.sidebar.number_input("Impuestos (%)", min_value=0.0, max_value=100.0, value=1.0, step=0.1, format="%.1f")

    # Aproximación de CFT efectivo agregado por período (suma simple de % adicionales)
    # Nota: para rigor, CFT debería componerse según estructura de cobro; aquí simplificamos.
    cft_aprox = tea + (gastos_pct + seguros_pct + impuestos_pct)/100.0

    st.write(pd.DataFrame({
        "Magnitud": ["TNA (base m)", "TEA (m)", "CFT aprox."],
        "Valor": [tna, tea, cft_aprox],
        "Valor (%)": [tna*100, tea*100, cft_aprox*100]
    }))

    fig, ax = plt.subplots()
    ax.plot([0,1], [tna*100, tna*100], label="TNA (%)")
    ax.plot([0,1], [tea*100, tea*100], label="TEA (%)")
    ax.plot([0,1], [cft_aprox*100, cft_aprox*100], label="CFT aprox. (%)")
    ax.set_xlabel("Escala comparativa"); ax.set_ylabel("Tasa (%)"); ax.legend()
    st.pyplot(fig)

    st.caption("Nota: El CFT real depende de cómo se cobren gastos/seguros/impuestos (monto fijo, sobre saldo, por fuera de cuota, etc.).")

elif modulo == "Precanc. y recálculo (consumo/hipoteca)":
    st.subheader("Precacelación y recálculo de préstamo (mantener cuota o plazo)")
    P = st.sidebar.number_input("Principal inicial (P)", min_value=0.0, value=1000000.0, step=10000.0, format="%.2f")
    i, i_pct = tasa_input("Tasa por período (i)", default_decimal=0.02)
    n = st.sidebar.number_input("Plazo original (n)", min_value=1, max_value=360, value=60, step=1)
    t = st.sidebar.number_input("Período de prepago (t)", min_value=1, max_value=360, value=18, step=1)
    prepago = st.sidebar.number_input("Monto de prepago", min_value=0.0, value=200000.0, step=10000.0, format="%.2f")

    # Cronograma hasta t
    df = tabla_frances(P, i, n)
    saldo_t = float(df.loc[df["Periodo"]==t, "Saldo Final"])
    saldo_nuevo = max(saldo_t - prepago, 0.0)
    A_original = cuota_frances(P, i, n)

    # Opción A: mantener cuota, reducir plazo
    if saldo_nuevo > 0 and A_original > 0:
        # encontrar n' tal que cuota(A_original) con saldo_nuevo e i
        n_reducido = None
        for nn in range(1, 361):
            A_try = cuota_frances(saldo_nuevo, i, nn)
            if A_try <= A_original + 0.01:
                n_reducido = nn
                break
    else:
        n_reducido = 0

    # Opción B: mantener plazo restante (n-t), recalcular nueva cuota
    plazo_restante = max(n - t, 0)
    A_nueva = cuota_frances(saldo_nuevo, i, plazo_restante) if plazo_restante>0 else 0.0

    st.write(pd.DataFrame({
        "Escenario": ["Original","Tras prepago"],
        "Saldo al t": [saldo_t, saldo_nuevo],
        "Cuota (original)": [A_original, A_original],
        "Nueva cuota (mantener plazo)": [None, A_nueva],
        "Nuevo plazo (mantener cuota)": [None, n_reducido]
    }))

    fig, ax = plt.subplots()
    ax.plot(df["Periodo"], df["Saldo Final"], label="Saldo original")
    # recomputar serie nueva si mantenés plazo
    if plazo_restante>0:
        df_new = tabla_frances(saldo_nuevo, i, plazo_restante)
        df_new["Periodo"] = df_new["Periodo"] + t
        ax.plot(df_new["Periodo"], df_new["Saldo Final"], label="Saldo tras prepago (mantener plazo)")
    ax.set_xlabel("Periodo"); ax.set_ylabel("Saldo"); ax.legend()
    st.pyplot(fig)
    st.caption("En consumo/hipoteca suele reconocerse descuento de intereses no devengados. La implementación busca efectos prácticos de reconfigurar el plan.")

elif modulo == "Imputación de pagos parciales":
    st.subheader("Imputación de pagos parciales (interés → capital)")
    C = st.sidebar.number_input("Capital base (C)", min_value=0.0, value=500000.0, step=1000.0, format="%.2f")
    i, i_pct = tasa_input("Tasa por período (i)", default_decimal=0.03)
    n = st.sidebar.number_input("Períodos transcurridos (n)", min_value=1, max_value=360, value=12, step=1)
    pago = st.sidebar.number_input("Pago parcial aplicado", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")

    # Interés devengado simple en n períodos (modelo pericial básico)
    interes_dev = C * i * n
    # Imputación: primero intereses, luego capital (regla usual salvo pacto distinto)
    imput_a_interes = min(pago, interes_dev)
    imput_a_capital = max(pago - interes_dev, 0.0)
    capital_remanente = max(C - imput_a_capital, 0.0)
    interes_remanente = max(interes_dev - imput_a_interes, 0.0)

    st.write(pd.DataFrame({
        "Concepto": ["Interés devengado", "Pago aplicado a interés", "Pago aplicado a capital", "Interés remanente", "Capital remanente"],
        "Monto": [interes_dev, imput_a_interes, imput_a_capital, interes_remanente, capital_remanente]
    }))
    st.caption("Base simple: I = C · i · n. Ajuste el modelo según norma/fallo (p. ej., tasa judicial, prorrateo por días, etc.).")

    fig, ax = plt.subplots()
    ax.plot([0,1,2], [C, capital_remanente, capital_remanente], label="Capital (antes↘después)")
    ax.set_xlabel("Etapas"); ax.set_ylabel("Monto"); ax.legend()
    st.pyplot(fig)

elif modulo == "Actualización + tasa pura (simulación)":
    st.subheader("Actualización por índice + tasa pura simple")
    C = st.sidebar.number_input("Capital base (C)", min_value=0.0, value=300000.0, step=1000.0, format="%.2f")
    n = st.sidebar.number_input("Número de períodos (n)", min_value=1, max_value=360, value=12, step=1)
    # índice multiplicativo (ej., 1.50 significa 50% de actualización total en n períodos)
    indice = st.sidebar.number_input("Índice acumulado (multiplicativo)", min_value=0.0, value=1.50, step=0.01, format="%.2f")
    i_pura, i_pura_pct = tasa_input("Tasa pura simple por período", default_decimal=0.01)

    capital_actualizado = C * indice
    interes_puro = capital_actualizado * i_pura * n
    total = capital_actualizado + interes_puro

    st.write(pd.DataFrame({
        "Concepto": ["Capital base", "Índice acumulado", "Capital actualizado", "Interés puro", "Total"],
        "Valor": [C, indice, capital_actualizado, interes_puro, total]
    }))
    st.caption("Modelo didáctico: primero actualizar capital (deuda de valor), luego aplicar tasa pura simple. Ajuste según fuero/criterio vigente.")

    fig, ax = plt.subplots()
    ax.plot([0,1,2], [C, capital_actualizado, total], label="Evolución (base→actualizado→+interés puro)")
    ax.set_xlabel("Etapas"); ax.set_ylabel("Monto"); ax.legend()
    st.pyplot(fig)

st.markdown("""
---
### 📌 Nota jurídica
- **CCyC 768 / 770 / 772**: tasas desde mora; límites al anatocismo; deudas de valor.
- **Transparencia (BCRA, LDC)**: TEA/CFT, cronogramas y costos informados.
> Adapte método/tasa a la norma o fallo aplicable. Este recurso es didáctico y no sustituye pericia contable/actuarial.
""")
