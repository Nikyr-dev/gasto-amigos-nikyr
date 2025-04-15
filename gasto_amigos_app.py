import streamlit as st
import pandas as pd
import os
import datetime

# Título con íconos
st.markdown(
    """
    <h1 style='text-align: center; color: #ffc107; font-size: 42px;'>
        💸 Gasto Justo – <span style='color:#FF5252;'>By NIKY’R</span> 😢
    </h1>
    """,
    unsafe_allow_html=True
)

# Participantes fijos por ahora
participantes = ["Rama", "Nacho", "Marce"]

# Nombre del archivo CSV
archivo = "gastos.csv"

# Cargar gastos desde el archivo si existe
if os.path.exists(archivo):
    gastos_df = pd.read_csv(archivo)
else:
    gastos_df = pd.DataFrame(columns=["fecha", "descripcion", "monto", "pagador"])

# Formulario para agregar gasto
st.subheader("Registrar nuevo gasto")
descripcion = st.text_input("¿Qué se compró?")
monto = st.number_input("¿Cuánto costó?", min_value=0.0, step=0.5)
pagador = st.selectbox("¿Quién pagó?", participantes)
fecha = st.date_input("Fecha del gasto", datetime.date.today())

if st.button("Agregar gasto"):
    nuevo = pd.DataFrame([{
        "fecha": fecha,
        "descripcion": descripcion,
        "monto": monto,
        "pagador": pagador
    }])
    gastos_df = pd.concat([gastos_df, nuevo], ignore_index=True)
    gastos_df.to_csv(archivo, index=False)
    st.success("✅ Gasto guardado correctamente.")

# Mostrar historial
st.subheader("Historial de gastos")
if not gastos_df.empty:
    for i, row in gastos_df.iterrows():
        st.markdown(f"- {row['fecha']} | **{row['descripcion']}** | ${row['monto']} – pagó *{row['pagador']}*")
else:
    st.info("No hay gastos registrados aún.")

# Cálculo de balances
st.subheader("Resumen de la semana")
if not gastos_df.empty:
    total = gastos_df["monto"].sum()
    promedio = total / len(participantes)

    pagado_por = gastos_df.groupby("pagador")["monto"].sum().to_dict()

    st.markdown(f"**Total gastado:**

