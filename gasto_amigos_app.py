import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2 import service_account
from PIL import Image

# Configuración de página
st.set_page_config(page_title="Gasto Justo - By NIKY'R", layout="centered")

# Cargar imagen de encabezado
imagen = Image.open('encabezado_gasto_justo.png')
st.image(imagen, use_column_width=True)

# Conexión a Google Sheets
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
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": st.secrets["client_x509_cert_url"]
}
credentials = service_account.Credentials.from_service_account_info(SECRETS, scopes=SCOPE)
client = gspread.authorize(credentials)
sheet = client.open_by_key(st.secrets["sheet_id"]).sheet1

# Cargar datos existentes
@st.cache_data
def cargar_datos():
    datos = sheet.get_all_records()
    return pd.DataFrame(datos)

df = cargar_datos()

if 'gastos' not in st.session_state:
    st.session_state.gastos = df.to_dict('records')

# Formulario para registrar nuevo gasto
st.header("Registrar nuevo gasto")
with st.form(key='nuevo_gasto'):
    descripcion = st.text_input("Descripción")
    monto = st.number_input("Monto", min_value=0.0, format="%.2f")
    pagador = st.text_input("Pagador")
    participantes = st.text_input("Participantes (separados por coma)")
    fecha = st.date_input("Fecha", value=datetime.date.today())
    submit_button = st.form_submit_button(label='Agregar gasto')

if submit_button:
    participantes_lista = [p.strip() for p in participantes.split(',')]
    nuevo_gasto = {
        'descripcion': descripcion,
        'monto': monto,
        'pagador': pagador,
        'participantes': participantes_lista,
        'fecha': fecha.strftime("%d-%b")
    }
    st.session_state.gastos.append(nuevo_gasto)

    # Actualizar Google Sheets
    nueva_fila = [
        descripcion,
        monto,
        pagador,
        ", ".join(participantes_lista),
        fecha.strftime("%d-%b")
    ]
    sheet.append_row(nueva_fila)
    st.success("Gasto agregado exitosamente")

# Mostrar historial de gastos
st.header("Historial de gastos")
if st.session_state.gastos:
    gastos_df = pd.DataFrame(st.session_state.gastos)
    st.dataframe(gastos_df)

# Calcular balances
st.header("Balance")

total_gastado = 0
balance_individual = {}
total_por_persona = {}

for gasto in st.session_state.gastos:
    monto = gasto['monto']
    participantes = gasto['participantes']
    pagador = gasto['pagador']

    # Inicializar el pagador en total_por_persona
    if pagador not in total_por_persona:
        total_por_persona[pagador] = 0
    total_por_persona[pagador] += monto

    total_gastado += monto

    monto_por_participante = monto / len(participantes)

    for participante in participantes:
        if participante not in balance_individual:
            balance_individual[participante] = 0
        balance_individual[participante] -= monto_por_participante

    if pagador not in balance_individual:
        balance_individual[pagador] = 0
    balance_individual[pagador] += monto

st.subheader("Total gastado hasta ahora:")
st.write(f"${total_gastado:.2f}")

st.subheader("Saldos individuales:")
for persona, saldo in balance_individual.items():
    st.write(f"{persona}: ${saldo:.2f}")
