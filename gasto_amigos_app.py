
import streamlit as st
import pandas as pd
import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Conexión con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credenciales_dict = st.secrets["gspread"]
credenciales = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_dict, scope)
cliente = gspread.authorize(credenciales)
hoja = cliente.open_by_key("1OXuFe8wp0WxrsidTJX75eWQ0TH9oUtZB1nbhenbZMY0").sheet1  # Reemplazá por el ID real de tu hoja

# Cargar datos de la hoja
datos = hoja.get_all_records()
df = pd.DataFrame(datos)

# Participantes predefinidos
participantes = ["Rama", "Nacho", "Marce"]

# Título con imagen personalizada
st.markdown(
    """
    <div style='text-align: center;'>
        <img src='https://raw.githubusercontent.com/Nikyr-dev/gasto-amigos-nikyr/main/logo_amigo_circular.png' width='100'><br>
        <h1 style='color: #ffc107; font-size: 42px; font-family: Verdana;'>💸 Gasto Justo</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.subheader("Registrar nuevo gasto")
descripcion = st.text_input("¿Qué se compró?")
monto = st.number_input("¿Cuánto costó?", min_value=0.0, step=0.5)
pagadores = st.multiselect("¿Quién(es) pagaron?", participantes, default=[])
involucrados = st.multiselect("¿Quiénes participaron?", participantes, default=participantes)
fecha = st.date_input("Fecha del gasto", datetime.date.today())

if st.button("Agregar gasto"):
    nuevo_gasto = [str(fecha), descripcion, monto, json.dumps(pagadores), json.dumps(involucrados)]
    hoja.append_row(nuevo_gasto)
    st.success("✅ Gasto guardado correctamente.")

st.subheader("Historial de gastos")
if not df.empty:
    for i, row in df.iterrows():
        try:
            personas = json.loads(row["participantes"])
        except:
            personas = []
        st.markdown(
            f"- {row['fecha']} | **{row['descripcion']}** | ${row['monto']} – "
            f"pagó *{row['pagador']}* | Participaron: {', '.join(personas)}"
        )
else:
    st.info("No hay gastos registrados aún.")

st.subheader("Resumen de la semana")
if not df.empty:
    df["monto"] = pd.to_numeric(df["monto"], errors="coerce")
    df["participantes"] = df["participantes"].apply(lambda x: json.loads(x) if isinstance(x, str) else [])
    balances = {p: 0 for p in participantes}
    total = 0

    for _, row in df.iterrows():
        monto = row["monto"]
        personas = row["participantes"]
        if not personas:
            continue
        monto_individual = monto / len(personas)
        for persona in personas:
            balances[persona] -= monto_individual
        for p in pagadores: balances[p] += monto / len(pagadores)

        total += monto

    st.markdown(f"**Total gastado:** ${total:.2f}")
    for persona, balance in balances.items():
        if balance > 0:
            st.success(f"✅ {persona} puso ${balance:.2f} de más")
        elif balance < 0:
            st.warning(f"⚠️ {persona} debe ${abs(balance):.2f}")
        else:
            st.info(f"{persona} está justo")

if st.button("🧹 Reiniciar semana"):
    hoja.clear()
    hoja.append_row(["fecha", "descripcion", "monto", "pagador", "participantes"])
    st.success("Todos los gastos fueron borrados.")
