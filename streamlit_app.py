
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="MatFin – Derecho Bancario", layout="wide")

st.title("Calculadora Interactiva – Matemática Financiera (Derecho Bancario)")

st.sidebar.header("Parámetros generales")
modulo = st.sidebar.selectbox("Módulo",
                              ["Interés simple/compuesto",
                               "Descuento y equivalencias",
                               "Amortización: Francés/Alemán/Americano"])

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

if modulo == "Interés simple/compuesto":
    C = st.sidebar.number_input("Capital (C)", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
    i = st.sidebar.number_input("Tasa por período (i)", min_value=0.0, max_value=1.0, value=0.10, step=0.005, format="%.3f")
    n = st.sidebar.number_input("Número de períodos (n)", min_value=1, max_value=360, value=12, step=1)

    # simple
    I_s = C * i * n
    VF_s = C + I_s

    # compuesto
    VF_c = C * (1 + i)**n
    I_c = VF_c - C

    st.subheader("Resultados")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Interés simple total**")
        st.write(I_s)
        st.markdown("**VF simple**")
        st.write(VF_s)
    with col2:
        st.markdown("**Interés compuesto total**")
        st.write(I_c)
        st.markdown("**VF compuesto**")
        st.write(VF_c)

    xs = np.arange(0, int(n)+1)
    vf_simple = C * (1 + i*xs)
    vf_comp = C * (1 + i)**xs
    fig, ax = plt.subplots()
    ax.plot(xs, vf_simple, label="Simple")
    ax.plot(xs, vf_comp, label="Compuesto")
    ax.set_xlabel("Períodos")
    ax.set_ylabel("Monto")
    ax.legend()
    st.pyplot(fig)

elif modulo == "Descuento y equivalencias":
    i = st.sidebar.number_input("Tasa de interés por período (i)", min_value=0.0, max_value=1.0, value=0.10, step=0.005, format="%.3f")
    VF = st.sidebar.number_input("Valor Futuro (VF)", min_value=0.0, value=110000.0, step=1000.0, format="%.2f")
    n = st.sidebar.number_input("Número de períodos (n)", min_value=1, max_value=360, value=2, step=1)
    d_s = st.sidebar.number_input("Tasa descuento simple (d_s)", min_value=0.0, max_value=1.0, value=0.10, step=0.005, format="%.3f")

    d = i / (1 + i) if (1+i)!=0 else 0
    i_rec = d / (1 - d) if d < 1 else float('nan')
    vp_r = VF / (1 + i)**n
    vp_c = VF * (1 - d_s*n)

    st.subheader("Resultados")
    st.write(pd.DataFrame({
        "Magnitud": ["d equivalente a i", "i recuperada desde d", "VP racional compuesto", "VP comercial simple (si d_s·n<1)"],
        "Valor": [d, i_rec, vp_r, vp_c]
    }))

else:
    sistema = st.sidebar.selectbox("Sistema", ["Francés","Alemán","Americano"])
    P = st.sidebar.number_input("Principal (P)", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
    i = st.sidebar.number_input("Tasa por período (i)", min_value=0.0, max_value=1.0, value=0.02, step=0.001, format="%.3f")
    n = st.sidebar.number_input("Número de períodos (n)", min_value=1, max_value=360, value=12, step=1)

    if sistema == "Francés":
        df = tabla_frances(P, i, n)
    elif sistema == "Alemán":
        df = tabla_aleman(P, i, n)
    else:
        df = tabla_americano(P, i, n)

    st.subheader("Cronograma")
    st.dataframe(df)

    fig, ax = plt.subplots()
    if sistema in ("Francés","Alemán"):
        ax.plot(df["Periodo"], df["Interés"], label="Interés")
        ax.plot(df["Periodo"], df["Amortización"], label="Amortización")
        ax.set_xlabel("Periodo"); ax.set_ylabel("Monto"); ax.legend()
    else:
        ax.plot(df["Periodo"], df["Cuota"], label="Cuota")
        ax.set_xlabel("Periodo"); ax.set_ylabel("Monto"); ax.legend()
    st.pyplot(fig)

st.markdown("""
---
### 📌 Nota jurídica
- **CCyC 768 / 770 / 772**: tasas desde mora; límites al anatocismo; deudas de valor.
- **Transparencia (BCRA, LDC)**: TEA/CFT y cronogramas claros.
> Use el método/tasa que dispongan la norma o el fallo aplicable.
""")
