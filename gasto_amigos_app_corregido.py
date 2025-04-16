
import streamlit as st
import pandas as pd
import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image
import os

# Configuración de conexión con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credenciales = st.secrets["gspread"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credenciales, scope)
cliente = gspread.authorize(credentials)
hoja = cliente.open_by_key("1OXuFe8wp0WxrsidTJX75eWQ0TH9oUtZB1nbhenbZMY0").sheet1

# Cargar datos desde Google Sheets
data = hoja.get_all_records()
gastos_df = pd.DataFrame(data)

# Mostrar encabezado con imagen (logo estilo Simpsons)
st.image("simpsons_gasto_justo.png", use_container_width=True)

# Formulario para registrar nuevo gasto
st.subheader("Registrar nuevo gasto")
participantes = ["Rama", "Nacho", "Marce"]
descripcion = st.text_input("¿Qué se compró?")
monto = st.number_input("¿Cuánto costó?", min_value=0.0, step=0.5)
pagadores = st.multiselect("¿Quién pagó?", participantes)
involucrados = st.multiselect("¿Quiénes participaron?", participantes, default=participantes)
fecha = st.date_input("Fecha del gasto", datetime.date.today())

if st.button("Agregar gasto"):
    nuevo = {
        "fecha": fecha.strftime("%d-%b"),
        "descripcion": descripcion,
        "monto": monto,
        "pagador": json.dumps(pagadores),
        "participantes": json.dumps(involucrados)
    }
    hoja.append_row(list(nuevo.values()))
    st.success("✅ Gasto guardado correctamente.")

# Mostrar historial
st.subheader("Historial de gastos")
if not gastos_df.empty:
    for _, row in gastos_df.iterrows():
    try: pagadores = json.loads(row["pagador"]) if isinstance(pagadores, str): pagadores = [pagadores]
try:
    pagadores = json.loads(row["pagador"])
    if isinstance(pagadores, str):
        pagadores = [pagadores]
except:
    pagadores = [row["pagador"]]
pagado_por = ', '.join(pagadores)
        st.markdown(f"- {row['fecha']} | **{row['descripcion']}** | ${row['monto']} – pagó *{pagado_por}*")
else:
    st.info("No hay gastos registrados aún.")

# Cálculo de balances
st.subheader("Resumen de la semana")
if not gastos_df.empty:
    total = gastos_df["monto"].sum()
    st.markdown(f"**Total gastado:** ${total:.2f}")
    
    saldos = {nombre: 0 for nombre in participantes}
    for _, row in gastos_df.iterrows():
        monto = float(row["monto"])
        pagadores = json.loads(row["pagador"]) if isinstance(row["pagador"], str) else [row["pagador"]]
        participantes_gasto = json.loads(row["participantes"]) if isinstance(row["participantes"], str) else [row["participantes"]]
        
        monto_por_persona = monto / len(participantes_gasto)
        for persona in participantes_gasto:
            saldos[persona] -= monto_por_persona
        monto_por_pagador = monto / len(pagadores)
        for pagador in pagadores:
            saldos[pagador] += monto_por_pagador

    for persona, saldo in saldos.items():
        if saldo > 0:
            st.success(f"{persona} tiene saldo a favor de ${saldo:.2f}")
        elif saldo < 0:
            st.warning(f"{persona} debe ${abs(saldo):.2f}")
        else:
            st.info(f"{persona} está justo")

# Botón para reiniciar semana (solo visual, no borra en la hoja)
if st.button("🧹 Reiniciar semana"):
    st.warning("Para reiniciar realmente, borra los datos manualmente en Google Sheets.")
