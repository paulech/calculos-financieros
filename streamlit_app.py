
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="MatFin – Derecho Bancario", layout="wide")

# ======= Encabezado / Ayuda rápida
st.markdown("### Calculadora Interactiva — Matemática Financiera (Derecho Bancario)")
st.caption("Navegación por **pestañas**; inputs en **formularios**; compatible con escritorio y celular.")

# ======= Preferencias globales
st.sidebar.header("Preferencias")
modo = st.sidebar.radio("Formato de tasa", ["Decimal (0.2)", "Porcentaje (20)"], horizontal=False)

def tasa_input_ui(container, label, default_decimal=0.10):
    """Devuelve (tasa_decimal, tasa_%). Muestra input según el modo elegido."""
    if modo == "Decimal (0.2)":
        i = container.number_input(f"{label} (decimal)", min_value=0.0, max_value=1.0, value=float(default_decimal), step=0.005, format="%.3f")
        return i, i*100.0
    else:
        i_pct = container.number_input(f"{label} (%)", min_value=0.0, max_value=100.0, value=float(default_decimal*100.0), step=0.1, format="%.1f")
        return i_pct/100.0, i_pct

# ======= Cache: utilidades
@st.cache_data
def cuota_frances(P, i, n):
    if n == 0 or i == 0:
        return P / n if n else 0.0
    return P * (i * (1 + i)**n) / ((1 + i)**n - 1)

@st.cache_data
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

@st.cache_data
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

@st.cache_data
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

def df_download_button(df, filename, label="Descargar CSV"):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(label=label, data=csv, file_name=filename, mime="text/csv")

# ======= Tabs: navegación
tabs = st.tabs([
    "Simple/Compuesto",
    "Descuento",
    "Amortización",
    "TNA↔TEA/CFT",
    "Precanc.",
    "Imputación",
    "Actualización"
])

# ---- Tab 1: Simple/Compuesto
with tabs[0]:
    with st.expander("Parámetros", expanded=True):
        with st.form("form_simple_comp"):
            C = st.number_input("Capital (C)", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
            i, i_pct = tasa_input_ui(st, "Tasa por período (i)", default_decimal=0.10)
            n = st.number_input("Número de períodos (n)", min_value=1, max_value=360, value=12, step=1)
            submit = st.form_submit_button("Calcular")
    if submit:
        I_s = C * i * n
        VF_s = C + I_s
        VF_c = C * (1 + i)**n
        I_c = VF_c - C

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Interés simple", f"{I_s:,.2f}")
        c2.metric("VF simple", f"{VF_s:,.2f}")
        c3.metric("Interés compuesto", f"{I_c:,.2f}")
        c4.metric("VF compuesto", f"{VF_c:,.2f}")
        st.caption(f"Tasa usada: {i_pct:.2f}% por período")

        xs = np.arange(0, int(n)+1)
        vf_simple = C * (1 + i*xs)
        vf_comp = C * (1 + i)**xs
        fig, ax = plt.subplots()
        ax.plot(xs, vf_simple, label="Simple")
        ax.plot(xs, vf_comp, label="Compuesto")
        ax.set_xlabel("Períodos"); ax.set_ylabel("Monto"); ax.legend()
        st.pyplot(fig)

# ---- Tab 2: Descuento
with tabs[1]:
    with st.expander("Parámetros", expanded=True):
        with st.form("form_descuento"):
            i, i_pct = tasa_input_ui(st, "Tasa de interés por período (i)", default_decimal=0.10)
            VF = st.number_input("Valor Futuro (VF)", min_value=0.0, value=110000.0, step=1000.0, format="%.2f")
            n = st.number_input("Número de períodos (n)", min_value=1, max_value=360, value=2, step=1)
            d_s, d_s_pct = tasa_input_ui(st, "Tasa descuento simple (d_s)", default_decimal=0.10)
            submit_d = st.form_submit_button("Calcular")
    if submit_d:
        d = i / (1 + i) if (1+i)!=0 else 0
        i_rec = d / (1 - d) if d < 1 else float('nan')
        vp_r = VF / (1 + i)**n
        vp_c = VF * (1 - d_s*n)
        df = pd.DataFrame({
            "Magnitud": ["d equivalente a i", "i desde d", "VP racional compuesto", "VP comercial simple (si d_s·n<1)"],
            "Valor": [d, i_rec, vp_r, vp_c]
        })
        st.dataframe(df, use_container_width=True)
        df_download_button(df, "descuento_resultados.csv")
        st.caption(f"i = {i_pct:.2f}% por período | d_s = {d_s_pct:.2f}% simple por período")

# ---- Tab 3: Amortización
with tabs[2]:
    with st.expander("Parámetros", expanded=True):
        with st.form("form_amort"):
            sistema = st.selectbox("Sistema", ["Francés","Alemán","Americano"])
            P = st.number_input("Principal (P)", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
            i, i_pct = tasa_input_ui(st, "Tasa por período (i)", default_decimal=0.02)
            n = st.number_input("Número de períodos (n)", min_value=1, max_value=360, value=12, step=1)
            submit_a = st.form_submit_button("Calcular")
    if submit_a:
        if sistema == "Francés":
            df = tabla_frances(P, i, n)
        elif sistema == "Alemán":
            df = tabla_aleman(P, i, n)
        else:
            df = tabla_americano(P, i, n)

        st.dataframe(df, use_container_width=True, height=380)
        df_download_button(df, f"cronograma_{sistema.lower()}.csv")
        st.caption(f"Tasa usada: {i_pct:.3f}% por período")

        fig, ax = plt.subplots()
        if sistema in ("Francés","Alemán"):
            ax.plot(df["Periodo"], df["Interés"], label="Interés")
            ax.plot(df["Periodo"], df["Amortización"], label="Amortización")
        else:
            ax.plot(df["Periodo"], df["Cuota"], label="Cuota")
        ax.set_xlabel("Periodo"); ax.set_ylabel("Monto"); ax.legend()
        st.pyplot(fig)

# ---- Tab 4: TNA↔TEA/CFT
with tabs[3]:
    with st.expander("Parámetros", expanded=True):
        with st.form("form_tasas"):
            base = st.selectbox("Base de capitalización m (por año)", [1,2,4,12,365], index=3)
            tipo = st.selectbox("Ingresar", ["TNA", "TEA"])
            if tipo == "TNA":
                tna, tna_pct = tasa_input_ui(st, "TNA", default_decimal=0.60)
                tea = tna_to_tea(tna, base)
            else:
                tea, tea_pct = tasa_input_ui(st, "TEA", default_decimal=0.796)
                tna = tea_to_tna(tea, base)
            gastos_pct = st.number_input("Gastos administrativos (%)", min_value=0.0, max_value=100.0, value=3.0, step=0.1, format="%.1f")
            seguros_pct = st.number_input("Seguros (%)", min_value=0.0, max_value=100.0, value=2.0, step=0.1, format="%.1f")
            impuestos_pct = st.number_input("Impuestos (%)", min_value=0.0, max_value=100.0, value=1.0, step=0.1, format="%.1f")
            submit_t = st.form_submit_button("Calcular")
    if submit_t:
        cft_aprox = tea + (gastos_pct + seguros_pct + impuestos_pct)/100.0
        df = pd.DataFrame({
            "Magnitud": ["TNA (base m)", "TEA (m)", "CFT aprox."],
            "Valor": [tna, tea, cft_aprox],
            "Valor (%)": [tna*100, tea*100, cft_aprox*100]
        })
        st.dataframe(df, use_container_width=True)
        df_download_button(df, "tasas_cft.csv")

        fig, ax = plt.subplots()
        ax.plot([0,1], [tna*100, tna*100], label="TNA (%)")
        ax.plot([0,1], [tea*100, tea*100], label="TEA (%)")
        ax.plot([0,1], [cft_aprox*100, cft_aprox*100], label="CFT aprox. (%)")
        ax.set_xlabel("Escala comparativa"); ax.set_ylabel("Tasa (%)"); ax.legend()
        st.pyplot(fig)
        st.caption("El CFT real depende de cómo se cobren gastos/seguros/impuestos (sobre saldo, monto fijo, por fuera de cuota, etc.).")

# ---- Tab 5: Precanc.
with tabs[4]:
    with st.expander("Parámetros", expanded=True):
        with st.form("form_precanc"):
            P = st.number_input("Principal inicial (P)", min_value=0.0, value=1000000.0, step=10000.0, format="%.2f")
            i, i_pct = tasa_input_ui(st, "Tasa por período (i)", default_decimal=0.02)
            n = st.number_input("Plazo original (n)", min_value=1, max_value=360, value=60, step=1)
            t = st.number_input("Período de prepago (t)", min_value=1, max_value=360, value=18, step=1)
            prepago = st.number_input("Monto de prepago", min_value=0.0, value=200000.0, step=10000.0, format="%.2f")
            submit_p = st.form_submit_button("Calcular")
    if submit_p:
        df_o = tabla_frances(P, i, n)
        saldo_t = float(df_o.loc[df_o["Periodo"]==t, "Saldo Final"])
        saldo_nuevo = max(saldo_t - prepago, 0.0)
        A_original = cuota_frances(P, i, n)

        # Mantener cuota -> reducir plazo (búsqueda discreta simple)
        n_reducido = 0
        if saldo_nuevo > 0 and A_original > 0:
            for nn in range(1, 361):
                A_try = cuota_frances(saldo_nuevo, i, nn)
                if A_try <= A_original + 0.01:
                    n_reducido = nn
                    break

        plazo_restante = max(n - t, 0)
        A_nueva = cuota_frances(saldo_nuevo, i, plazo_restante) if plazo_restante>0 else 0.0

        df_res = pd.DataFrame({
            "Escenario": ["Original","Tras prepago"],
            "Saldo al t": [saldo_t, saldo_nuevo],
            "Cuota (original)": [A_original, A_original],
            "Nueva cuota (mantener plazo)": [None, A_nueva],
            "Nuevo plazo (mantener cuota)": [None, n_reducido]
        })
        st.dataframe(df_res, use_container_width=True)
        df_download_button(df_res, "precancelacion_resultados.csv")

        fig, ax = plt.subplots()
        ax.plot(df_o["Periodo"], df_o["Saldo Final"], label="Saldo original")
        if plazo_restante>0:
            df_new = tabla_frances(saldo_nuevo, i, plazo_restante)
            df_new["Periodo"] = df_new["Periodo"] + t
            ax.plot(df_new["Periodo"], df_new["Saldo Final"], label="Saldo tras prepago (mantener plazo)")
        ax.set_xlabel("Periodo"); ax.set_ylabel("Saldo"); ax.legend()
        st.pyplot(fig)
        st.caption("Reconoce descuento de intereses no devengados; recálculo didáctico para negociación.")

# ---- Tab 6: Imputación
with tabs[5]:
    with st.expander("Parámetros", expanded=True):
        with st.form("form_imputacion"):
            C = st.number_input("Capital base (C)", min_value=0.0, value=500000.0, step=1000.0, format="%.2f")
            i, i_pct = tasa_input_ui(st, "Tasa por período (i)", default_decimal=0.03)
            n = st.number_input("Períodos transcurridos (n)", min_value=1, max_value=360, value=12, step=1)
            pago = st.number_input("Pago parcial aplicado", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
            submit_i = st.form_submit_button("Calcular")
    if submit_i:
        interes_dev = C * i * n
        imput_a_interes = min(pago, interes_dev)
        imput_a_capital = max(pago - interes_dev, 0.0)
        capital_remanente = max(C - imput_a_capital, 0.0)
        interes_remanente = max(interes_dev - imput_a_interes, 0.0)

        df = pd.DataFrame({
            "Concepto": ["Interés devengado", "Pago a interés", "Pago a capital", "Interés remanente", "Capital remanente"],
            "Monto": [interes_dev, imput_a_interes, imput_a_capital, interes_remanente, capital_remanente]
        })
        st.dataframe(df, use_container_width=True)
        df_download_button(df, "imputacion_resultados.csv")

        fig, ax = plt.subplots()
        ax.plot([0,1,2], [C, capital_remanente, capital_remanente], label="Capital (antes→después)")
        ax.set_xlabel("Etapas"); ax.set_ylabel("Monto"); ax.legend()
        st.pyplot(fig)
        st.caption("I = C · i · n (simple). Ajuste según norma/fallo: tasa judicial, prorrateo por días, etc.")

# ---- Tab 7: Actualización
with tabs[6]:
    with st.expander("Parámetros", expanded=True):
        with st.form("form_actualizacion"):
            C = st.number_input("Capital base (C)", min_value=0.0, value=300000.0, step=1000.0, format="%.2f")
            n = st.number_input("Número de períodos (n)", min_value=1, max_value=360, value=12, step=1)
            indice = st.number_input("Índice acumulado (multiplicativo)", min_value=0.0, value=1.50, step=0.01, format="%.2f")
            i_pura, i_pura_pct = tasa_input_ui(st, "Tasa pura simple por período", default_decimal=0.01)
            submit_u = st.form_submit_button("Calcular")
    if submit_u:
        capital_actualizado = C * indice
        interes_puro = capital_actualizado * i_pura * n
        total = capital_actualizado + interes_puro
        df = pd.DataFrame({
            "Concepto": ["Capital base", "Índice acumulado", "Capital actualizado", "Interés puro", "Total"],
            "Valor": [C, indice, capital_actualizado, interes_puro, total]
        })
        st.dataframe(df, use_container_width=True)
        df_download_button(df, "actualizacion_resultados.csv")

        fig, ax = plt.subplots()
        ax.plot([0,1,2], [C, capital_actualizado, total], label="Evolución (base→actualizado→+interés)")
        ax.set_xlabel("Etapas"); ax.set_ylabel("Monto"); ax.legend()
        st.pyplot(fig)

st.markdown("""
---
**📌 Nota jurídica**  
- **CCyC 768 / 770 / 772**: tasas desde mora; límites al anatocismo; deudas de valor.  
- **Transparencia (BCRA, LDC)**: TEA/CFT, cronogramas y costos informados.  
> Adapte método/tasa al texto normativo o criterio jurisprudencial aplicable. Este recurso es didáctico y no sustituye pericia contable/actuarial.
""")
