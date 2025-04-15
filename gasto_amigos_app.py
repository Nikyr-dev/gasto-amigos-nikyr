import streamlit as st
import pandas as pd
import os
import datetime
import json

st.set_page_config(page_title="Gasto Justo – By NIKY’R")

# Fuente global: Verdana
st.markdown(
    """
    <style>
        * {
            font-family: Verdana, sans-serif !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Título con íconos
st.markdown(
    """
    <div style='text-align: center;'>
        <h1 style='color: #ffc107; font-size: 40px; margin-top: 10px;'>
            💸 Gasto Justo – <span style='color:#FF5252;'>By NIKY’R</span>
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Participantes por defecto
participantes = ["Rama", "Nacho", "Marce"]
archivo = "gastos.csv"

# Cargar historial si existe
if os.path.exists(archivo):
    gastos_df = pd.read_csv(archivo)
    gastos_df["participantes"] = gastos_df["participantes"].apply(json.loads)
else:
    gastos_df = pd.DataFrame(columns=["fecha", "descripcion", "monto", "pagador", "participantes"])

# Registrar nuevo gasto
st.subheader("Registrar nuevo gasto")

descripcion = st.text_input("¿Qué se compró?")
monto = st.number_input("¿Cuánto costó?", min_value=0.0, step=0.5)
pagador = st.selectbox("¿Quién pagó?", participantes)
involucrados = st.multiselect("¿Quiénes participaron?", participantes)
fecha = st.date_input("Fecha del gasto", datetime.date.today())

if st.button("Agregar gasto"):
    if not involucrados:
        st.warning("Seleccioná al menos una persona que participó del gasto.")
    else:
        nuevo = pd.DataFrame([{
            "fecha": str(fecha),
            "descripcion": descripcion,
            "monto": monto,
            "pagador": pagador,
            "participantes": json.dumps(involucrados)
        }])
        gastos_df = pd.concat([gastos_df, nuevo], ignore_index=True)
        gastos_df.to_csv(archivo, index=False)
        st.success("✅ Gasto agregado correctamente.")

# Historial de gastos
st.subheader("Historial de gastos")
if not gastos_df.empty:
    for _, row in gastos_df.iterrows():
        fecha_formateada = pd.to_datetime(row["fecha"]).strftime("%d-%b").lower()
        participantes_str = ", ".join(row["participantes"])
        st.write(f"{fecha_formateada} | {row['descripcion']} | ${row['monto']} – pagó {row['pagador']} | participaron: {participantes_str}")
else:
    st.info("No hay gastos registrados aún.")

# Cálculo de balances
st.subheader("Resumen en tiempo real 🧮")
if not gastos_df.empty:
    balances = {p: 0 for p in participantes}
    aportes = {p: 0 for p in participantes}
    total = 0

    for _, row in gastos_df.iterrows():
        monto = float(row["monto"])
        pagador = row["pagador"]
        involucrados = row["participantes"]
        if isinstance(involucrados, str):
            involucrados = json.loads(involucrados)
        division = monto / len(involucrados)
        total += monto

        aportes[pagador] += monto
        for persona in involucrados:
            balances[persona] += division

    st.markdown(f"🧾 **Total gastado hasta hoy:** ${total:.2f}")

    st.markdown("### 💸 Balance individual:")
    for p in participantes:
        diferencia = aportes[p] - balances[p]
        if diferencia > 0:
            st.success(f"✅ {p} puso ${diferencia:.2f} de más")
        elif diferencia < 0:
            st.warning(f"⚠️ {p} debe ${abs(diferencia):.2f}")
        else:
            st.info(f"{p} está justo")

# Reiniciar semana
if st.button("🧹 Reiniciar semana"):
    gastos_df = pd.DataFrame(columns=["fecha", "descripcion", "monto", "pagador", "participantes"])
    gastos_df.to_csv(archivo, index=False)
    st.success("Todos los gastos fueron borrados.")
