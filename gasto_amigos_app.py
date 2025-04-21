# BLOQUE 1: Importaciones necesarias
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

st.set_page_config(page_title="Gasto Justo – By NIKY’R", page_icon="💸", layout="centered")

# Fondo amarillo
st.markdown(
    """
    <style>
    body {
        background-color: #FFF7D4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# BLOQUE 2: Conexión con Google Sheets
try:
    credentials = service_account.Credentials.from_service_account_info({
        "type": st.secrets["gspread"]["type"],
        "project_id": st.secrets["gspread"]["project_id"],
        "private_key_id": st.secrets["gspread"]["private_key_id"],
        "private_key": st.secrets["gspread"]["private_key"],
        "client_email": st.secrets["gspread"]["client_email"],
        "client_id": st.secrets["gspread"]["client_id"],
        "auth_uri": st.secrets["gspread"]["auth_uri"],
        "token_uri": st.secrets["gspread"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["gspread"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["gspread"]["client_x509_cert_url"]
    })
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key('1OXuFe8wp0WxrsidTJX75eWQ0TH9oUtZB1nbhenbZMY0')
    worksheet = sh.sheet1
    datos = worksheet.get_all_records()
    gastos_df = pd.DataFrame(datos)
except Exception as e:
    st.error(f"❌ Error de conexión con Google Sheets. Verificá tus credenciales y permisos.\n\nDetalles: {e}")
    gastos_df = pd.DataFrame()

# BLOQUE 3: Mostrar imagen de portada
st.image("https://raw.githubusercontent.com/Nikyr-dev/gasto-amigos-nikyr/main/portada_gasto_justo.png", use_container_width=True)

# BLOQUE 4: Mostrar historial de gastos
st.title("📋 Historial de Gastos")
if not gastos_df.empty:
    st.dataframe(gastos_df)
else:
    st.warning("No hay gastos registrados todavía.")

# BLOQUE 5: Cálculo de resumen y deudas
st.title("💸 Resumen Final")

if not gastos_df.empty:
    participantes = ["Rama", "Nacho", "Marce"]
    gastos_participantes = {p: 0 for p in participantes}

    for _, row in gastos_df.iterrows():
        for participante in participantes:
            if participante in row['participantes']:
                gastos_participantes[participante] += row['monto'] / len(row['participantes'])

    total_gasto = sum(gastos_participantes.values())
    promedio = total_gasto / len(participantes)

    st.subheader(f"**Total gastado:** ${total_gasto:.2f}")
    st.subheader(f"**Cada uno debería haber puesto:** ${promedio:.2f}")

    for nombre in participantes:
        diferencia = gastos_participantes[nombre] - promedio
        if diferencia > 0:
            st.success(f"✅ {nombre} puso ${diferencia:.2f} de más")
        elif diferencia < 0:
            st.warning(f"⚠️ {nombre} debe ${abs(diferencia):.2f}")
        else:
            st.info(f"🎯 {nombre} está justo")
else:
    st.info("Cargá gastos para ver el resumen.")

