
import streamlit as st
import pandas as pd
import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Gasto Justo – By NIKY’R")

# Fuente Verdana
st.markdown('''
<style>
html, body, [class*="css"]  {
    font-family: Verdana;
}
</style>
''', unsafe_allow_html=True)

# Título
st.markdown("""
<h1 style='text-align: center; color: #ffc107; font-size: 42px;'>
    💸 Gasto Justo – <span style='color:#FF5252;'>By NIKY’R</span> 🧾
</h1>
""", unsafe_allow_html=True)

participantes = ["Rama", "Nacho", "Marce"]

# Conexión segura a Google Sheets usando secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credenciales = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gspread"], scope)
cliente = gspread.authorize(credenciales)
hoja = cliente.open("Gasto_Justo_nikyr").sheet1

# Leer los datos
datos = hoja.get_all_records()
df = pd.DataFrame(datos)

# Formulario
st.subheader("Registrar nuevo gasto")
descripcion = st.text_input("¿Qué se compró?")
monto = st.number_input("¿Cuánto costó?", min_value=0.0, step=0.5)
pagador = st.selectbox("¿Quién pagó?", participantes)
involucrados = st.multiselect("¿Quiénes participaron?", participantes, default=participantes)
fecha = st.date_input("Fecha del gasto", datetime.date.today())

if st.button("Agregar gasto"):
    nueva_fila = [fecha.strftime("%d-%b"), descripcion, monto, pagador, json.dumps(involucrados)]
    hoja.append_row(nueva_fila)
    st.success("✅ Gasto guardado correctamente.")

# Historial
st.subheader("Historial de gastos")
if not df.empty:
    for _, row in df.iterrows():
        try:
            lista = json.loads(row["participantes"])
            participantes_str = ", ".join(lista)
        except:
            participantes_str = row["participantes"]
        st.write(f"{row['fecha']} | {row['descripcion']} | ${row['monto']} – pagó {row['pagador']} | participaron: {participantes_str}")
else:
    st.info("No hay gastos registrados aún.")

# Balance
st.subheader("Resumen de la semana")
if not df.empty:
    saldos = {nombre: 0 for nombre in participantes}
    for _, row in df.iterrows():
        try:
            lista = json.loads(row["participantes"])
        except:
            lista = participantes
        monto = float(row["monto"])
        division = monto / len(lista)
        for persona in lista:
            saldos[persona] -= division
        saldos[row["pagador"]] += monto

    total = df["monto"].sum()
    st.markdown(f"**Total gastado:** ${total:.2f}")

    for nombre, saldo in saldos.items():
        if saldo > 0:
            st.success(f"✅ {nombre} puso ${saldo:.2f} de más")
        elif saldo < 0:
            st.warning(f"⚠️ {nombre} debe ${abs(saldo):.2f}")
        else:
            st.info(f"{nombre} está justo")
