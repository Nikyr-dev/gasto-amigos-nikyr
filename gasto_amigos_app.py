import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2 import service_account
from PIL import Image
import os
import ast

st.set_page_config(page_title="Gasto Justo - By NIKY'R", layout="centered")

if os.path.exists('encabezado_gasto_justo.png'):
    imagen = Image.open('encabezado_gasto_justo.png')
    st.image(imagen, use_container_width=True)

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

def cargar_datos_gastos():
    datos = sheet_gastos.get_all_records()
    filas_validas = []
    for row in datos:
        try:
            if isinstance(row.get('participantes'), str) and '[' not in row['participantes']:
                row['participantes'] = [p.strip() for p in row['participantes'].split(',') if p.strip()]
            elif isinstance(row.get('participantes'), str):
                row['participantes'] = ast.literal_eval(row['participantes'])
            filas_validas.append(row)
        except Exception as e:
            st.warning(f"⚠️ Error procesando fila: {row}. Error: {e}")
            continue
    return pd.DataFrame(filas_validas)

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

try:
    df = cargar_datos_gastos()
    columnas_esperadas = ['fecha', 'detalle', 'monto', 'pagador', 'participantes', 'saldado']
    if not df.empty and all(col in df.columns for col in columnas_esperadas):
        st.session_state['gastos'] = df.to_dict('records')
    else:
        st.session_state['gastos'] = []
except:
    st.session_state['gastos'] = []

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

# Nuevo BALANCE y DEUDAS
st.header("Balance y deudas")

def limpiar_nombre(nombre):
    nombre_limpio = nombre.strip()
    return nombre_limpio if nombre_limpio in participantes_validos else None

# Inicializar contadores
total_pagado = {}
total_deberia_pagar = {}

if 'gastos' in st.session_state and st.session_state['gastos']:
    for gasto in st.session_state['gastos']:
        try:
            monto = float(str(gasto['monto']).replace(',', '').strip())
        except ValueError:
            continue

        pagador = limpiar_nombre(gasto['pagador'])
        participantes = [limpiar_nombre(p) for p in gasto['participantes']]
        participantes = [p for p in participantes if p]

        if not pagador or not participantes:
            continue

        total_pagado[pagador] = total_pagado.get(pagador, 0) + monto

        monto_por_persona = monto / len(participantes)
        for participante in participantes:
            total_deberia_pagar[participante] = total_deberia_pagar.get(participante, 0) + monto_por_persona

saldos_finales = {}
for persona in participantes_validos:
    pagado = total_pagado.get(persona, 0)
    deberia = total_deberia_pagar.get(persona, 0)
    saldo = pagado - deberia
    saldos_finales[persona] = saldo

# Mostrar resumen
st.subheader("Resumen de gastos y saldos")
df_balance = pd.DataFrame([
    {"Persona": persona, "Gastó en total": round(total_pagado.get(persona, 0), 2), "Debe pagar": round(total_deberia_pagar.get(persona, 0), 2), "Saldo final": round(saldo, 2), "Situación": ("A favor" if saldo > 0 else "Debe")}
    for persona, saldo in saldos_finales.items()
])
st.dataframe(df_balance)

# Estado de deudas
st.subheader("Estado final de deudas")
saldados_actualizados = cargar_datos_saldados()
for persona, saldo in saldos_finales.items():
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

# Botón de reinicio
if st.button("Reiniciar semana"):
    sheet_gastos.clear()
    sheet_gastos.append_row(["fecha", "detalle", "monto", "pagador", "participantes", "saldado"])
    sheet_saldados.clear()
    sheet_saldados.append_row(["Persona", "Estado"])
    st.session_state['gastos'] = []
    cargar_datos_gastos()
    st.success("✅ Semana reiniciada correctamente.")
    st.rerun()