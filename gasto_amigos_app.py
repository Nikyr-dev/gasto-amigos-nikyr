import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2 import service_account
from PIL import Image
import os
import ast

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
    for row in datos:
        try:
            if isinstance(row['participantes'], str):
                row['participantes'] = ast.literal_eval(row['participantes'])
        except:
            row['participantes'] = []
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

participantes_validos = ["Rama", "Nacho", "Marce"]

def limpiar_nombre(nombre):
    nombre_limpio = nombre.strip().replace('[', '').replace(']', '').replace('"', '').replace("'", '').replace(',', '')
    if nombre_limpio in participantes_validos:
        return nombre_limpio
    else:
        return None

total_gastado = 0
gastos_por_persona = {}
balance_individual = {}

for gasto in st.session_state.gastos:
    monto = gasto['monto']
    participantes = [limpiar_nombre(p) for p in gasto['participantes']]
    participantes = [p for p in participantes if p is not None]
    pagador = limpiar_nombre(gasto['pagador'])

    if pagador is None or len(participantes) == 0:
        continue

    total_gastado += monto

    if pagador not in gastos_por_persona:
        gastos_por_persona[pagador] = 0
    gastos_por_persona[pagador] += monto

    monto_por_participante = monto / len(participantes)

    for participante in participantes:
        if participante not in balance_individual:
            balance_individual[participante] = 0
        balance_individual[participante] -= monto_por_participante

    if pagador not in balance_individual:
        balance_individual[pagador] = 0
    balance_individual[pagador] += monto

# Mostrar resumen de saldo
st.subheader("Resumen de gastos y saldos:")

datos_balance = []
for persona in sorted(set(list(gastos_por_persona.keys()) + list(balance_individual.keys()))):
    gasto_total = gastos_por_persona.get(persona, 0)
    saldo = balance_individual.get(persona, 0)
    datos_balance.append({
        "Persona": persona,
        "Gastó en total": round(gasto_total, 2),
        "Saldo final": round(saldo, 2),
        "Situación": "Debe" if saldo < 0 else "A favor"
    })

df_balance = pd.DataFrame(datos_balance)
st.dataframe(df_balance)

# Mostrar resumen en texto simple
st.subheader("Estado final de deudas:")

for persona, saldo in balance_individual.items():
    if saldo < 0:
        st.write(f"👉 {persona} debe ${-saldo:.2f}")
    elif saldo > 0:
        st.write(f"✅ {persona} tiene ${saldo:.2f} a favor")
