
# MatFin – Derecho Bancario (Streamlit)

Calculadora interactiva de **matemática financiera aplicada al derecho bancario**. Optimizada para **escritorio y celular**.

## ✨ Características de UX
- **Pestañas (tabs)** para navegar entre módulos.
- **Inputs en formularios** con botón **Calcular** (mejor rendimiento en móvil).
- **Selector de formato de tasa** como **radio** (decimal o %).
- **Parámetros en "expanders"** ordenados y plegables.
- **Métricas (`st.metric`)** en columnas responsivas.
- **Descarga CSV** de todos los resultados tabulares.
- **Cache de cálculos** (`st.cache_data`) para fluidez.
- Gráficos con **matplotlib** (sin estilos de color específicos).

## 🧮 Módulos
1. **Simple/Compuesto**: VF, interés simple vs. compuesto con gráfico.
2. **Descuento**: i↔d, VP racional compuesto y comercial simple.
3. **Amortización**: Francés, Alemán y Americano (cronograma + gráfico).
4. **TNA↔TEA/CFT**: conversión y CFT aproximado con gastos/seguros/impuestos.
5. **Precanc.**: prepago con dos escenarios (mantener cuota o mantener plazo).
6. **Imputación**: reparto de pago parcial entre interés y capital.
7. **Actualización**: índice multiplicativo + tasa pura simple.

> **Nota jurídica**: Ver al pie de la app (CCyC 768/770/772; transparencia BCRA/LDC). Ajuste método y tasa a la norma/fallo aplicable.

## 🚀 Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## ☁️ Deploy en Streamlit Cloud
1. Crear un repo con:
   - `streamlit_app.py`
   - `requirements.txt`
   - `README.md`
2. Desde https://streamlit.io/cloud, conectar el repo y desplegar.

## 🧾 Formato de tasas
- Elegí **Decimal (0.2)** o **Porcentaje (20)** desde la barra lateral.
- Internamente se usan decimales para los cálculos.

## 📂 Estructura
```
streamlit_app.py
requirements.txt
README.md
```

## ⚠️ Descargo didáctico
Este recurso es **educativo** y no sustituye informes periciales contables/actuariales ni asesoramiento profesional específico.
