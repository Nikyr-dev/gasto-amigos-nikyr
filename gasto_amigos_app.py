
import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2 import service_account
from PIL import Image
import os

# Configuración de página
st.set_page_config(page_title="Gasto Justo - By NIKY'R", layout="centered")

# Cargar imagen de encabezado
if os.path.exists('encabezado_gasto_justo.png'):
    imagen = Image.open('encabezado_gasto_justo.png')
    st.image(imagen, use_container_width=True)
else:
    st.warning("No se encontró la imagen de encabezado.")

# Conexión a Google Sheets
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SECRETS = {
    "type": "service_account",
    "project_id": st.secrets["project_id"],
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"].replace("\n", "\n"),
    "client_email": st.secrets["client_email"],
    "client_id": st.secrets["client_id"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/v1/certs",
    "client_x509_cert_url": st.secrets["client_x509_cert_url"]
}
credentials = service_account.Credentials.from_service_account_info(SECRETS, scopes=SCOPE)
client = gspread.authorize(credentials)
sheet_gastos = client.open_by_key(st.secrets["sheet_id"]).worksheet("Hoja 1")
sheet_saldados = client.open_by_key(st.secrets["sheet_id"]).worksheet("saldados")

# Asegurar que la hoja 'saldados' tiene encabezado correcto
if sheet_saldados.row_count < 1 or sheet_saldados.cell(1, 1).value != "Persona":
    sheet_saldados.clear()
    sheet_saldados.append_row(["Persona", "Estado"])

# Cargar datos existentes
@st.cache_data
def cargar_datos_gastos():
    datos = sheet_gastos.get_all_records()
    for row in datos:
        try:
            if isinstance(row['participantes'], str):
                row['participantes'] = [p.strip() for p in row['participantes'].split(',') if p.strip()]
        except:
            row['participantes'] = []
    return pd.DataFrame(datos)

# Reiniciar semana
st.subheader("¿Empezar semana nueva?")
if st.button("Reiniciar semana"):
    sheet_gastos.clear()
    sheet_gastos.append_row(["fecha", "detalle", "monto", "pagador", "participantes", "saldado"])
    sheet_saldados.clear()
    sheet_saldados.append_row(["Persona", "Estado"])
    st.session_state.gastos = []
    cargar_datos_gastos.clear()  # limpia el cache
    st.success("✅ Semana reiniciada correctamente.")
    st.rerun()
