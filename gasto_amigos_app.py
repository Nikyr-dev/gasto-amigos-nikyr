
import streamlit as st
import pandas as pd
import os
import datetime
import json

st.set_page_config(page_title="Gasto Justo – By NIKY’R")

st.markdown(
    '''
    <style>
    html, body, [class*="css"]  {
        font-family: Verdana;
    }
    </style>
    ''',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <h1 style='text-align: center; color: #ffc107; font-size: 42px;'>
        💸 Gasto Justo – <span style='color:#FF5252;'>By NIKY’R</span> 🧾
    </h1>
    """,
    unsafe_allow_html=True
)

participantes = ["Rama", "Nacho", "Marce"]
archivo = "gastos.csv"
columnas = ["fecha", "descripcion", "monto", "pagador", "participantes"]

if os.path.exists(archivo):
    try:
        gastos_df = pd.read_csv(archivo)
        if all(col in gastos_df.columns for col in columnas):
            gastos_df["participantes"] = gastos_df["participantes"].apply(json.loads)
        else:
            gastos_df = pd.DataFrame(columns=columnas)
    except Exception:
        gastos_df = pd.DataFrame(columns=columnas)
else:
    gastos_df = pd.DataFrame(columns=columnas)

st.subheader("Registrar nuevo gasto")
descripcion = st.text_input("¿Qué se compró?")
monto = st.number_input("¿Cuánto costó?", min_value=0.0, step=0.5)
pagador = st.selectbox("¿Quién pagó?", participantes)
involucrados = st.multiselect("¿Quiénes participaron?", participantes, default=participantes)
fecha = st.date_input("Fecha del gasto", datetime.date.today())

if st.button("Agregar gasto"):
    nuevo = pd.DataFrame([{
        "fecha": fecha.strftime("%d-%b"),
        "descripcion": descripcion,
        "monto": monto,
        "pagador": pagador,
        "participantes": json.dumps(involucrados)
    }])
    gastos_df = pd.concat([gastos_df, nuevo], ignore_index=True)
    gastos_df.to_csv(archivo, index=False)
    st.success("✅ Gasto guardado correctamente.")

st.subheader("Historial de gastos")
if not gastos_df.empty:
    for _, row in gastos_df.iterrows():
        try:
            participantes_data = row["participantes"]
            if isinstance(participantes_data, str):
                participantes_data = json.loads(participantes_data)
            participantes_str = ", ".join(participantes_data)
        except Exception:
            participantes_str = "???"
        st.write(f"{row['fecha']} | {row['descripcion']} | ${row['monto']} – pagó {row['pagador']} | participaron: {participantes_str}")
else:
    st.info("No hay gastos registrados aún.")

st.subheader("Resumen de la semana")
if not gastos_df.empty:
    saldos = {nombre: 0 for nombre in participantes}
    for _, row in gastos_df.iterrows():
        monto = float(row["monto"])
        pagador = row["pagador"]
        quienes = row["participantes"]
        if isinstance(quienes, str):
            quienes = json.loads(quienes)
        dividido = monto / len(quienes)
        for persona in quienes:
            saldos[persona] -= dividido
        saldos[pagador] += monto

    total = gastos_df["monto"].sum()
    st.markdown(f"**Total gastado:** ${total:.2f}")

    for nombre, saldo in saldos.items():
        if saldo > 0:
            st.success(f"✅ {nombre} puso ${saldo:.2f} de más")
        elif saldo < 0:
            st.warning(f"⚠️ {nombre} debe ${abs(saldo):.2f}")
        else:
            st.info(f"{nombre} está justo")

if st.button("🧹 Reiniciar semana"):
    gastos_df = pd.DataFrame(columns=columnas)
    gastos_df.to_csv(archivo, index=False)
    st.success("Todos los gastos fueron borrados.")
