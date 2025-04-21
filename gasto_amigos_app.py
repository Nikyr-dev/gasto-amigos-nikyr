# BLOQUE 1: Importaciones necesarias
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Gasto Justo", page_icon="💸", layout="centered")

# BLOQUE 2: Imagen de encabezado
st.image("https://raw.githubusercontent.com/Nikyr-dev/gasto-amigos-nikyr/main/encabezado_gasto_justo.png", use_container_width=True)

# BLOQUE 3: Cargar datos
archivo = "gastos.csv"
if os.path.exists(archivo):
    df = pd.read_csv(archivo)
else:
    df = pd.DataFrame(columns=["fecha", "detalle", "monto", "quien", "participantes"])

# Convertir columna participantes de string a lista
if not df.empty:
    df["participantes"] = df["participantes"].apply(eval)

# BLOQUE 4: Sección para registrar un nuevo gasto
st.header("Registrar Gasto")
with st.form("nuevo_gasto"):
    fecha = st.date_input("Fecha", value=datetime.today())
    detalle = st.text_input("Detalle del gasto")
    monto = st.number_input("Monto", min_value=0.0, step=100.0)
    quien = st.selectbox("¿Quién pagó?", options=["Rama", "Nacho", "Marce"])
    participantes = st.multiselect("¿Quiénes participaron?", options=["Rama", "Nacho", "Marce"], default=["Rama", "Nacho", "Marce"])
    submitted = st.form_submit_button("Registrar")

    if submitted:
        nuevo = {
            "fecha": fecha.strftime("%Y-%m-%d"),
            "detalle": detalle,
            "monto": monto,
            "quien": quien,
            "participantes": participantes
        }
        df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
        df.to_csv(archivo, index=False)
        st.success("✅ Gasto registrado correctamente")
        st.experimental_rerun()

# BLOQUE 5: Historial de gastos
st.subheader("📜 Historial de Gastos")
df_vista = df.copy()
df_vista["participantes"] = df_vista["participantes"].apply(lambda x: ", ".join(x))
st.dataframe(df_vista)

# BLOQUE 6: Análisis de deudas
st.subheader("📊 Análisis de Deudas")

personas = ["Rama", "Nacho", "Marce"]

# Cuánto puso cada uno
aportado = df.groupby("quien")["monto"].sum().reindex(personas, fill_value=0)

# Cuánto consumió cada uno
deuda_total = {persona: 0 for persona in personas}
for _, row in df.iterrows():
    monto_por_persona = row["monto"] / len(row["participantes"])
    for p in row["participantes"]:
        deuda_total[p] += monto_por_persona

# Saldo final (lo que puso menos lo que gastó)
saldos = {}
for persona in personas:
    saldo = aportado[persona] - deuda_total[persona]
    saldos[persona] = round(saldo, 2)

# Mostrar el resumen general
resumen = pd.DataFrame({
    "Persona": personas,
    "Aportó": [aportado[p] for p in personas],
    "Consumió": [deuda_total[p] for p in personas],
    "Saldo Final": [saldos[p] for p in personas],
    "Estado": ["Debe" if saldos[p] < 0 else "A favor" if saldos[p] > 0 else "Ok" for p in personas]
})
st.dataframe(resumen)

# BLOQUE 7: Deudas cruzadas
st.subheader("🔁 Deudas Cruzadas")

acreedores = {p: s for p, s in saldos.items() if s > 0}
deudores = {p: -s for p, s in saldos.items() if s < 0}

deuda_detalle = []

for deudor, debe in deudores.items():
    for acreedor, a_favor in acreedores.items():
        if debe == 0:
            break
        if a_favor == 0:
            continue
        pago = min(debe, a_favor)
        deuda_detalle.append({
            "Deudor": deudor,
            "Acreedor": acreedor,
            "Monto": round(pago, 2)
        })
        deudores[deudor] -= pago
        acreedores[acreedor] -= pago
        debe -= pago

df_deudas = pd.DataFrame(deuda_detalle)
if df_deudas.empty:
    st.info("✅ No hay deudas pendientes.")
else:
    st.dataframe(df_deudas)
