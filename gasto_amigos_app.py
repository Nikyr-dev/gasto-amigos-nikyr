
import streamlit as st
import pandas as pd
import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Conexión a Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credenciales = st.secrets["gspread"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credenciales, scope)
cliente = gspread.authorize(credentials)
hoja = cliente.open_by_key("1OXuFe8wp0WxrsidTJX75eWQ0TH9oUtZB1nbhenbZMY0").sheet1

# Cargar datos de la hoja
datos = hoja.get_all_records()
df = pd.DataFrame(datos)

participantes = ["Rama", "Nacho", "Marce"]

# Imagen de encabezado
st.image("encabezado_gasto_justo.png", use_container_width=True)

# Formulario para registrar nuevo gasto
st.subheader("Registrar nuevo gasto")
descripcion = st.text_input("¿Qué se compró?")
monto = st.number_input("¿Cuánto costó?", min_value=0.0, step=0.5)
pagadores = st.multiselect("¿Quién pagó?", participantes)
involucrados = st.multiselect("¿Quiénes participaron?", participantes, default=participantes)
fecha = st.date_input("Fecha del gasto", datetime.date.today())

if st.button("Agregar gasto") and pagadores and involucrados:
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
if not df.empty:
    for _, row in df.iterrows():
        try:
            pagadores = json.loads(row["pagador"])
            if isinstance(pagadores, str):
                pagadores = [pagadores]
        except:
            pagadores = [row["pagador"]]
        try:
            personas = json.loads(row["participantes"]) if row["participantes"] else []
        except:
            personas = []
        pagado_por = ', '.join(pagadores)
        st.markdown(f"- {row['fecha']} | **{row['descripcion']}** | ${row['monto']} – pagó *{pagado_por}*")

# Cálculo de balances
st.subheader("Resumen de la semana")
if not df.empty:
    df["monto"] = pd.to_numeric(df["monto"], errors="coerce")
    balances = {p: 0 for p in participantes}
    total = 0

    for _, row in df.iterrows():
        monto = float(row["monto"])
        try:
            pagadores = json.loads(row["pagador"])
            if isinstance(pagadores, str):
                pagadores = [pagadores]
        except:
            pagadores = [row["pagador"]]

        try:
            personas = json.loads(row["participantes"]) if row["participantes"] else []
        except:
            personas = []

        if not personas:
            continue
        monto_individual = monto / len(personas)
        for persona in personas:
            balances[persona] -= monto_individual
        for p in pagadores:
            balances[p] += monto / len(pagadores)
        total += monto

    st.markdown(f"**Total gastado:** ${total:.2f}")
    for persona, balance in balances.items():
        if balance > 0:
            st.success(f"{persona} tiene saldo a favor de ${balance:.2f}")
        elif balance < 0:
            st.warning(f"{persona} debe ${abs(balance):.2f}")
        else:
            st.info(f"{persona} está justo")

# Aviso para reiniciar (manual)
if st.button("🧹 Reiniciar semana"):
    st.warning("Para reiniciar realmente, borra los datos manualmente en Google Sheets.")
