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

# Inicializar sesión para que los datos no se pierdan al actualizar
if "gastos_df" not in st.session_state:
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
    st.session_state["gastos_df"] = gastos_df

gastos_df = st.session_state["gastos_df"]

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
        st.session_state["gastos_df"] = pd.concat([st.session_state["gastos_df"], nuevo], ignore_index=True)
        st.session_state["gastos_df"].to_csv(archivo, index=False)
        st.success("✅ Gasto guardado correctamente.")

# Mostrar historial