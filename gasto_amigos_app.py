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

# Asegurar encabezados
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

# Lista fija de participantes
participantes_validos = ["Rama", "Nacho", "Marce"]

# Formulario
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
    st.rerun()

# Cargar gastos actualizados
st.session_state.gastos = cargar_datos_gastos().to_dict('records')

# Mostrar historial
st.header("Historial de gastos")
if st.session_state.gastos:
    gastos_df = pd.DataFrame(st.session_state.gastos)
    st.dataframe(gastos_df)

# Balance
st.header("Balance")

def limpiar_nombre(nombre):
    nombre_limpio = nombre.strip()
    if nombre_limpio in participantes_validos:
        return nombre_limpio
    return None

total_gastado = 0
gastos_por_persona = {}
balance_individual = {}

for gasto in st.session_state.gastos:
    monto = gasto['monto']
    participantes = [limpiar_nombre(p) for p in gasto['participantes']]
    participantes = [p for p in participantes if p]
    pagador = limpiar_nombre(gasto['pagador'])

    if pagador is None or len(participantes) == 0:
        continue

    total_gastado += monto
    gastos_por_persona[pagador] = gastos_por_persona.get(pagador, 0) + monto

    monto_por_persona = monto / len(participantes)
    for p in participantes:
        balance_individual[p] = balance_individual.get(p, 0) - monto_por_persona
    balance_individual[pagador] = balance_individual.get(pagador, 0) + monto

# Mostrar balances
st.subheader("Resumen de gastos y saldos")
df_balance = pd.DataFrame([
    {
        "Persona": persona,
        "Gastó en total": round(gastos_por_persona.get(persona, 0), 2),
        "Saldo final": round(balance, 2),
        "Situación": "Debe" if balance < 0 else "A favor"
    }
    for persona, balance in balance_individual.items()
])
st.dataframe(df_balance)

# Estado de deudas
st.subheader("Estado final de deudas")
saldados_actualizados = cargar_datos_saldados()

for persona, saldo in balance_individual.items():
    if saldo < 0:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"👉 {persona} debe ${-saldo:.2f}")
        with col2:
            estado_actual = saldados_actualizados.get(persona, False)
            marcado = st.checkbox(f"Saldado {persona}", value=estado_actual, key=f"saldado_{persona}")
            if marcado != estado_actual:
                actualizar_estado_saldado(persona, marcado)
            if marcado:
                st.success(f"✅ {persona} saldó su deuda.")
    elif saldo > 0:
        st.write(f"✅ {persona} tiene ${saldo:.2f} a favor")

# Reiniciar semana
st.subheader("¿Empezar semana nueva?")
if st.button("Reiniciar semana"):
    sheet_gastos.clear()
    sheet_gastos.append_row(["fecha", "detalle", "monto", "pagador", "participantes", "saldado"])
    sheet_saldados.clear()
    sheet_saldados.append_row(["Persona", "Estado"])
    st.session_state.gastos = []
    st.success("✅ Semana reiniciada correctamente.")
    st.rerun()
