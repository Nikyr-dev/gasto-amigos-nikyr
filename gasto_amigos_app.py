import streamlit as st
import pandas as pd
import os
import datetime
import json

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

columnas = ["fecha", "descripcion", "monto", "pagador", "involucrados"]

# Cargar gastos desde el archivo si existe
if os.path.exists(archivo):
    try:
        gastos_df = pd.read_csv(archivo)
        if "involucrados" in gastos_df.columns:
            gastos_df["involucrados"] = gastos_df["involucrados"].apply(json.loads)
        else:
            gastos_df = pd.DataFrame(columns=columnas)
    except Exception:
        gastos_df = pd.DataFrame(columns=columnas)
else:
    gastos_df = pd.DataFrame(columns=columnas)

# Formulario para agregar gasto
st.subheader("Registrar nuevo gasto")
descripcion = st.text_input("¿Qué se compró?")
monto = st.number_input("¿Cuánto costó?", min_value=0.0, step=0.5)
pagador = st.selectbox("¿Quién pagó?", participantes)
involucrados = st.multiselect("¿Quiénes participaron en el gasto?", participantes, default=participantes)
fecha = st.date_input("Fecha del gasto", datetime.date.today())

if st.button("Agregar gasto"):
    if not involucrados:
        st.warning("Debe haber al menos un involucrado.")
    else:
        nuevo = pd.DataFrame([{
            "fecha": str(fecha),
            "descripcion": descripcion,
            "monto": monto,
            "pagador": pagador,
            "involucrados": json.dumps(involucrados)
        }])
        gastos_df = pd.concat([gastos_df, nuevo], ignore_index=True)
        gastos_df.to_csv(archivo, index=False)
        st.success("✅ Gasto guardado correctamente.")

# Mostrar historial
st.subheader("Historial de gastos")
if not gastos_df.empty:
    for _, row in gastos_df.iterrows():
        involucrados = row["involucrados"] if isinstance(row["involucrados"], list) else json.loads(row["involucrados"])
        involucrados_str = ", ".join(involucrados)
        st.markdown(f"- {row['fecha']} | **{row['descripcion']}** | ${row['monto']} – pagó *{row['pagador']}* | participaron: {involucrados_str}")
else:
    st.info("No hay gastos registrados aún.")

# Cálculo de balances
st.subheader("Resumen de la semana")
if not gastos_df.empty:
    total = 0
    balance_individual = {p: 0 for p in participantes}
    pagado_por = {p: 0 for p in participantes}

    for _, row in gastos_df.iterrows():
        monto = float(row["monto"])
        pagador = row["pagador"]
        involucrados = row["involucrados"] if isinstance(row["involucrados"], list) else json.loads(row["involucrados"])

        pagado_por[pagador] += monto
        dividido = monto / len(involucrados)
        for p in involucrados:
            balance_individual[p] += dividido

        total += monto

    st.markdown(f"**Total gastado:** ${total:.2f}")

    for nombre in participantes:
        diferencia = pagado_por[nombre] - balance_individual[nombre]
        if diferencia > 0:
            st.success(f"✅ {nombre} puso ${diferencia:.2f} de más")
        elif diferencia < 0:
            st.warning(f"⚠️ {nombre} debe ${abs(diferencia):.2f}")
        else:
            st.info(f"{nombre} está justo")

# Botón para reiniciar semana
if st.button("🧹 Reiniciar semana"):
    gastos_df = pd.DataFrame(columns=columnas)
    gastos_df.to_csv(archivo, index=False)
    st.success("Todos los gastos fueron borrados.")
