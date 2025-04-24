import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2 import service_account
from PIL import Image
import os

st.set_page_config(page_title="Gasto Justo - By NIKY'R", layout="centered")

if os.path.exists('encabezado_gasto_justo.png'):
    imagen = Image.open('encabezado_gasto_justo.png')
    st.image(imagen, use_container_width=True)
else:
    st.warning("No se encontró la imagen de encabezado.")

SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SECRETS = {
    "type": "service_account",
    "project_id": st.secrets["project_id"],
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"].replace("\\n", "\n"),
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

if sheet_saldados.row_count < 1 or sheet_saldados.cell(1, 1).value != "Persona":
    sheet_saldados.clear()
    sheet_saldados.append_row(["Persona", "Estado"])

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

def cargar_datos_saldados():
    datos = sheet_saldados.get_all_records()
    return {row['Persona']: str(row['Estado']).upper() == "TRUE" for row in datos if 'Persona' in row and 'Estado' in row}

def actualizar_estado_saldado(persona, estado):
    datos_saldados = sheet_saldados.get_all_records()
    nombres = [row['Persona'] for row in datos_saldados]
    if persona in nombres:
        index = nombres.index(persona)
        sheet_saldados.update_cell(index + 2, 2, "TRUE" if estado else "FALSE")
    else:
        sheet_saldados.append_row([persona, "TRUE" if estado else "FALSE"])

participantes_validos = ["Rama", "Nacho", "Marce"]

# Bloque de debug directo
st.write("🔍 Datos crudos desde Google Sheets:")
st.dataframe(cargar_datos_gastos())

# Cargar gastos en session_state
st.session_state['gastos'] = cargar_datos_gastos().to_dict('records')

st.header("Registrar nuevo gasto")
with st.form(key='nuevo_gasto'):
    descripcion = st.text_input("Descripción")
    monto = st.number_input("Monto", min_value=0.0, format="%.2f")
    pagador = st.selectbox("Pagador", participantes_validos)
    participantes = st.multiselect("Participantes", participantes_validos, default=participantes_validos)
    fecha = st.date_input("Fecha", value=datetime.date.today())
    submit_button = st.form_submit_button(label='Agregar gasto')

if submit_button:
    nueva_fila = [
        fecha.strftime("%d-%b"),
        descripcion,
        monto,
        pagador,
        ", ".join(participantes),
        "FALSE"
    ]
    sheet_gastos.append_row(nueva_fila)
    st.success("Gasto agregado exitosamente")
    st.session_state['gastos'] = cargar_datos_gastos().to_dict('records')
    st.rerun()

st.header("Historial de gastos")
if 'gastos' in st.session_state and st.session_state['gastos']:
    gastos_df = pd.DataFrame(st.session_state['gastos'])
    st.dataframe(gastos_df)