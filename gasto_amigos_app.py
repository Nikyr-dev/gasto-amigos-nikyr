# gasto_amigos_app.py

import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

# Configuración inicial de la página
st.set_page_config(page_title="Gasto Justo", page_icon="💸", layout="centered")

# Fondo amarillo
st.markdown(
    """
    <style>
    body {
        background-color: #FFF8DC;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Imagen de portada
st.image("https://raw.githubusercontent.com/Nikyr-dev/gasto-amigos-nikyr/main/encabezado_gasto_justo.png", use_container_width=True)

# Conexión a Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gspread"], scopes=scope
)

gc = gspread.authorize(credentials)

try:
    sh = gc.open_by_key('1OXuFe8wp0WxrsidTJX75eWQ0TH9oUtZB1nbhenbZMY0')
    worksheet = sh.sheet1
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"❌ Error de conexión con Google Sheets. Verificá tus credenciales y permisos.\n\nDetalles: {e}")
    st.stop()

# Participantes iniciales
participantes = ["Rama", "Nacho", "Marce"]

# Registrar nuevo gasto
st.subheader("Registrar nuevo gasto")

descripcion = st.text_input("Descripción del gasto:")
monto = st.number_input("Monto:", min_value=0.0, step=0.5)
pagador = st.selectbox("¿Quién pagó?", participantes)
involucrados = st.multiselect("¿Quiénes participaron?", participantes, default=participantes)
fecha = st.date_input("Fecha del gasto", pd.Timestamp.now())

if st.button("Registrar Gasto"):
    nuevo_gasto = [str(fecha), descripcion, monto, pagador, ', '.join(involucrados)]
    worksheet.append_row(nuevo_gasto)
    st.success("✅ Gasto registrado correctamente.")
    st.experimental_rerun()

# Historial de gastos
st.subheader("Historial de gastos")

if not df.empty:
    for i, row in df.iterrows():
        st.markdown(f"- {row['fecha']} | **{row['descripcion']}** | ${row['monto']} – pagó *{row['pagador']}* | Participantes: {row['participantes']}")
else:
    st.info("No hay gastos registrados todavía.")

# Análisis de deudas
st.subheader("Saldos por persona")

if not df.empty:
    # Calcular balances
    balances = {nombre: 0 for nombre in participantes}
    
    for i, row in df.iterrows():
        participantes_en_gasto = row['participantes'].split(", ")
        monto_individual = row['monto'] / len(participantes_en_gasto)
        
        for persona in participantes_en_gasto:
            balances[persona] -= monto_individual
        
        balances[row['pagador']] += row['monto']
    
    # Mostrar resultados
    for nombre, saldo in balances.items():
        if saldo > 0:
            st.success(f"{nombre} tiene a favor: ${saldo:.2f}")
        elif saldo < 0:
            st.error(f"{nombre} debe: ${abs(saldo):.2f}")
        else:
            st.info(f"{nombre} está saldado.")

else:
    st.warning("No hay datos suficientes para calcular balances.")
